"""Keep capability evidence distinct from solver proofs and application execution."""

import json
from pathlib import Path

import pytest
from pydantic import JsonValue, TypeAdapter, ValidationError

from psi4_parser.builder import ElectronicState, Molecule, molecule
from psi4_parser.formal import (
    Calculation,
    CapabilityCatalog,
    ComponentCapability,
    ComponentRequirement,
    MethodCapability,
    Model,
    OptionCapability,
    OptionCondition,
    Plan,
    QuantityType,
    SameModel,
    ScientificRequest,
    Setting,
    discover_capabilities,
    export_bundle,
    render,
    verify,
)
from psi4_parser.formal.capabilities import Support
from psi4_parser.formal.intent import CalculationGoal


def single_point(model: Model) -> tuple[ScientificRequest, Plan]:
    """Return independent intent and implementation for one H2 energy."""
    geometry = Molecule.from_xyz(
        "2\nH2\nH 0 0 0\nH 0 0 .85\n", state=ElectronicState(charge=0, multiplicity=1)
    )
    request = ScientificRequest(
        molecules=(molecule("h2", geometry),),
        goals=(
            CalculationGoal(
                id="energy", driver="energy", geometry="h2", models=(model,)
            ),
        ),
    )
    plan = Plan(
        molecules=request.molecules,
        steps=(
            Calculation(
                id="e",
                driver="energy",
                geometry="h2",
                model=model,
                satisfies=("energy",),
            ),
        ),
        requirements=(SameModel(calculations=("e", "e")),),
    )
    return request, plan


@pytest.mark.parametrize(
    ("setting", "status"), [(None, "unknown"), ("df", "unknown"), ("pK", "proved")]
)
def test_method_evidence_applies_only_to_declared_algorithm_conditions(
    formal_profile: CapabilityCatalog,
    setting: str | None,
    status: str,
) -> None:
    """Keep unexamined algorithms unknown and accept the evidenced explicit route.

    Args:
        formal_profile: Synthetic base capability facts.
        setting: Omitted, unexamined, or covered SCF algorithm.
        status: Expected verification result independent of the algebra.
    """
    method = MethodCapability(
        method="scf",
        driver="energy",
        reference="rhf",
        status="supported",
        quantity=QuantityType(meaning="electronic_energy", unit="hartree"),
        conditions=(
            OptionCondition(name="scf_type", values=("PK",), case_sensitive=False),
        ),
        options=("scf_type",),
        evidence=("fixture",),
    )
    catalog = CapabilityCatalog(
        id="conditional-fixture",
        evidence=formal_profile.evidence,
        methods=(method,),
        bases=formal_profile.bases,
        options=(
            OptionCapability(
                name="scf_type",
                status="supported",
                values=("PK", "DF"),
                case_sensitive=False,
                evidence=("fixture",),
            ),
        ),
    )
    settings = () if setting is None else (Setting(name="scf_type", value=setting),)
    request, plan = single_point(
        Model(method="scf", basis="sto-3g", reference="rhf", settings=settings)
    )

    report = verify(plan, request=request, catalog=catalog)

    assert report.status == status
    if status == "unknown":
        assert any(issue.code == "capability_condition" for issue in report.diagnostics)


def test_case_insensitive_option_domains_preserve_nonstring_literal_types() -> None:
    """Fold enum string case without equating booleans and integers in arrays."""
    option = OptionCapability(
        name="sample",
        status="supported",
        values=("PK", ("VALUE", 1)),
        case_sensitive=False,
        evidence=("external",),
    )

    assert option.accepts("pK")
    assert option.accepts(("value", 1))
    assert not option.accepts(("value", True))


def test_global_scope_aliases_cannot_hide_overwriting_model_settings() -> None:
    """Reject two declarations that native Psi4 will apply to the same option."""
    with pytest.raises(ValidationError, match="unique"):
        Model(
            method="scf",
            basis="sto-3g",
            reference="rhf",
            settings=(
                Setting(name="scf_type", value="PK"),
                Setting(name="scf_type", module="GLOBALS", value="DF"),
            ),
        )


def test_option_evidence_normalizes_native_global_scope_aliases() -> None:
    """Keep condition lookup and option availability aligned with emitted scopes."""
    condition = OptionCondition(name="scf_type", module="GLOBAL", values=("PK",))
    option = OptionCapability(
        name="scf_type",
        module="GLOBALS",
        status="supported",
        values=("PK",),
        evidence=("external",),
    )

    assert condition.key == ("", "scf_type")
    assert option.key == "scf_type"


@pytest.mark.parametrize(
    ("frozen", "expected"), [(False, "proved"), (True, "unsupported")]
)
def test_disjoint_cases_resolve_dedicated_model_settings(
    formal_profile: CapabilityCatalog,
    frozen: bool,
    expected: str,
) -> None:
    """Select the relevant positive or negative case using the actual lowered value.

    Args:
        formal_profile: Synthetic evidence and basis dimensions.
        frozen: Core treatment explicitly represented by the model.
        expected: Outcome of the matching case alone.
    """
    catalog = CapabilityCatalog(
        id="core-cases",
        evidence=formal_profile.evidence,
        bases=formal_profile.bases,
        methods=tuple(
            MethodCapability(
                method="scf",
                driver="energy",
                reference="rhf",
                status="unsupported" if core else "supported",
                quantity=QuantityType(meaning="electronic_energy", unit="hartree"),
                conditions=(OptionCondition(name="freeze_core", values=(core,)),),
                features=("frozen_core",),
                evidence=("fixture",),
            )
            for core in (False, True)
        ),
    )
    request, plan = single_point(
        Model(method="scf", basis="sto-3g", reference="rhf", frozen_core=frozen)
    )

    assert verify(plan, request=request, catalog=catalog).status == expected


def test_profile_rejects_overlapping_case_insensitive_conditions(
    formal_profile: CapabilityCatalog,
) -> None:
    """Prevent ambiguous support when two declarations can match the same settings.

    Args:
        formal_profile: Evidence identity for the deliberately ambiguous cases.
    """
    cases = tuple(
        MethodCapability(
            method="scf",
            driver="energy",
            reference="rhf",
            status="supported",
            quantity=QuantityType(meaning="electronic_energy", unit="hartree"),
            conditions=(
                OptionCondition(
                    name="scf_type", values=(value,), case_sensitive=sensitive
                ),
            ),
            evidence=("fixture",),
        )
        for value, sensitive in (("PK", False), ("pk", True))
    )

    with pytest.raises(ValidationError, match="overlap"):
        CapabilityCatalog(
            id="ambiguous",
            evidence=formal_profile.evidence,
            methods=cases,
        )


@pytest.mark.parametrize(
    ("availability", "expected"),
    [
        (None, "proved"),
        ("unknown", "proved"),
        ("unsupported", "proved"),
        ("supported", "proved"),
    ],
)
def test_optional_component_observations_do_not_constrain_construction(
    formal_profile: CapabilityCatalog,
    availability: Support | None,
    expected: str,
    recwarn: pytest.WarningsRecorder,
) -> None:
    """Accept the plan regardless of reference component availability.

    Args:
        formal_profile: Synthetic application evidence.
        availability: Optional component status, or absent evidence.
        expected: Independent verification outcome.
        recwarn: Captured Python warnings, which must remain empty.
    """
    model = Model(method="scf", basis="sto-3g", reference="rhf")
    original, _ = single_point(model)
    request = ScientificRequest(
        molecules=original.molecules,
        goals=(
            CalculationGoal(
                id="opt",
                driver="optimize",
                geometry="h2",
                models=(model,),
            ),
        ),
    )
    plan = Plan(
        molecules=request.molecules,
        steps=(
            Calculation(
                id="opt",
                driver="optimize",
                geometry="h2",
                model=model,
                satisfies=("opt",),
            ),
        ),
        requirements=(SameModel(calculations=("opt", "opt")),),
    )
    catalog = CapabilityCatalog(
        id="optimizer-fixture",
        evidence=formal_profile.evidence,
        bases=formal_profile.bases,
        methods=(
            MethodCapability(
                method="scf",
                driver="optimize",
                reference="rhf",
                status="supported",
                quantity=QuantityType(meaning="electronic_energy", unit="hartree"),
                components=("optking",),
                evidence=("fixture",),
            ),
        ),
        components=()
        if availability is None
        else (
            ComponentCapability(
                name="optking",
                version="test/2",
                status=availability,
                evidence=("fixture",),
            ),
        ),
    )

    report = verify(plan, request=request, catalog=catalog)

    assert report.status == expected
    assert not any(issue.code == "component_support" for issue in report.diagnostics)
    assert not recwarn


def test_component_requirements_survive_verification_and_export(
    tmp_path: Path,
    formal_profile: CapabilityCatalog,
) -> None:
    """Describe used component names without pinning the operator's installation.

    Args:
        tmp_path: New bundle parent.
        formal_profile: Synthetic application declarations.
    """
    request, plan = single_point(Model(method="scf", basis="sto-3g", reference="rhf"))
    catalog = CapabilityCatalog(
        id="component-fixture",
        evidence=formal_profile.evidence,
        bases=formal_profile.bases,
        methods=(
            MethodCapability(
                method="scf",
                driver="energy",
                reference="rhf",
                status="supported",
                quantity=QuantityType(meaning="electronic_energy", unit="hartree"),
                components=("auxiliary_library",),
                evidence=("fixture",),
            ),
        ),
        components=(
            ComponentCapability(
                name="auxiliary_library",
                version="test/2",
                status="supported",
                evidence=("fixture",),
            ),
        ),
    )

    report = verify(plan, request=request, catalog=catalog)

    expected = (ComponentRequirement(name="auxiliary_library"),)
    assert report.status == "proved"
    assert report.required_components == expected
    exported = export_bundle(plan, request, catalog, tmp_path / "bundle")
    assert exported.manifest.required_components == expected


def test_declared_support_and_proof_are_bound_to_the_profile(
    formal_profile: CapabilityCatalog,
) -> None:
    """Record evidence identity and expose explicit declaration assumptions.

    Args:
        formal_profile: Synthetic capability declarations used only by planner tests.
    """
    request, plan = single_point(Model(method="scf", basis="sto-3g", reference="rhf"))

    report = verify(plan, request=request, catalog=formal_profile)

    assert report.status == "proved"
    assert report.request_complete
    assert report.capability_digest
    assert "application_version" not in type(report).model_fields
    assert any(
        "Declared capability assumption fixture" in item for item in report.assumptions
    )
    assert render(plan, request=request, catalog=formal_profile)
    renamed = CapabilityCatalog.model_validate_json(
        formal_profile.model_dump_json().replace(
            '"synthetic-planner-fixture"', '"second-snapshot"'
        )
    )
    assert (
        verify(plan, request=request, catalog=renamed).capability_digest
        != report.capability_digest
    )


def test_an_unlisted_method_is_unknown_not_supported(
    formal_profile: CapabilityCatalog,
) -> None:
    """Require evidence for the exact method/driver/reference/route combination.

    Args:
        formal_profile: Synthetic catalog with no MP2 entry.
    """
    request, plan = single_point(Model(method="mp2", basis="sto-3g", reference="rhf"))

    report = verify(plan, request=request, catalog=formal_profile)

    assert report.status == "unknown"
    assert any(item.code == "method_support" for item in report.diagnostics)
    assert report.obligations[0].status == "proved"


def test_explicit_unsupported_is_distinct_from_missing_evidence(
    formal_profile: CapabilityCatalog,
) -> None:
    """Preserve a negative capability declaration instead of guessing alternatives.

    Args:
        formal_profile: Synthetic catalog to extend with an unsupported combination.
    """
    unsupported = MethodCapability(
        method="mp2",
        driver="energy",
        reference="rhf",
        status="unsupported",
        quantity=QuantityType(meaning="electronic_energy", unit="hartree"),
        evidence=("fixture",),
    )
    catalog = CapabilityCatalog(
        id=formal_profile.id,
        evidence=formal_profile.evidence,
        methods=(*formal_profile.methods, unsupported),
        bases=formal_profile.bases,
        options=formal_profile.options,
    )
    request, plan = single_point(Model(method="mp2", basis="sto-3g", reference="rhf"))

    assert verify(plan, request=request, catalog=catalog).status == "unsupported"
    assert discover_capabilities(catalog, method="MP2") == (unsupported,)


@pytest.mark.parametrize(
    ("value", "status"), [("pk", "proved"), ("unknown_algorithm", "unsupported")]
)
def test_option_values_are_checked_for_the_method_combination(
    formal_profile: CapabilityCatalog, value: str, status: str
) -> None:
    """Validate an explicit numerical setting against supplied option evidence.

    Args:
        formal_profile: Synthetic catalog covering SCF_TYPE values pk and df.
        value: Requested algorithm.
        status: Independently expected verification status.
    """
    request, plan = single_point(
        Model(
            method="scf",
            basis="sto-3g",
            reference="rhf",
            settings=(Setting(name="scf_type", value=value),),
        )
    )

    assert verify(plan, request=request, catalog=formal_profile).status == status


def test_capability_version_labels_do_not_constrain_construction(
    formal_profile: CapabilityCatalog,
) -> None:
    """Retain source labels without requiring them to describe the execution host.

    Args:
        formal_profile: Synthetic version-matched catalog.
    """
    changed = formal_profile.model_dump_json().replace(
        '"application_version":"fixture/1"', '"application_version":"different/2"', 1
    )
    changed = changed.replace('"build":null', '"build":"different-binary"', 1)

    catalog = CapabilityCatalog.model_validate_json(changed)
    request, plan = single_point(Model(method="scf", basis="sto-3g", reference="rhf"))
    assert verify(plan, request=request, catalog=catalog).request_complete


def test_source_contracts_need_no_application_version_or_build(
    formal_profile: CapabilityCatalog,
) -> None:
    """Construct with versionless source contracts and no runtime diagnostics.

    Args:
        formal_profile: Scientific/input facts independent of runtime deployment.
    """
    document = TypeAdapter(JsonValue).validate_json(formal_profile.model_dump_json())
    assert isinstance(document, dict)
    document.pop("application_version", None)
    document.pop("build", None)
    evidence = document["evidence"]
    assert isinstance(evidence, list)
    for entry in evidence:
        assert isinstance(entry, dict)
        entry.pop("application_version", None)
        entry.pop("build", None)
    catalog = CapabilityCatalog.model_validate_json(json.dumps(document))
    request, plan = single_point(Model(method="scf", basis="sto-3g", reference="rhf"))

    report = verify(plan, request=request, catalog=catalog)

    assert report.request_complete
    assert "application_version" not in type(report).model_fields
    assert report.runtime_policy == "operator_managed"
    assert report.diagnostics == ()


def test_option_evidence_retains_literal_types_inside_arrays() -> None:
    """Distinguish an integer array from a boolean array in exact option evidence."""
    option = OptionCapability(
        name="indices", status="supported", values=((1,),), evidence=("external",)
    )

    assert option.accepts((1,))
    assert not option.accepts((True,))


def test_electron_occupancy_must_fit_the_declared_basis(
    formal_profile: CapabilityCatalog,
) -> None:
    """Reject an electron count that cannot fit the finite orbital basis.

    Args:
        formal_profile: Synthetic STO-3G hydrogen basis evidence.
    """
    model = Model(method="scf", basis="sto-3g", reference="rhf")
    geometry = Molecule.from_xyz(
        "2\nH2\nH 0 0 0\nH 0 0 .85\n",
        state=ElectronicState(charge=-100, multiplicity=1),
    )
    request = ScientificRequest(
        molecules=(molecule("h2", geometry),),
        goals=(
            CalculationGoal(
                id="energy", driver="energy", geometry="h2", models=(model,)
            ),
        ),
    )
    plan = Plan(
        molecules=request.molecules,
        steps=(
            Calculation(
                id="e",
                driver="energy",
                geometry="h2",
                model=model,
                satisfies=("energy",),
            ),
        ),
        requirements=(SameModel(calculations=("e", "e")),),
    )

    report = verify(plan, request=request, catalog=formal_profile)

    assert report.status == "violated"
    assert any(item.code == "basis_occupancy" for item in report.diagnostics)
