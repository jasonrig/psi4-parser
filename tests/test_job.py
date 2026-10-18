"""Exercise construction, serialization, and regeneration of native jobs."""

from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from pydantic import JsonValue, TypeAdapter

from psi4_parser.job import (
    Anchor,
    Atom,
    AtomReference,
    Basis,
    BasisAssignment,
    Cartesian,
    ElectronicState,
    Fragment,
    FragmentSeparator,
    GeometrySource,
    GeometryVariable,
    Job,
    JobSyntaxError,
    Molecule,
    Nucleus,
    Number,
    OptionAssignment,
    OptionExpression,
    OptionReference,
    Python,
    PythonTemplate,
    SetOptions,
    Symmetry,
    Units,
    Variable,
    ZMatrix,
    emit_job,
    read_job,
)

_JSON = TypeAdapter(JsonValue)


def _schema() -> Draft202012Validator:
    # Pydantic types its schema as dict[str, Any]; validate that boundary as JSON.
    schema = _JSON.validate_python(Job.model_json_schema())  # type: ignore[misc]
    assert isinstance(schema, dict)
    return Draft202012Validator(schema)


def test_mixed_fragments_keep_states_variables_and_anchor_identity() -> None:
    """Retain overall state, fragment states, and mixed coordinate records."""
    job = read_job(
        "molecule pair {\n0 1\n--\n0 2\nH 0 0 0\n--\n0 2\n"
        "@13C@13.003 1 R\nR=1.5\nno_reorient\n}\n"
    )

    molecule = job.body[0]
    assert isinstance(molecule, Molecule)
    assert molecule.name == "pair"
    state = molecule.records[0]
    assert isinstance(state, ElectronicState)
    assert state.multiplicity.value == "1"
    assert isinstance(molecule.records[1], FragmentSeparator)
    assert len(molecule.fragments) == 2
    assert all(fragment.state is not None for fragment in molecule.fragments)
    assert isinstance(molecule.atoms[0].coordinates, Cartesian)
    carbon = molecule.atoms[1]
    assert carbon.nucleus == Nucleus(
        label="13C", ghost="at", mass=Number(value="13.003")
    )
    assert isinstance(carbon.coordinates, ZMatrix)
    assert carbon.coordinates.anchors[0].atom == AtomReference(atom_id="a1")
    assert carbon.coordinates.anchors[0].value == Variable(name="R")


def test_construct_native_job_and_roundtrip_json_and_source() -> None:
    """Construct a complete calculation and recover its structure after emission."""
    molecule = Molecule(
        name="helium",
        records=(
            Atom(
                id="a1",
                nucleus=Nucleus(label="He"),
                coordinates=Cartesian(
                    x=Number(value="0"),
                    y=Number(value="0"),
                    z=Number(value="0"),
                ),
            ),
        ),
    )
    job = Job(
        body=(
            molecule,
            Basis(
                records=(BasisAssignment(basis="cc-pvdz"),),
            ),
            SetOptions(
                assignments=(
                    OptionAssignment(
                        key="reference",
                        value=OptionReference(name="reference_name"),
                    ),
                ),
            ),
            Python(source="energy('scf', molecule=helium)"),
        )
    )

    document = job.model_dump_json()
    _schema().validate(_JSON.validate_json(document))
    restored = Job.model_validate_json(document)
    source = emit_job(restored)

    assert restored == job
    assert read_job(source) == job
    assert "assign cc-pvdz" in source
    assert "reference $reference_name" in source
    assert "energy('scf', molecule=helium)" in source


def test_python_loop_keeps_native_children_accessible() -> None:
    """Represent surrounding Python as text while exposing embedded native nodes."""
    job = read_job(
        "for r in [0.7, 0.8]:\n    molecule h2 {\nH\nH 1 r\n}\n    energy('scf')\n"
    )

    template = job.body[0]
    assert isinstance(template, PythonTemplate)
    assert isinstance(template.parts[0], Python)
    assert isinstance(template.parts[1], Molecule)
    assert isinstance(template.parts[2], Python)
    assert read_job(emit_job(Job.model_validate_json(job.model_dump_json()))) == job


def test_schema_validation_precedes_python_validation() -> None:
    """Accept structurally valid Python text and diagnose its language error later."""
    job = Job(body=(Python(source="return 3"),))

    _schema().validate(_JSON.validate_json(job.model_dump_json()))
    with pytest.raises(JobSyntaxError, match="return"):
        emit_job(job)


def test_concrete_constructors_supply_serialized_discriminators() -> None:
    """Default known tags in Python while retaining tags for JSON union loading."""
    options = SetOptions(
        assignments=(
            OptionAssignment(key="basis", value=OptionExpression(source="sto-3g")),
        )
    )
    job = Job(body=(options,))

    document = _JSON.validate_json(job.model_dump_json())

    assert options.kind == "set"
    assert options.assignments[0].value.kind == "option_expression"
    _schema().validate(document)
    assert Job.model_validate_json(job.model_dump_json()) == job
    assert emit_job(job) == "set {\n    basis sto-3g\n}\n"


def test_known_json_field_type_can_use_its_default_kind() -> None:
    """Require tags at union choices while defaulting an unambiguous nested type."""
    document = '{"body":[{"kind":"memory","amount":{"value":"500"},"units":"MiB"}]}'

    _schema().validate(_JSON.validate_json(document))
    job = Job.model_validate_json(document)

    assert emit_job(job) == "memory 500 MiB\n"


@pytest.mark.parametrize(
    "document",
    [
        '{"body":[{"kind":"unknown"}]}',
        '{"body":[{"kind":"python","source":42}]}',
        '{"body":[{"kind":"python","source":"pass","extra":1}]}',
        '{"body":[{"source":"pass"}]}',
    ],
)
def test_schema_rejects_unknown_or_malformed_variants(document: str) -> None:
    """Require discriminator tags and the exact fields of the selected variant.

    Args:
        document: Structurally invalid serialized job.
    """
    assert not _schema().is_valid(_JSON.validate_json(document))
    with pytest.raises(ValueError, match="validation error"):
        Job.model_validate_json(document)


def test_geometry_parameter_update_is_immutable() -> None:
    """Replace a geometry variable without rewriting a Z-matrix as Cartesian data."""
    molecule = read_job("molecule {\nH\nH 1 R\nR=0.74\n}\n").body[0]
    assert isinstance(molecule, Molecule)

    changed = molecule.with_variable("R", Number(value="0.85"))

    assert molecule.records[-1] == GeometryVariable(
        name="R", value=Number(value="0.74")
    )
    assert changed.records[-1] == GeometryVariable(name="R", value=Number(value="0.85"))
    assert changed.atoms == molecule.atoms
    with pytest.raises(ValueError, match="Undeclared"):
        molecule.with_variable("missing", Number(value="1"))


def test_import_xyz_explicitly_reads_file(tmp_path: Path) -> None:
    """Import XYZ coordinates and its explicit unit marker.

    Args:
        tmp_path: Isolated directory for an explicitly requested import.
    """
    path = tmp_path / "geometry.xyz"
    path.write_text("2 au\nHydrogen's title\nH 0 0 0\nH 0 0 1.4\n")

    molecule = Molecule.from_file(path, name="h2")

    assert len(molecule.atoms) == 2
    assert molecule.name == "h2"
    assert molecule.records[-1] == Units(name="au")


@pytest.mark.parametrize("title", ["Hydrogen", "water", "H", ""])
def test_import_xyz_accepts_single_word_or_empty_title(title: str) -> None:
    """Treat an XYZ title as literal data even when it resembles an atom label.

    Args:
        title: Literal XYZ comment line, including an empty line.
    """
    source = "2\n" + title + "\nH 0 0 0\nH 0 0 0.74\n"

    molecule = Molecule.from_xyz(source)

    assert len(molecule.atoms) == 2
    assert read_job(emit_job(Job(body=(molecule,)))) == Job(body=(molecule,))


def test_source_reference_does_not_read_file() -> None:
    """Retain a nonexistent geometry path as data without opening it."""
    job = read_job("molecule {\nfrom_file: /nonexistent/geometry.xyz\n}\n")

    molecule = job.body[0]
    assert isinstance(molecule, Molecule)
    assert molecule.records == (
        GeometrySource(
            provider="from_file",
            value="/nonexistent/geometry.xyz",
        ),
    )
    assert read_job(emit_job(job)) == job


@pytest.mark.parametrize(
    "source", ["H 0 0 0\n", "2\nIncomplete\nH 0 0 0\n", "1\nTitle\nH\n"]
)
def test_xyz_import_requires_complete_cartesian_document(source: str) -> None:
    """Reject native geometry that does not satisfy the explicit XYZ format.

    Args:
        source: Missing XYZ header, missing atom, or non-Cartesian atom.
    """
    with pytest.raises(ValueError, match="XYZ"):
        Molecule.from_xyz(source)


def test_fragment_construction_keeps_independent_electronic_states() -> None:
    """Keep fragment doublets distinct from their overall singlet coupling."""
    first = read_job("molecule {\nH 0 0 0\n}\n").body[0]
    second = read_job("molecule {\nH 0 0 2\n}\n").body[0]
    assert isinstance(first, Molecule)
    assert isinstance(second, Molecule)
    second_atom = second.atoms[0]
    singlet = ElectronicState(
        charge=Number(value="0"),
        multiplicity=Number(value="1"),
    )
    doublet = ElectronicState(
        charge=Number(value="0"),
        multiplicity=Number(value="2"),
    )
    fragments = (
        Fragment(state=doublet, records=first.records),
        Fragment(
            state=doublet,
            records=(
                Atom(
                    id="a2",
                    nucleus=second_atom.nucleus,
                    coordinates=second_atom.coordinates,
                ),
            ),
        ),
    )

    molecule = Molecule.from_fragments(fragments, state=singlet)

    assert molecule.fragments == fragments
    assert emit_job(Job(body=(molecule,))) == (
        "molecule {\n    0 1\n    --\n    0 2\n    H 0 0 0\n"
        "    --\n    0 2\n    H 0 0 2\n}\n"
    )


def test_atom_references_follow_identities_after_reordering() -> None:
    """Resolve a constructed Z-matrix against the current ordered atom records."""
    molecule = read_job("molecule {\nO 0 0 0\nH 0 0 1\nH 0 1 0\n}\n").body[0]
    assert isinstance(molecule, Molecule)
    position = ZMatrix(
        anchors=(
            Anchor(
                atom=AtomReference(atom_id="a1"),
                value=Number(value="0.96"),
            ),
            Anchor(
                atom=AtomReference(atom_id="a2"),
                value=Number(value="104.5"),
            ),
        ),
    )
    changed = molecule.with_coordinates("a3", position)
    reordered = Molecule(
        records=(changed.atoms[1], changed.atoms[0], changed.atoms[2]),
    )

    source = emit_job(Job(body=(reordered,)))

    assert "H 2 0.96 1 104.5" in source
    assert isinstance(molecule.atoms[2].coordinates, Cartesian)
    assert changed.atoms[2].id == "a3"
    with pytest.raises(ValueError, match="Expected one atom"):
        molecule.with_coordinates("missing", position)


def test_schema_describes_every_model_field() -> None:
    """Publish descriptions for fields throughout the recursive JSON Schema."""
    schema = _JSON.validate_python(Job.model_json_schema())  # type: ignore[misc]
    assert isinstance(schema, dict)
    definitions = schema["$defs"]
    assert isinstance(definitions, dict)
    models = [schema, *definitions.values()]
    for model in models:
        if not isinstance(model, dict) or "properties" not in model:
            continue
        fields = model["properties"]
        assert isinstance(fields, dict)
        for name, field in fields.items():
            assert isinstance(field, dict)
            assert field.get("description"), (model.get("title"), name)


def test_coordinate_constraints_are_in_schema() -> None:
    """Describe the exact permitted arities of internal and EFP coordinates."""
    schema = _JSON.validate_python(Job.model_json_schema())  # type: ignore[misc]
    assert isinstance(schema, dict)
    definitions = schema["$defs"]
    assert isinstance(definitions, dict)
    zmatrix = definitions["ZMatrix"]
    assert isinstance(zmatrix, dict)
    fields = zmatrix["properties"]
    assert isinstance(fields, dict)
    anchors = fields["anchors"]
    assert isinstance(anchors, dict)
    assert anchors["maxItems"] == 3


def test_molecule_reader_retains_symmetry_and_shared_parameter_references() -> None:
    """Keep subgroup requests and shared bond definitions through read and edit."""
    job = read_job(
        "molecule water {\nO\nH 1 R\nH 1 R 2 A\n"
        "R=0.96\nA=104.5\nsymmetry c2v\nno_com\nno_reorient\n}\n"
    )
    molecule = job.body[0]
    assert isinstance(molecule, Molecule)
    assert Symmetry(group="c2v") in molecule.records
    changed = molecule.with_variable("R", Number(value="1.1"))
    assert changed.atoms == molecule.atoms
    assert tuple(
        record for record in changed.records if not isinstance(record, GeometryVariable)
    ) == tuple(
        record
        for record in molecule.records
        if not isinstance(record, GeometryVariable)
    )
    for atom in changed.atoms[1:]:
        assert isinstance(atom.coordinates, ZMatrix)
        assert atom.coordinates.anchors[0].value == Variable(name="R")
    restored = Job.model_validate_json(Job(body=(changed,)).model_dump_json())
    assert read_job(emit_job(restored)) == restored


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_template_indentation_can_span_multiple_python_parts(newline: str) -> None:
    """Carry suite indentation across separate Python fragments and native nodes.

    Args:
        newline: Physical line ending in the surrounding Python fragments.
    """
    options = SetOptions(
        assignments=(
            OptionAssignment(key="basis", value=OptionExpression(source="sto-3g")),
        )
    )
    template = PythonTemplate(
        parts=(
            Python(source="if True:" + newline),
            Python(source="  "),
            Python(source="  "),
            options,
            Python(source=newline),
            Python(source=" "),
            Python(source="   "),
            options,
            Python(source=newline + "    pass" + newline),
        )
    )
    source = emit_job(Job(body=(template,)))
    assert source.count("        basis sto-3g") == 2
    assert source.count("    set {") == 2
    assert read_job(source).body
