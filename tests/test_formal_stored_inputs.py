"""Check molecular handle reuse without weakening independent scientific intent."""

from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from pydantic import JsonValue, TypeAdapter, ValidationError

from psi4_parser.builder import (
    Atom,
    Cartesian,
    ElectronicState,
    Fragment,
    Molecule,
    Nucleus,
    angstrom,
    distance,
    molecule,
)
from psi4_parser.formal import (
    CalculationGoal,
    CoordinateValue,
    Model,
    MoleculeBinding,
    Plan,
    PlanningWorkspace,
    RequestTemplate,
    ScientificRequest,
    Setting,
    StoredMolecule,
    describe_schema,
    verify,
)
from psi4_parser.formal.interface_models import RecordKind


def _geometry() -> Molecule:
    return Molecule.from_xyz(
        "2\nH2\nH 0 0 0\nH 0 0 .8\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )


def _goal(name: str = "h2") -> CalculationGoal:
    return CalculationGoal(
        id="energy",
        geometry=name,
        driver="energy",
        models=(
            Model(
                method="hf",
                basis="sto-3g",
                reference="rhf",
                settings=(Setting(name="scf_type", value="PK"),),
            ),
        ),
    )


def _saved_template(workspace: PlanningWorkspace, handle: str) -> str:
    return workspace.import_json(
        "request_template",
        RequestTemplate(
            molecules=(MoleculeBinding(name="h2", molecule=handle),),
            goals=(_goal(),),
        ).model_dump_json(),
    ).handle


def test_reused_geometry_yields_the_exact_independent_request(tmp_path: Path) -> None:
    """Preserve ordered goals and relations while naming one input more than once.

    Args:
        tmp_path: Persistent source and relocated workspace directories.
    """
    geometry = _geometry()
    workspace = PlanningWorkspace(tmp_path / "work")
    saved = workspace.save_molecule(geometry)
    same = workspace.import_json(
        "molecule", StoredMolecule(geometry=geometry).model_dump_json()
    )
    goal = _goal("left")
    relation = CoordinateValue(
        geometry="left",
        coordinate=distance("a1", "a2"),
        value=angstrom(0.8),
        tolerance=angstrom(1e-8),
    )
    draft = RequestTemplate(
        molecules=(
            MoleculeBinding(name="left", molecule=saved.handle),
            MoleculeBinding(name="right", molecule=saved.handle),
        ),
        goals=(goal,),
        relations=(relation,),
    )
    template = workspace.import_json("request_template", draft.model_dump_json())
    direct = workspace.import_json(
        "request",
        ScientificRequest(
            molecules=(molecule("left", geometry), molecule("right", geometry)),
            goals=(goal,),
            relations=(relation,),
        ).model_dump_json(),
    )

    materialized = workspace.materialize_request(template.handle)

    assert saved == same
    assert materialized == direct
    # A copied workspace remains usable without its original absolute paths.
    relocated = tmp_path / "relocated"
    workspace.directory.rename(relocated)
    reopened = PlanningWorkspace(relocated)
    assert reopened.materialize_request(template.handle).handle == direct.handle
    proposal = reopened.propose(direct.handle)
    assert proposal.status == "constructed"
    assert proposal.verification is not None
    assert proposal.verification.request_complete


def test_molecular_metadata_survives_materialization(tmp_path: Path) -> None:
    """Preserve stable identities, isotopes, ghosts, fragments, units, and frames.

    Args:
        tmp_path: Workspace retaining exact molecular records.
    """
    geometry = Molecule(
        atoms=(
            Atom(
                id="isotope",
                nucleus=Nucleus(label="2H", mass=2.014),
                coordinates=Cartesian(x=0.0, y=0.0, z=0.0, unit="bohr"),
            ),
            Atom(
                id="ghost",
                nucleus=Nucleus(label="He", ghost="gh"),
                coordinates=Cartesian(x=0.0, y=0.0, z=3.0, unit="bohr"),
            ),
        ),
        fragments=(
            Fragment(
                name="real",
                atom_ids=("isotope",),
                state=ElectronicState(charge=0, multiplicity=2),
            ),
            Fragment(
                name="basis",
                atom_ids=("ghost",),
                state=ElectronicState(charge=0, multiplicity=1),
            ),
        ),
        state=ElectronicState(charge=0, multiplicity=2),
        units="bohr",
        symmetry="c1",
        fixed_com=True,
        fixed_orientation=True,
    )
    workspace = PlanningWorkspace(tmp_path / "workspace")
    saved = workspace.save_molecule(geometry)

    complete = workspace.materialize_request(_saved_template(workspace, saved.handle))

    request = ScientificRequest.model_validate_json(Path(complete.path).read_bytes())
    assert request.molecules == (molecule("h2", geometry),)
    # Structural import is not approval of this RHF doublet calculation.
    rejected = workspace.propose(complete.handle)
    assert rejected.status != "constructed"


@pytest.mark.parametrize("damage", ["molecule", "request_template", "missing"])
def test_changed_or_missing_dependencies_cannot_be_materialized(
    tmp_path: Path, damage: str
) -> None:
    """Reject changed saved bytes or a missing molecule without saving a request.

    Args:
        tmp_path: Workspace whose imported copy is deliberately damaged.
        damage: Record to modify, or remove the molecule entirely.
    """
    workspace = PlanningWorkspace(tmp_path / "work")
    saved = workspace.save_molecule(_geometry())
    template = workspace.reference(_saved_template(workspace, saved.handle))
    path = Path(template.path if damage == "request_template" else saved.path)
    error: type[FileNotFoundError] | type[ValueError]
    if damage == "missing":
        path.unlink()
        error = FileNotFoundError
        message = "No such file"
    else:
        path.write_text("{}")
        error = ValueError
        message = "content no longer matches"

    with pytest.raises(error, match=message):
        workspace.materialize_request(template.handle)

    assert not list((workspace.directory / "records").glob("request-*.json"))


def test_materialized_request_and_bundle_are_independent_of_handles(
    tmp_path: Path,
) -> None:
    """Export and independently verify after all template dependencies are removed.

    Args:
        tmp_path: Molecular records and a separately retained construction bundle.
    """
    workspace = PlanningWorkspace(tmp_path / "workspace")
    saved = workspace.save_molecule(_geometry())
    template = workspace.reference(_saved_template(workspace, saved.handle))
    request = workspace.materialize_request(template.handle)
    Path(template.path).unlink()
    Path(saved.path).unlink()

    proposed = workspace.propose(request.handle)

    assert proposed.plan is not None
    exported = workspace.export(
        proposed.plan.handle, request.handle, None, tmp_path / "bundle"
    )
    assert exported.status == "exported"
    assert exported.manifest_path is not None
    complete = ScientificRequest.model_validate_json(
        (Path(exported.manifest_path).parent / "scientific-request.json").read_bytes()
    )
    assert complete.molecules == (molecule("h2", _geometry()),)
    assert "molecule:" not in complete.model_dump_json()
    plan = Plan.model_validate_json(Path(proposed.plan.path).read_bytes())
    assert verify(plan, request=complete).request_complete


def test_assembled_size_bound_cannot_be_bypassed_by_small_handles(
    tmp_path: Path,
) -> None:
    """Enforce the byte bound on a request larger than any of its source records.

    Args:
        tmp_path: A workspace reopened with a smaller per-record byte limit.
    """
    workspace = PlanningWorkspace(tmp_path / "workspace")
    saved = workspace.save_molecule(_geometry())
    bindings = tuple(
        MoleculeBinding(name=f"input_{index}", molecule=saved.handle)
        for index in range(8)
    )
    template = workspace.import_json(
        "request_template",
        RequestTemplate(
            molecules=(
                *bindings,
                MoleculeBinding(name="unread", molecule="molecule:" + "a" * 64),
            ),
            goals=(_goal("input_0"),),
        ).model_dump_json(),
    )
    smaller = PlanningWorkspace(
        workspace.directory, max_record_bytes=max(saved.bytes, template.bytes)
    )

    with pytest.raises(ValueError, match="byte limit"):
        smaller.materialize_request(template.handle)

    assert not list((workspace.directory / "records").glob("request-*.json"))


def test_template_names_and_handle_kinds_are_unambiguous() -> None:
    """Reject duplicate input names and handles for non-molecular records."""
    binding = MoleculeBinding(name="h2", molecule="molecule:" + "a" * 64)
    with pytest.raises(ValidationError, match="names must be unique"):
        RequestTemplate(molecules=(binding, binding), goals=(_goal(),))
    with pytest.raises(ValidationError, match="string_pattern_mismatch"):
        MoleculeBinding(name="h2", molecule="request:" + "a" * 64)


def test_template_and_molecule_are_not_accepted_as_complete_requests(
    tmp_path: Path,
) -> None:
    """Require a complete independent request before entering scientific planning.

    Args:
        tmp_path: Molecular and template preparation records.
    """
    workspace = PlanningWorkspace(tmp_path / "workspace")
    saved = workspace.save_molecule(_geometry())
    template = _saved_template(workspace, saved.handle)

    with pytest.raises(ValueError, match="Expected request, received request_template"):
        workspace.propose(template)
    with pytest.raises(
        ValueError, match="Expected request_template, received molecule"
    ):
        workspace.materialize_request(saved.handle)


def test_stored_input_schemas_are_discoverable_and_closed() -> None:
    """Expose selected molecular and template fields with complete referenced types."""
    kinds: tuple[RecordKind, ...] = ("molecule", "request_template")
    for kind in kinds:
        description = describe_schema(kind)
        assert all(field.description for field in description.fields)
    selected = describe_schema("request_template", fields=("molecules", "goals"))
    assert selected.json_schema is not None
    validator = Draft202012Validator(selected.json_schema)
    validator.check_schema(selected.json_schema)
    template = RequestTemplate(
        molecules=(MoleculeBinding(name="h2", molecule="molecule:" + "a" * 64),),
        goals=(_goal(),),
    )
    value = TypeAdapter(JsonValue).validate_json(
        template.model_dump_json(exclude={"schema_version", "relations"})
    )
    assert validator.is_valid(value)
