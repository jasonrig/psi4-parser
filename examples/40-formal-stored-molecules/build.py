"""Reuse one molecular upload across complete, independently checked requests."""

import argparse
import json
import sys
from pathlib import Path

from psi4_parser.builder import ElectronicState, Molecule, molecule
from psi4_parser.formal import (
    CalculationGoal,
    Model,
    MoleculeBinding,
    PlanningWorkspace,
    RequestTemplate,
    ScientificRequest,
    Setting,
    StoredMolecule,
)
from psi4_parser.formal.interface_models import ProposalSummary, RecordReference


class _Arguments:
    destination: Path


def _geometry() -> Molecule:
    # A fixed illustrative water array; no geometry or protocol recommendation.
    rows = tuple(
        row
        for index in range(6)
        for row in (
            f"O {3.5 * index} 0.0 0.0",
            f"H {3.5 * index + 0.758} 0.0 0.504",
            f"H {3.5 * index - 0.758} 0.0 0.504",
        )
    )
    parsed = Molecule.from_xyz(
        f"{len(rows)}\nIllustrative six-water array\n" + "\n".join(rows) + "\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    return Molecule(
        atoms=parsed.atoms,
        state=parsed.state,
        symmetry="c1",
        fixed_com=True,
        fixed_orientation=True,
    )


def _goal(method: str, basis: str) -> CalculationGoal:
    settings: tuple[Setting, ...] = (Setting(name="scf_type", value="PK"),)
    if method == "mp2":
        settings = (
            *settings,
            Setting(name="mp2_type", value="CONV"),
            Setting(name="qc_module", value="OCC"),
        )
    return CalculationGoal(
        id="energy",
        driver="energy",
        geometry="waters",
        models=(Model(method=method, basis=basis, reference="rhf", settings=settings),),
    )


def _assemble(
    workspace: PlanningWorkspace,
    geometry: Molecule,
    saved: RecordReference,
    destination: Path,
) -> tuple[list[RecordReference], list[ProposalSummary], int, int]:
    requests: list[RecordReference] = []
    proposals: list[ProposalSummary] = []
    template_bytes = 0
    inline_bytes = 0
    for method, basis in (
        ("hf", "sto-3g"),
        ("hf", "cc-pvdz"),
        ("mp2", "sto-3g"),
        ("mp2", "cc-pvdz"),
    ):
        name = f"{method}-{basis}"
        goal = _goal(method, basis)
        template = RequestTemplate(
            molecules=(MoleculeBinding(name="waters", molecule=saved.handle),),
            goals=(goal,),
        )
        template_bytes += len(template.model_dump_json().encode())
        path = destination / f"{name}-template.json"
        path.write_text(template.model_dump_json(indent=2) + "\n", encoding="utf-8")
        reference = workspace.import_file("request_template", path)
        request = workspace.materialize_request(reference.handle)
        direct = ScientificRequest(
            molecules=(molecule("waters", geometry),), goals=(goal,)
        )
        inline_bytes += len(direct.model_dump_json().encode())
        checked = ScientificRequest.model_validate_json(Path(request.path).read_bytes())
        if checked != direct:
            raise RuntimeError(
                "Assembly changed the independent molecular input or goals"
            )
        proposed = workspace.propose(request.handle)
        (destination / f"{name}-proposal.json").write_text(
            proposed.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        if proposed.status != "constructed":
            raise RuntimeError(f"Inspect the failed proposal: {proposed.proposal.path}")
        requests.append(request)
        proposals.append(proposed)
    return requests, proposals, template_bytes, inline_bytes


def main() -> None:
    """Save reusable inputs, four complete requests, size measures, and one bundle.

    Raises:
        RuntimeError: Assembly changes intent, planning rejects work, or export fails.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args(namespace=_Arguments())
    args.destination.mkdir()
    workspace = PlanningWorkspace(args.destination / "workspace")
    geometry = _geometry()
    molecular_record = StoredMolecule(geometry=geometry)
    (args.destination / "molecule.json").write_text(
        molecular_record.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    saved = workspace.save_molecule(geometry)
    requests, proposals, template_bytes, inline_bytes = _assemble(
        workspace, geometry, saved, args.destination
    )
    last = proposals[-1]
    if last.plan is None:
        raise RuntimeError("The final proposal has no accepted plan")
    exported = workspace.export(
        last.plan.handle, requests[-1].handle, None, args.destination / "bundle"
    )
    (args.destination / "export-summary.json").write_text(
        exported.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    if exported.status != "exported":
        raise RuntimeError("Inspect the rejected export summary")
    upload_bytes = len(molecular_record.model_dump_json().encode())
    measures = {
        "requests": len(requests),
        "molecule_uploads": 1,
        "molecular_input_upload_bytes": upload_bytes,
        "request_template_upload_bytes": template_bytes,
        "handle_workflow_upload_bytes": upload_bytes + template_bytes,
        "equivalent_inline_request_upload_bytes": inline_bytes,
        "upload_bytes_saved": inline_bytes - upload_bytes - template_bytes,
        "proposals_constructed": sum(
            item.status == "constructed" for item in proposals
        ),
        "assembled_requests_equal_independent_inputs": True,
        "complete_request_bytes": [reference.bytes for reference in requests],
        "summary_response_bytes": [
            len(item.model_dump_json().encode()) for item in proposals
        ],
        "equivalent_compact_tool_calls": {
            "formal_load_molecule": 1,
            "formal_load_template": len(requests),
            "formal_request": len(requests),
            "formal_propose": len(requests),
            "formal_export": 1,
        },
        "measurement": "UTF-8 JSON bytes and construction calls; not model tokens, "
        "agent success rates, calculation runtime, or research accuracy",
    }
    (args.destination / "measurements.json").write_text(
        json.dumps(measures, indent=2) + "\n", encoding="utf-8"
    )
    sys.stdout.write(f"Stored-molecule planning artifacts: {args.destination}\n")


if __name__ == "__main__":
    main()
