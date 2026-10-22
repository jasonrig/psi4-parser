"""Check explicit product provenance and thermal conditions before construction."""

import os
import subprocess
from pathlib import Path

import pytest

from psi4_parser.builder import ElectronicState, Molecule, molecule
from psi4_parser.formal import (
    Calculation,
    CalculationGoal,
    CapabilityCatalog,
    CapabilityQuery,
    Combination,
    EnergyFormula,
    EnergyTerm,
    ExpressionGoal,
    GoalTerm,
    MethodCapability,
    Model,
    Plan,
    PlanningWorkspace,
    Product,
    ProductCapability,
    ProductGoal,
    QuantityType,
    Rational,
    SameModel,
    ScientificRequest,
    StudyCase,
    ThermalConditions,
    VibrationalAnalysis,
    export_bundle,
    finite_study,
    propose,
    render,
    verify,
)
from psi4_parser.formal.products import product_quantity
from psi4_parser.formal.science import ProductName


def _analysis(temperature: float = 298.15) -> VibrationalAnalysis:
    return VibrationalAnalysis(
        conditions=ThermalConditions(
            temperature_kelvin=temperature, pressure_pascal=101325.0
        ),
        rotational_symmetry_number=2,
    )


def _geometry() -> Molecule:
    return Molecule.from_xyz(
        "2\nH2\nH 0 0 0\nH 0 0 .8\n", state=ElectronicState(charge=0, multiplicity=1)
    )


def _model() -> Model:
    return Model(method="scf", basis="sto-3g", reference="rhf")


def _profile(base: CapabilityCatalog, *, products: bool = True) -> CapabilityCatalog:
    names: tuple[ProductName, ...] = (
        "electronic_energy",
        "hessian",
        "harmonic_frequencies",
        "normal_modes",
        "zero_point_energy",
        "gibbs_correction",
        "gibbs_free_energy",
        "enthalpy_correction",
        "enthalpy",
    )
    method = MethodCapability(
        method="scf",
        driver="frequency",
        reference="rhf",
        status="supported",
        quantity=QuantityType(meaning="electronic_energy", unit="hartree"),
        features=("vibrational_analysis:ideal_gas_rrho", "native_vibrec"),
        evidence=("fixture",),
        products=tuple(
            ProductCapability(
                name=name,
                status="supported",
                quantity=product_quantity(name),
                evidence=("fixture",),
            )
            for name in names
        )
        if products
        else (),
    )
    return CapabilityCatalog(
        id="product-fixture",
        evidence=base.evidence,
        bases=base.bases,
        methods=(
            *tuple(item for item in base.methods if item.driver != "frequency"),
            method,
        ),
    )


def _request(*, analysis: VibrationalAnalysis | None = None) -> ScientificRequest:
    return ScientificRequest(
        molecules=(molecule("h2", _geometry()),),
        goals=(
            CalculationGoal(
                id="frequency",
                driver="frequency",
                geometry="h2",
                models=(_model(),),
                analysis=analysis,
            ),
            ProductGoal(
                id="spectrum", calculation="frequency", name="harmonic_frequencies"
            ),
        ),
    )


def test_thermal_settings_require_the_full_frequency_driver() -> None:
    """Reject thermal intent attached to an energy call that cannot perform it."""
    geometry = Molecule.from_xyz(
        "2\nH2\nH 0 0 0\nH 0 0 .8\n", state=ElectronicState(charge=0, multiplicity=1)
    )
    plan = Plan(
        molecules=(molecule("h2", geometry),),
        steps=(
            Calculation(
                id="energy",
                driver="energy",
                geometry="h2",
                model=Model(method="scf", basis="sto-3g", reference="rhf"),
                analysis=VibrationalAnalysis(
                    conditions=ThermalConditions(
                        temperature_kelvin=298.15, pressure_pascal=101325.0
                    ),
                    rotational_symmetry_number=2,
                ),
            ),
        ),
        requirements=(SameModel(calculations=("energy", "energy")),),
    )

    report = verify(plan)

    assert report.status == "invalid"
    assert any(item.code == "analysis_driver" for item in report.diagnostics)


def test_named_spectrum_has_typed_provenance_without_replacing_primary_energy(
    formal_profile: CapabilityCatalog,
) -> None:
    """Keep frequency-return energy distinct from the expected complex mode spectrum.

    Args:
        formal_profile: Synthetic method evidence to extend with named products.
    """
    proposal = propose(_request(), _profile(formal_profile))

    assert proposal.status == "constructed"
    assert proposal.report is not None
    quantities = {item.id: item for item in proposal.report.quantities}
    assert quantities["frequency"].quantity.meaning == "electronic_energy"
    spectrum = quantities["spectrum"]
    assert spectrum.quantity.meaning == "harmonic_frequencies"
    assert spectrum.quantity.unit == "cm^-1"
    assert spectrum.quantity.shape == ("3*atoms",)
    assert spectrum.quantity.number_kind == "complex"
    assert spectrum.geometry == "h2"
    assert spectrum.producer == "frequency"


def test_real_only_spectrum_claim_cannot_weaken_the_named_product_contract(
    formal_profile: CapabilityCatalog,
) -> None:
    """Reject a goal that erases the possibility of imaginary harmonic frequencies.

    Args:
        formal_profile: Synthetic producing method and product evidence.
    """
    request = _request()
    incorrect = ProductGoal(
        id="spectrum",
        calculation="frequency",
        name="harmonic_frequencies",
        quantity=QuantityType(
            meaning="harmonic_frequencies", unit="cm^-1", shape=("3*atoms",)
        ),
    )
    request = ScientificRequest(
        molecules=request.molecules, goals=(request.goals[0], incorrect)
    )

    proposal = propose(request, _profile(formal_profile))

    assert proposal.status == "no_candidate"
    assert any(item.code == "product_quantity" for item in proposal.diagnostics)


def test_oriented_product_requires_the_producing_frame_and_requested_property() -> None:
    """Keep a dipole tied to an explicit property call and its native frame."""
    plan = Plan(
        molecules=(molecule("h2", _geometry()),),
        steps=(
            Calculation(
                id="property_call",
                driver="properties",
                geometry="h2",
                model=_model(),
                properties=("MULLIKEN_CHARGES",),
            ),
            Product(
                id="dipole",
                calculation="property_call",
                name="dipole",
                quantity=QuantityType(
                    meaning="dipole", unit="e*bohr", shape=(3,), frame="h2"
                ),
            ),
        ),
        requirements=(SameModel(calculations=("property_call", "property_call")),),
    )

    report = verify(plan)

    assert any(item.code == "product_driver" for item in report.diagnostics)
    assert any(item.code == "product_quantity" for item in report.diagnostics)


def test_frequency_product_files_have_distinct_labels_and_declared_encodings() -> None:
    """Prevent two calls on one geometry from overwriting the same native record."""
    plan = Plan(
        molecules=(molecule("h2", _geometry()),),
        steps=(
            Calculation(
                id="first",
                driver="frequency",
                geometry="h2",
                model=_model(),
                analysis=_analysis(),
            ),
            Product(id="first_g", calculation="first", name="gibbs_correction"),
            Calculation(
                id="second",
                driver="frequency",
                geometry="h2",
                model=_model(),
                analysis=_analysis(400.0),
            ),
            Product(id="second_g", calculation="second", name="gibbs_correction"),
        ),
        requirements=(SameModel(calculations=("first", "second")),),
    )

    report = verify(plan)

    assert report.status == "proved"
    assert len({item.label for item in report.native_outputs}) == 2
    assert [item.bindings[0].encoding for item in report.native_outputs] == [
        "qcelemental_datum_json"
    ] * 2
    assert report.native_outputs[0].bindings[0].key == "G_corr"


def test_method_support_alone_does_not_establish_secondary_product_support(
    formal_profile: CapabilityCatalog,
) -> None:
    """Require combination-specific product evidence rather than assuming all outputs.

    Args:
        formal_profile: Base declarations without secondary product evidence.
    """
    proposal = propose(_request(), _profile(formal_profile, products=False))

    assert proposal.status == "unknown"
    assert any(item.code == "product_support" for item in proposal.diagnostics)


def test_required_products_cannot_be_omitted_from_an_otherwise_complete_job(
    formal_profile: CapabilityCatalog,
) -> None:
    """Derive mandatory product coverage independently from plan assertions.

    Args:
        formal_profile: Method and product declarations.
    """
    request = _request()
    catalog = _profile(formal_profile)
    proposal = propose(request, catalog)
    assert proposal.plan is not None
    damaged = Plan(
        molecules=proposal.plan.molecules,
        steps=proposal.plan.steps[:1],
        requirements=proposal.plan.requirements,
    )

    report = verify(damaged, request=request, catalog=catalog)

    assert report.status == "violated"
    assert report.coverage[-1].status == "missing"


def test_gibbs_correction_requires_explicit_thermal_conditions() -> None:
    """Keep native defaults separate from asserted thermodynamic conditions."""
    plan = Plan(
        molecules=(molecule("h2", _geometry()),),
        steps=(
            Calculation(
                id="frequency", driver="frequency", geometry="h2", model=_model()
            ),
            Product(id="g", calculation="frequency", name="gibbs_correction"),
        ),
        requirements=(SameModel(calculations=("frequency", "frequency")),),
    )

    report = verify(plan)

    assert report.status == "unknown"
    assert any(item.code == "product_thermal_context" for item in report.diagnostics)


def test_native_total_and_electronic_plus_correction_share_an_exact_contract() -> None:
    """Prove the named total's algebra without calculating or reading a Gibbs value."""
    terms = (
        EnergyTerm(result="frequency", coefficient=1),
        EnergyTerm(result="correction", coefficient=1),
    )
    plan = Plan(
        molecules=(molecule("h2", _geometry()),),
        steps=(
            Calculation(
                id="frequency",
                driver="frequency",
                geometry="h2",
                model=_model(),
                analysis=_analysis(),
            ),
            Product(id="correction", calculation="frequency", name="gibbs_correction"),
            Product(id="total", calculation="frequency", name="gibbs_free_energy"),
            Combination(
                id="assembled",
                terms=terms,
                quantity=QuantityType(meaning="gibbs_free_energy", unit="hartree"),
            ),
        ),
        requirements=(EnergyFormula(result="total", terms=terms),),
    )

    report = verify(plan)

    assert report.status == "proved"
    assert report.obligations[0].proof
    assert report.quantities[-1].analysis == _analysis()


@pytest.mark.parametrize("damage", ["double_correction", "temperature", "geometry"])
def test_thermal_composition_requires_the_right_formula_context_and_geometry(
    damage: str,
) -> None:
    """Reject internally consistent algebra that mixes thermodynamic definitions.

    Args:
        damage: Independent scientific mismatch to introduce.
    """
    molecules = (molecule("h2", _geometry()), molecule("other", _geometry()))
    plan = Plan(
        molecules=molecules,
        steps=(
            Calculation(
                id="frequency",
                driver="frequency",
                geometry="h2",
                model=_model(),
                analysis=_analysis(),
            ),
            Calculation(
                id="second",
                driver="frequency",
                geometry="other" if damage == "geometry" else "h2",
                model=_model(),
                analysis=_analysis(400.0 if damage == "temperature" else 298.15),
            ),
            Product(
                id="first_correction", calculation="frequency", name="gibbs_correction"
            ),
            Product(
                id="second_correction", calculation="second", name="gibbs_correction"
            ),
            Combination(
                id="g",
                quantity=QuantityType(meaning="gibbs_free_energy", unit="hartree"),
                terms=(
                    EnergyTerm(result="frequency", coefficient=1),
                    EnergyTerm(
                        result="first_correction",
                        coefficient=1
                        if damage == "double_correction"
                        else Rational(numerator=1, denominator=2),
                    ),
                    EnergyTerm(
                        result="second_correction",
                        coefficient=1
                        if damage == "double_correction"
                        else Rational(numerator=1, denominator=2),
                    ),
                ),
            ),
        ),
        requirements=(SameModel(calculations=("frequency", "second")),),
    )

    report = verify(plan)

    assert report.status == "violated"
    code = {
        "double_correction": "thermal_formula",
        "temperature": "thermal_context",
        "geometry": "thermal_geometry",
    }[damage]
    assert any(item.code == code for item in report.diagnostics)


def test_product_recipes_and_thermal_settings_export_without_result_retrieval(
    formal_profile: CapabilityCatalog,
    tmp_path: Path,
) -> None:
    """Export products and dependent arithmetic as recipes for a separate consumer.

    Args:
        formal_profile: Synthetic product availability declarations.
        tmp_path: Fresh bundle parent.
    """
    request = ScientificRequest(
        molecules=(molecule("h2", _geometry()),),
        goals=(
            CalculationGoal(
                id="frequency",
                driver="frequency",
                geometry="h2",
                models=(_model(),),
                analysis=_analysis(),
            ),
            ProductGoal(
                id="correction", calculation="frequency", name="gibbs_correction"
            ),
            ExpressionGoal(
                id="g",
                quantity=QuantityType(meaning="gibbs_free_energy", unit="hartree"),
                terms=(
                    GoalTerm(goal="frequency", coefficient=1),
                    GoalTerm(goal="correction", coefficient=1),
                ),
            ),
        ),
    )
    catalog = _profile(formal_profile)
    proposal = propose(request, catalog)
    assert proposal.plan is not None

    exported = export_bundle(proposal.plan, request, catalog, tmp_path / "bundle")

    assert exported.manifest.products[0].name == "gibbs_correction"
    assert exported.manifest.native_outputs[0].products == ("correction",)
    source = (Path(exported.directory) / "inputs/workflow.dat").read_text()
    assert "ROTATIONAL_SYMMETRY_NUMBER" in source
    assert "project_trans=True" in source
    assert ".variable(" not in source
    assert "gibbs" not in source.lower()
    assert exported.manifest.quantities[-1].analysis == _analysis()
    assert (
        "gibbs" not in render(proposal.plan, request=request, catalog=catalog).lower()
    )


def test_product_goals_compose_across_namespaced_finite_cases(
    formal_profile: CapabilityCatalog,
) -> None:
    """Keep source calculations and oriented product frames in their own case histories.

    Args:
        formal_profile: Synthetic method and product evidence.
    """
    template = _request()
    request = finite_study(
        template,
        (
            StudyCase(id="a", molecules=template.molecules),
            StudyCase(id="b", molecules=template.molecules),
        ),
    )

    proposal = propose(request, _profile(formal_profile))

    assert proposal.plan is not None
    assert [
        step.calculation for step in proposal.plan.steps if isinstance(step, Product)
    ] == ["a:frequency", "b:frequency"]


@pytest.mark.skipif(
    os.environ.get("PSI4_PYTHON") is None,
    reason="Set PSI4_PYTHON for native thermal option checks",
)
def test_native_thermal_settings_are_effective_and_restored(tmp_path: Path) -> None:
    """Inspect generated-call settings without performing a chemistry calculation.

    Args:
        tmp_path: Isolated native interpreter workspace.
    """
    plan = Plan(
        molecules=(molecule("h2", _geometry()),),
        steps=(
            Calculation(
                id="frequency",
                driver="frequency",
                geometry="h2",
                model=_model(),
                analysis=_analysis(),
            ),
            Product(id="g", calculation="frequency", name="gibbs_correction"),
        ),
        requirements=(SameModel(calculations=("frequency", "frequency")),),
    )
    program = """import sys, psi4
psi4.core.set_output_file('native.dat', False)
psi4.core.set_local_option('THERMO','T',999.)
psi4.core.set_local_option('THERMO','P',40000.)
psi4.core.set_local_option('THERMO','ROTATIONAL_SYMMETRY_NUMBER',7)
calls=[]
def observe(name, **kwargs):
    assert psi4.core.get_option('THERMO','T') == 298.15
    assert psi4.core.get_option('THERMO','P') == 101325.
    assert psi4.core.get_option('THERMO','ROTATIONAL_SYMMETRY_NUMBER') == 2
    assert kwargs['project_trans'] is True and kwargs['project_rot'] is True
    calls.append(name)
    return 0.
psi4.frequency=observe
namespace={'psi4':psi4}
translated=psi4.process_input(sys.stdin.read(), print_level=0)
exec(compile(translated, '<generated>', 'exec'),namespace)
assert calls == ['scf']
assert psi4.core.get_option('THERMO','T') == 999.
assert psi4.core.get_option('THERMO','P') == 40000.
assert psi4.core.get_option('THERMO','ROTATIONAL_SYMMETRY_NUMBER') == 7
assert psi4.core.has_local_option_changed('THERMO','T')
assert 'g' not in namespace['formal_results']
print('thermal settings isolated')
"""
    # The interpreter and harness are explicit; no shell is used.
    completed = subprocess.run(  # noqa: S603
        [os.environ["PSI4_PYTHON"], "-c", program],
        input=render(plan),
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert completed.stdout.strip().endswith("thermal settings isolated")


def test_product_discovery_retains_conditions_without_expanding_method_products(
    tmp_path: Path,
) -> None:
    """Retrieve one product fact with its producing scope and saved evidence.

    Args:
        tmp_path: Fresh artifact workspace.
    """
    workspace = PlanningWorkspace(tmp_path / "planning")
    reference = workspace.load_catalog("psi4")
    products = workspace.capabilities(
        reference.handle,
        CapabilityQuery(
            section="products",
            name="hf",
            driver="frequency",
            product="gibbs_correction",
            limit=1,
        ),
    )
    methods = workspace.capabilities(
        reference.handle, CapabilityQuery(name="hf", driver="frequency", limit=1)
    )

    # Three references, each with two basis groups for automatic/analytic
    # routes and one finite-difference case.
    assert products.total == 9
    assert products.next_offset == 1
    assert "conditions" in str(products.items[0])
    assert "gibbs_correction" in str(products.items[0])
    assert "product_count" in str(methods.items[0])
    assert "gibbs_correction" not in str(methods.items[0])


@pytest.mark.skipif(
    os.environ.get("PSI4_PYTHON") is None,
    reason="Set PSI4_PYTHON for native product contracts",
)
def test_native_frequency_and_property_products_match_reviewed_contracts(
    tmp_path: Path,
) -> None:
    """Check product availability separately from the public construction framework.

    Args:
        tmp_path: Isolated engine output and scratch directory.
    """
    names = (
        "DIPOLE",
        "QUADRUPOLE",
        "MULLIKEN_CHARGES",
        "LOWDIN_CHARGES",
        "MAYER_INDICES",
        "WIBERG_LOWDIN_INDICES",
    )
    plan = Plan(
        molecules=(molecule("h2", _geometry()),),
        steps=(
            Calculation(
                id="frequency",
                driver="frequency",
                geometry="h2",
                model=_model(),
                analysis=_analysis(),
            ),
            Calculation(
                id="properties",
                driver="properties",
                geometry="h2",
                model=_model(),
                properties=names,
            ),
            Product(id="g", calculation="frequency", name="gibbs_correction"),
        ),
        requirements=(SameModel(calculations=("frequency", "properties")),),
    )
    program = """import sys, json, os, pathlib, psi4, numpy as np
psi4.core.set_output_file('native.dat', False)
psi4.set_memory('256MiB')
psi4.set_num_threads(1)
original_frequency=psi4.frequency
original_properties=psi4.properties
captured={}
def frequency(*args, **kwargs):
    energy,wfn=original_frequency(*args,return_wfn=True,**kwargs)
    captured['frequency']=wfn
    return energy
def properties(*args, **kwargs):
    energy,wfn=original_properties(*args,return_wfn=True,**kwargs)
    captured['properties']=wfn
    return energy
psi4.frequency=frequency
psi4.properties=properties
namespace={'psi4':psi4}
translated=psi4.process_input(sys.stdin.read(),print_level=0)
exec(compile(translated,'<generated>','exec'),namespace)
wfn=captured['frequency']
assert wfn.frequency_analysis['omega'].data.shape == (6,)
assert wfn.frequency_analysis['x'].data.shape == (6,6)
assert wfn.frequency_analysis['omega'].units == 'cm^-1'
assert wfn.frequency_analysis['x'].units == 'a0'
assert wfn.hessian().shape == (6,6)
energy=namespace['formal_results']['frequency']
files=list(pathlib.Path('.').glob('formal_*.vibrec'))
assert len(files) == 1
record=json.loads(files[0].read_text())
assert abs(json.loads(record['G_tot'])['data'] - energy -
           json.loads(record['G_corr'])['data']) < 1e-10
assert json.loads(record['T'])['data'] == 298.15
assert json.loads(record['P'])['data'] == 101325.
properties=captured['properties']
assert np.asarray(properties.variable('SCF DIPOLE')).size == 3
assert np.asarray(properties.variable('SCF QUADRUPOLE')).size in {6,9}
for name in ('MULLIKEN CHARGES','LOWDIN CHARGES'):
    assert np.asarray(properties.variable(name)).size == 2
for name in ('MAYER INDICES','WIBERG LOWDIN INDICES'):
    assert np.asarray(properties.variable(name)).shape == (2,2)
print('reviewed products available')
"""
    # This fixed development harness is separate from construction/export APIs.
    completed = subprocess.run(  # noqa: S603
        [os.environ["PSI4_PYTHON"], "-c", program],
        input=render(plan),
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        timeout=90,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert completed.stdout.strip().endswith("reviewed products available")
