"""Construct explicit SAPT decompositions and a counterpoise comparison."""

import argparse
import json
import sys
from pathlib import Path

from pydantic import JsonValue, TypeAdapter

from psi4_parser.builder import ElectronicState, Molecule, assemble_fragments, molecule
from psi4_parser.formal import (
    AuxiliaryBasis,
    Calculation,
    CalculationGoal,
    CapabilityCatalog,
    EnergyFormula,
    EnergyTerm,
    ExpressionGoal,
    FragmentStudy,
    GoalTerm,
    Model,
    ProductGoal,
    QuantityType,
    SAPTAnalysis,
    ScientificRequest,
    Setting,
    export_bundle,
    fragment_expansion,
    load_catalog,
    propose,
)
from psi4_parser.formal.science import ProductName

_JSON = TypeAdapter(JsonValue)
_COMPONENTS: tuple[ProductName, ...] = (
    "sapt_electrostatics",
    "sapt_exchange",
    "sapt_induction",
    "sapt_dispersion",
)
_PRODUCTS: tuple[ProductName, ...] = (*_COMPONENTS, "sapt_total_energy")


class _Arguments:
    destination: Path
    capabilities: Path | None


def _request(
    *, wrong_partition: bool = False, wrong_sum: bool = False
) -> ScientificRequest:
    state = ElectronicState(charge=0, multiplicity=1)
    a = Molecule.from_xyz("2\nH2\nH 0 0 0\nH 0 0 .8\n", state=state)
    b = Molecule.from_xyz("2\nH2\nH 0 0 3\nH 0 0 3.8\n", state=state)
    assembled = assemble_fragments(("a", a), ("b", b), state=state)
    geometry = Molecule(
        atoms=assembled.atoms,
        fragments=assembled.fragments,
        state=state,
        fixed_com=True,
        fixed_orientation=True,
        symmetry="c1",
    )
    sapt_model = Model(
        method="sapt0",
        basis="cc-pvdz",
        reference="rhf",
        settings=(Setting(name="scf_type", value="DF"),),
        auxiliary_bases=(
            AuxiliaryBasis(role="df_basis_sapt", basis="cc-pvdz-ri"),
            AuxiliaryBasis(role="df_basis_elst", basis="cc-pvdz-jkfit"),
            AuxiliaryBasis(role="df_basis_scf", basis="cc-pvdz-jkfit"),
        ),
    )
    hf = Model(
        method="hf",
        basis="cc-pvdz",
        reference="rhf",
        settings=(Setting(name="scf_type", value="PK"),),
    )
    cp = fragment_expansion(
        FragmentStudy(
            id="cp", geometry="complex", fragments=geometry.fragments, models=(hf,)
        )
    )
    return ScientificRequest(
        molecules=(molecule("complex", geometry),),
        goals=(
            CalculationGoal(
                id="sapt_dimer",
                driver="energy",
                geometry="complex",
                models=(sapt_model,),
                sapt=SAPTAnalysis(
                    fragments=("b", "a") if wrong_partition else ("a", "b")
                ),
            ),
            *(
                ProductGoal(id=name, calculation="sapt_dimer", name=name)
                for name in _PRODUCTS
            ),
            ExpressionGoal(
                id="partition",
                terms=tuple(
                    GoalTerm(
                        goal=name,
                        coefficient=2 if wrong_sum and name == "sapt_dispersion" else 1,
                    )
                    for name in _COMPONENTS
                ),
                quantity=QuantityType(meaning="interaction_energy", unit="hartree"),
            ),
            CalculationGoal(
                id="sapt_monomer",
                driver="energy",
                geometry="complex",
                models=(sapt_model,),
                sapt=SAPTAnalysis(fragments=("a", "b"), basis="monomer"),
            ),
            *cp.goals,
            ExpressionGoal(
                id="basis_comparison",
                terms=(
                    GoalTerm(goal="sapt_monomer", coefficient=1),
                    GoalTerm(goal="sapt_dimer", coefficient=-1),
                ),
                quantity=QuantityType(meaning="energy_difference", unit="hartree"),
            ),
            ExpressionGoal(
                id="method_comparison",
                terms=(
                    GoalTerm(goal="sapt_dimer", coefficient=1),
                    GoalTerm(goal=cp.target, coefficient=-1),
                ),
                quantity=QuantityType(meaning="energy_difference", unit="hartree"),
            ),
        ),
        relations=(
            *cp.relations,
            EnergyFormula(
                result="sapt_dimer",
                terms=tuple(
                    EnergyTerm(result=name, coefficient=1) for name in _COMPONENTS
                ),
            ),
        ),
    )


def main() -> None:
    """Save input-only SAPT/CP plans and declarative component handoffs.

    Raises:
        SystemExit: Supplied evidence cannot establish the accepted construction.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--capabilities", type=Path, default=None)
    args = parser.parse_args(namespace=_Arguments())
    catalog = (
        CapabilityCatalog.model_validate_json(args.capabilities.read_bytes())
        if args.capabilities
        else load_catalog("psi4")
    )
    request = _request()
    proposal = propose(request, catalog)
    args.destination.mkdir()
    (args.destination / "proposal.json").write_text(
        proposal.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    if proposal.plan is None:
        raise SystemExit(f"Planning returned {proposal.status}; inspect proposal.json")
    exported = export_bundle(
        proposal.plan, request, catalog, args.destination / "bundle"
    )
    rejected_status: dict[str, JsonValue] = {}
    for name, damaged in (
        ("wrong-partition", _request(wrong_partition=True)),
        ("wrong-sum", _request(wrong_sum=True)),
    ):
        rejected = propose(damaged, catalog)
        (args.destination / f"{name}-request.json").write_text(
            damaged.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        (args.destination / f"{name}-proposal.json").write_text(
            rejected.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        rejected_status[name] = rejected.status
        if rejected.status != "no_candidate":
            raise SystemExit(f"Expected {name} to be rejected: {rejected.status}")
    summary: dict[str, JsonValue] = {
        "status": proposal.status,
        "goals": len(request.goals),
        "top_level_calls": sum(
            isinstance(step, Calculation) for step in proposal.plan.steps
        ),
        "transient_native_variables": [
            _JSON.validate_json(binding.model_dump_json())
            for binding in exported.manifest.native_variables
        ],
        "native_product_files": len(exported.manifest.native_outputs),
        "namespace_policy": exported.manifest.namespace_policy,
        "option_policy": exported.manifest.option_policy,
        "backend_version": exported.manifest.backend_version,
        "rejected": rejected_status,
        "manifest_digest": exported.manifest_digest,
    }
    (args.destination / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    sys.stdout.write(f"Construction artifacts: {args.destination}\n")


if __name__ == "__main__":
    main()
