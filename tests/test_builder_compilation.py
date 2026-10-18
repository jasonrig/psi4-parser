"""Check complete Psithon generation, comments, schema, and reference semantics."""

import ast
import json
import os
import subprocess
import warnings
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from pydantic import JsonValue, TypeAdapter, ValidationError

from psi4_parser import format_source, parse
from psi4_parser import job as native
from psi4_parser.builder import (
    PCM,
    Anchor,
    Atom,
    Basis,
    BasisAssignment,
    BasisData,
    BasisLabel,
    Cartesian,
    CFour,
    EFPFragment,
    ElectronicState,
    Expression,
    External,
    ExternalAtom,
    ExternalBasis,
    ExternalSeparator,
    ExternalUnits,
    Fragment,
    GeometryParameter,
    GeometrySource,
    JobSpec,
    Memory,
    Molecule,
    NamedCoordinate,
    Nucleus,
    OptionExpression,
    Parameter,
    PointCharge,
    Python,
    Reference,
    SymmetryChangedWarning,
    XYZHeader,
    ZMatrix,
    angstrom,
    bound,
    call,
    cartesian,
    compose,
    dihedral,
    distance,
    energy,
    freeze,
    frequency,
    gradient,
    hessian,
    lower_job,
    molecule,
    optimize,
    options,
    out_of_plane,
    positions,
    properties,
    render_job,
    set_distance,
    to_zmatrix,
    with_symmetry,
)
from psi4_parser.builder.components import JobComponent

_PYTHON = os.environ.get("PSI4_PYTHON")
_JSON = TypeAdapter(dict[str, JsonValue])


def _geometry() -> Molecule:
    return Molecule.from_xyz("4\nPeroxide\nH 1 0 0\nO 0 0 0\nO 0 0 1.4\nH 0 1 1.4\n")


def _components() -> tuple[JobComponent, ...]:
    return (
        molecule("hooh", _geometry()),
        options(basis="sto-3g", docc=[1, 0], fail_on_maxiter=False),
        Basis(
            name="custom",
            records=(
                BasisAssignment(basis="sto-3g"),
                BasisLabel(name="local"),
                BasisData(text="H 0"),
            ),
        ),
        External(
            records=(
                ExternalUnits(name="angstrom"),
                PointCharge(charge=1.0, position=(0.0, 0.0, 4.0)),
                ExternalAtom(nucleus=Nucleus(label="He"), position=(1.0, 0.0, 4.0)),
                ExternalBasis(role="basis", value="sto-3g"),
                ExternalSeparator(),
            )
        ),
        PCM(body="\nUnits = Angstrom\nMedium { SolverType = IEFPCM }\n"),
        CFour(body="\n# Literal solver data\n*CFOUR(CALC=CCSD)\n"),
        Memory(amount=1.0, units="GiB"),
        energy("uncommon-method", assign=("e", "w"), return_wfn=True, novel_keyword=42),
        call("w.some_uncommon_api", Reference(name="e")),
        Python(source="result = e", provides=("result",)),
    )


def test_every_component_supports_comments_and_json_roundtrips() -> None:
    """Keep annotations attached across all native blocks and Python components."""
    components = _components()
    annotated = tuple(
        component.with_comment(
            f"Component {index}\n\nA researcher's # note \\ path {{x}}"
        )
        for index, component in enumerate(components)
    )
    spec = compose(*annotated)
    assert JobSpec.model_validate_json(spec.model_dump_json()) == spec
    source = render_job(spec)
    assert not parse(source).diagnostics
    assert format_source(source) == source
    for index in range(len(components)):
        assert f"# Component {index}\n#\n# A researcher's # note" in source
    assert "\n\n# Component 1\n" in source
    assert "note \\ path {x}\n\n" not in source
    assert "# Literal solver data" in source


def test_native_adapter_covers_schema_variants() -> None:
    """Fail when a native AST family is added without a builder mapping."""
    schema = _JSON.validate_python(TypeAdapter(native.NativeNode).json_schema())  # type: ignore[misc]  # Pydantic's schema API exposes Any.
    discriminator = schema["discriminator"]
    assert isinstance(discriminator, dict)
    mapping = discriminator["mapping"]
    assert isinstance(mapping, dict)
    lowered = lower_job(compose(*_components()[:7]))
    assert {node.kind for node in lowered.body} == set(mapping)


def test_high_level_schema_rejects_unknown_variants_and_fields() -> None:
    """Validate high-level JSON independently of complete Psi4 syntax."""
    schema = _JSON.validate_python(JobSpec.model_json_schema())  # type: ignore[misc]  # Pydantic's schema API exposes Any.
    validator = Draft202012Validator(schema)
    valid = _JSON.validate_json('{"components":[{"kind":"memory","amount":1.0}]}')
    unknown = _JSON.validate_json('{"components":[{"kind":"unknown"}]}')
    negative = _JSON.validate_json('{"components":[{"kind":"memory","amount":-1}]}')
    assert validator.is_valid(valid)
    assert not validator.is_valid(unknown)
    assert not validator.is_valid(negative)
    with pytest.raises(ValidationError):
        JobSpec.model_validate_json('{"components":[{"kind":"unknown"}]}')
    properties_schema = schema["properties"]
    assert isinstance(properties_schema, dict)
    assert "schema_version" not in properties_schema


@pytest.mark.parametrize(
    "component",
    [
        energy("new-method"),
        gradient("new-method"),
        hessian("new-method"),
        optimize("new-method"),
        frequency("new-method"),
        properties("new-method", properties=["dipole"]),
    ],
)
def test_open_driver_helpers_remain_extensible(component: JobComponent) -> None:
    """Accept all supplied driver families without method catalogues.

    Args:
        component: Driver helper using an unrestricted method name.
    """
    assert not parse(render_job(compose(component))).diagnostics


def test_references_and_assignments_require_explicit_prior_bindings() -> None:
    """Reject unresolved references and duplicates without inserting declarations."""
    with pytest.raises(ValueError, match="follow its declaration"):
        lower_job(compose(energy("scf", molecule=Reference(name="missing"))))
    with pytest.raises(ValueError, match="Duplicate"):
        lower_job(
            compose(Python(source="x = 1", provides=("x",)), call("str", 1, assign="x"))
        )
    with pytest.raises(ValueError, match="reserved"):
        lower_job(compose(call("str", 1, assign="_psi4_builder_options_0")))
    source = render_job(
        compose(
            Python(source="method = 'scf'", provides=("method",)),
            energy(Reference(name="method"), assign=("e", "w"), return_wfn=True),
            call("print", Reference(name="e")),
        )
    )
    assert "e, w = energy(method" in source


def test_expression_parentheses_preserve_argument_boundaries() -> None:
    """Treat tuple expressions as one argument and parenthesize callable expressions."""
    source = render_job(
        compose(
            call("lambda: (lambda x: x)", assign="f"),
            call("f", Expression(source="1, 2")),
        )
    )
    tree = ast.parse(source)
    final = tree.body[-1]
    assert isinstance(final, ast.Expr)
    assert isinstance(final.value, ast.Call)
    assert len(final.value.args) == 1
    assert isinstance(final.value.args[0], ast.Tuple)
    assert not parse(source).diagnostics


def test_geometry_metadata_lowers_without_loss() -> None:
    """Map isotope masses, ghosts, fragments, symbolic anchors, and frame settings."""
    atoms = (
        Atom(
            id="a",
            nucleus=Nucleus(label="13C", mass=13.003, ghost="at"),
            coordinates=ZMatrix(),
        ),
        Atom(
            id="b",
            nucleus=Nucleus(label="H"),
            coordinates=ZMatrix(anchors=(Anchor(atom="a", value=Parameter(name="R")),)),
        ),
    )
    geometry = Molecule(
        atoms=atoms,
        parameters=(GeometryParameter(name="R", value=angstrom(1.1)),),
        fragments=(
            Fragment(
                name="one",
                atom_ids=("a", "b"),
                state=ElectronicState(charge=0, multiplicity=2),
            ),
        ),
        state=ElectronicState(charge=0, multiplicity=2),
        fixed_com=True,
        fixed_orientation=True,
        symmetry="c1",
    )
    result = lower_job(compose(molecule("fragment", geometry))).body[0]
    assert isinstance(result, native.Molecule)
    assert result.atoms[0].nucleus.mass == native.Number(value="13.003")
    assert result.atoms[0].nucleus.ghost == "at"
    source = render_job(compose(molecule("fragment", geometry)))
    assert "no_com" in source
    assert "no_reorient" in source
    assert "R = 1.1" in source


def test_nonatomic_molecule_records_are_representable() -> None:
    """Expose native external geometry, XYZ headers, and EFP placements."""
    inputs = (
        Molecule(sources=(GeometrySource(provider="pubchem", value="water"),)),
        Molecule(atoms=_geometry().atoms, xyz_header=XYZHeader(title="Peroxide")),
        Molecule(
            efp=(
                EFPFragment(
                    id="efp1", name="water", points=((0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
                ),
            )
        ),
    )
    for index, geometry in enumerate(inputs):
        assert not parse(
            render_job(compose(molecule(f"m{index}", geometry)))
        ).diagnostics


def test_constraint_indices_exclude_dummies_and_track_reordering() -> None:
    """Compile stable IDs into optimizer indices separately from Z-matrix indices."""
    atoms = _geometry().atoms
    geometry = Molecule(
        atoms=(
            atoms[3],
            Atom(
                id="dummy",
                nucleus=Nucleus(label="X"),
                coordinates=Cartesian(x=2.0, y=2.0, z=2.0),
            ),
            *atoms[:3],
        )
    )
    declaration = molecule("m", geometry)
    source = render_job(
        compose(
            declaration,
            optimize(
                "scf",
                molecule=declaration.ref,
                constraints=(
                    freeze(dihedral("a1", "a2", "a3", "a4")),
                    bound(distance("a1", "a2"), angstrom(0.8), angstrom(1.2)),
                    freeze(cartesian("a4", "xy")),
                    freeze(out_of_plane("a1", "a2", "a3", "a4")),
                ),
            ),
        )
    )
    assert "'FROZEN_DIHEDRAL', '2 3 4 1'" in source
    assert "'RANGED_DISTANCE', '2 3 0.8 1.2'" in source
    assert "'FROZEN_CARTESIAN', '1 XY'" in source
    assert "'FROZEN_OOFP', '2 3 4 1'" in source


@pytest.mark.parametrize(
    "mode", ["driver", "engine", "raw", "optimizer_keywords", "dummy"]
)
def test_unsupported_constraint_combinations_fail_before_emission(mode: str) -> None:
    """Reject conflicting raw settings and unsupported constraint backends.

    Args:
        mode: Conflict or unsupported combination under test.
    """
    declaration = molecule("m", _geometry())
    constraints = (freeze(distance("a1", "a2")),)
    if mode == "driver":
        component = energy("scf", molecule=declaration.ref, constraints=constraints)
    elif mode == "engine":
        component = optimize(
            "scf", molecule=declaration.ref, constraints=constraints, engine="geometric"
        )
    elif mode == "raw":
        component = optimize(
            "scf",
            molecule=declaration.ref,
            constraints=constraints,
            local_options=(
                options(
                    modules=("optking",), frozen_distance=OptionExpression(source="1 2")
                ),
            ),
        )
    elif mode == "optimizer_keywords":
        component = optimize(
            "scf",
            molecule=declaration.ref,
            constraints=constraints,
            optimizer_keywords={"frozen_distance": "1 2"},
        )
    else:
        component = optimize(
            "scf",
            molecule=declaration.ref,
            constraints=(freeze(distance("a1", "missing")),),
        )
    with pytest.raises(ValueError, match=r"constraint|Constraint|OptKing|optimize"):
        lower_job(compose(declaration, component))


def _reference(source: str, program: str, tmp_path: Path) -> str:
    assert _PYTHON is not None
    result = subprocess.run(  # noqa: S603 - Supplied interpreter; fixed tests instrument all calculation drivers.
        [_PYTHON, "-c", program],
        input=source,
        text=True,
        capture_output=True,
        check=False,
        cwd=tmp_path,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


@pytest.mark.skipif(_PYTHON is None, reason="Set PSI4_PYTHON for reference checks")
def test_comments_preserve_reference_semantics(tmp_path: Path) -> None:
    """Compare real preprocessing with and without attached block comments.

    Args:
        tmp_path: Isolated directory for reference preprocessing.
    """
    declaration = molecule("m", _geometry())
    components = (
        declaration,
        options(basis="sto-3g"),
        energy("novel-method", molecule=declaration.ref),
    )
    plain = render_job(compose(*components))
    annotated = render_job(
        compose(
            *(
                c.with_comment("A researcher's # note\n\nBackslash \\ and braces {}")
                for c in components
            )
        )
    )
    program = """import ast,json,sys,psi4
psi4.core.set_output_file('/dev/null',False)
trees = [
    ast.dump(ast.parse(psi4.process_input(source,print_level=0)),
             include_attributes=False)
    for source in json.loads(sys.stdin.read())
]
assert trees[0] == trees[1]
print('equal')
"""
    inputs: tuple[str, str] = (plain, annotated)
    assert _reference(json.dumps(inputs), program, tmp_path) == "equal"


@pytest.mark.skipif(_PYTHON is None, reason="Set PSI4_PYTHON for reference checks")
@pytest.mark.parametrize("raises", [False, True])
@pytest.mark.parametrize("modules", [(), ("globals",)])
def test_real_option_restoration_on_success_and_failure(
    raises: bool, modules: tuple[str, ...], tmp_path: Path
) -> None:
    """Restore values and changed flags after an instrumented driver returns or raises.

    Args:
        raises: Whether the instrumented calculation raises an exception.
        modules: Empty global scope or the explicit GLOBALS alias.
        tmp_path: Isolated directory for reference execution.
    """
    declaration = molecule("m", _geometry())
    spec = compose(
        declaration,
        options(modules=("scf",), maxiter=37),
        optimize(
            "scf",
            molecule=declaration.ref,
            local_options=(
                options(modules=("scf",), maxiter=5),
                options(modules=modules, basis="sto-3g"),
            ),
            constraints=(freeze(distance("a1", "a2")),),
        ),
    )
    program = """import json,sys,psi4
psi4.core.set_output_file('/dev/null',False)
source = sys.stdin.read()
initial = (
    psi4.core.get_global_option('BASIS'),
    psi4.core.has_global_option_changed('BASIS'),
    psi4.core.get_local_option('OPTKING','FROZEN_DISTANCE'),
    psi4.core.has_local_option_changed('OPTKING','FROZEN_DISTANCE'),
)
def instrumented(*args,**kwargs):
    assert psi4.core.get_option('SCF','MAXITER') == 5
    assert psi4.core.get_option('OPTKING','FROZEN_DISTANCE') == '1 2'
    assert psi4.core.get_global_option('BASIS') == 'STO-3G'
    if RAISES:
        raise RuntimeError('instrumented failure')
    return 0.0
psi4.optimize = instrumented
try:
    exec(compile(psi4.process_input(source,print_level=0),'<generated>','exec'),{})
except RuntimeError as error:
    assert RAISES and str(error) == 'instrumented failure'
assert psi4.core.get_option('SCF','MAXITER') == 37
final = (
    psi4.core.get_global_option('BASIS'),
    psi4.core.has_global_option_changed('BASIS'),
    psi4.core.get_local_option('OPTKING','FROZEN_DISTANCE'),
    psi4.core.has_local_option_changed('OPTKING','FROZEN_DISTANCE'),
)
assert initial == final,(initial,final)
print('restored')
""".replace("RAISES", repr(raises))
    assert _reference(render_job(spec), program, tmp_path) == "restored"


@pytest.mark.skipif(_PYTHON is None, reason="Set PSI4_PYTHON for reference checks")
def test_literal_values_survive_real_psithon_rewriting(tmp_path: Path) -> None:
    """Retain hashes, slashes, quotes, line breaks, and reserved namespace text.

    Args:
        tmp_path: Isolated reference process directory.
    """
    literals = (
        "a#b",
        "a\\#b",
        "researcher's # title",
        "first\n# second",
        "psi4.Matrix",
        "psi_hartree2kcalmol",
        "\\psi4.Matrix",
        '"quoted"',
    )
    sources = tuple(
        render_job(compose(call("capture", literal))) for literal in literals
    )
    program = """import ast,json,sys,psi4
psi4.core.set_output_file('/dev/null',False)
sources,expected = json.loads(sys.stdin.read())
for source,literal in zip(sources,expected,strict=True):
    tree = ast.parse(psi4.process_input(source,print_level=0))
    calls = [node for node in ast.walk(tree) if isinstance(node,ast.Call)
             and isinstance(node.func,ast.Name) and node.func.id == 'capture']
    assert len(calls) == 1
    assert calls[0].args[0].value == literal,(source,calls[0].args[0].value,literal)
print('preserved')
"""
    assert _reference(json.dumps((sources, literals)), program, tmp_path) == "preserved"


@pytest.mark.skipif(_PYTHON is None, reason="Set PSI4_PYTHON for reference checks")
def test_converted_geometry_matches_real_psi4_placement(tmp_path: Path) -> None:
    """Match the real reader through proper frame changes without reflection.

    Args:
        tmp_path: Isolated reference process directory.
    """
    internal = to_zmatrix(
        _geometry(),
        frame="canonical",
        requested=(
            NamedCoordinate(name="D", coordinate=dihedral("a1", "a2", "a3", "a4")),
        ),
    )
    frame_directives: dict[str, bool] = {"fixed_com": True, "fixed_orientation": True}
    internal = internal.model_copy(update=frame_directives)
    source = render_job(compose(molecule("m", internal)))
    expected = tuple(positions(internal).values())
    program = """import json,sys,psi4
import numpy as np
psi4.core.set_output_file('/dev/null',False)
source,expected = json.loads(sys.stdin.read())
namespace = {}
exec(compile(psi4.process_input(source,print_level=0),'<generated>','exec'),namespace)
geometry = namespace['m'].full_geometry().to_array()*psi4.constants.bohr2angstroms
expected = np.asarray(expected)
distances = np.linalg.norm(geometry[:,None]-geometry[None,:],axis=-1)
expected_distances = np.linalg.norm(expected[:,None]-expected[None,:],axis=-1)
assert np.allclose(distances,expected_distances,atol=1e-8,rtol=0)
def volume(points):
    return np.linalg.det(points[1:]-points[:1])
assert abs(volume(geometry)-volume(expected)) < 1e-8
print('matched')
"""
    assert _reference(json.dumps((source, expected)), program, tmp_path) == "matched"


def test_step_local_option_comments_retain_scope() -> None:
    """Emit attached local-option comments inside the generated try suite."""
    source = render_job(
        compose(
            energy(
                "scf",
                local_options=(options(basis="sto-3g").with_comment("Local basis"),),
            )
        )
    )
    assert "    # Local basis\n    set {" in source


@pytest.mark.skipif(_PYTHON is None, reason="Set PSI4_PYTHON for reference checks")
@pytest.mark.parametrize(
    ("xyz", "symmetry", "full_group", "computational_group"),
    [
        pytest.param(
            "3\nWater\nO 0 0 0\nH 0 0.757 0.586\nH 0 -0.757 0.586\n",
            "c2v",
            "C2v",
            "c2v",
            id="water-explicit-c2v",
        ),
        pytest.param(
            "5\nMethane\nC 0 0 0\nH 1 1 1\nH -1 -1 1\nH -1 1 -1\nH 1 -1 -1\n",
            None,
            "Td",
            "c2v",
            id="methane-automatic-subgroup",
        ),
        pytest.param(
            "3\nCarbon dioxide\nO 0 0 -1.16\nC 0 0 0\nO 0 0 1.16\n",
            "c1",
            "D_inf_h",
            "c1",
            id="linear-co2-computational-c1",
        ),
    ],
)
def test_symmetric_conversion_and_psi4_subgroup_requests(
    xyz: str,
    symmetry: str | None,
    full_group: str,
    computational_group: str,
    tmp_path: Path,
) -> None:
    """Preserve symmetric geometry and honor native point-group requests.

    Args:
        xyz: Symmetric Cartesian geometry with labelled atom order.
        symmetry: Explicit computational subgroup or automatic detection.
        full_group: Expected full molecular point group.
        computational_group: Expected Psi4 computational subgroup.
        tmp_path: Isolated directory for the real molecule reader.
    """
    original = Molecule(atoms=Molecule.from_xyz(xyz).atoms, symmetry=symmetry)
    internal = to_zmatrix(original, frame="canonical")
    assert internal.symmetry == symmetry
    assert tuple(atom.id for atom in internal.atoms) == tuple(
        atom.id for atom in original.atoms
    )
    sources = tuple(
        render_job(compose(molecule("m", geometry)))
        for geometry in (original, internal)
    )
    for source in sources:
        if symmetry is None:
            assert "symmetry " not in source
        else:
            assert f"symmetry {symmetry}" in source
    expected_positions = tuple(positions(original).values())
    program = """import json,sys,psi4
import numpy as np
psi4.core.set_output_file('/dev/null',False)
sources,expected,full_group,computational_group = json.loads(sys.stdin.read())
for source in sources:
    namespace = {}
    exec(compile(psi4.process_input(source,print_level=0),'<symmetry>','exec'),namespace)
    molecule = namespace['m']
    molecule.update_geometry()
    assert molecule.get_full_point_group() == full_group
    assert molecule.schoenflies_symbol() == computational_group
    assert molecule.natom() == len(expected)
    geometry = molecule.geometry().to_array()*psi4.constants.bohr2angstroms
    expected_geometry = np.asarray(expected)
    distances = np.linalg.norm(geometry[:,None]-geometry[None,:],axis=-1)
    expected_distances = np.linalg.norm(
        expected_geometry[:,None]-expected_geometry[None,:],axis=-1
    )
    assert np.allclose(distances,expected_distances,atol=1e-8,rtol=0)
print('preserved')
"""
    payload = json.dumps((sources, expected_positions, full_group, computational_group))
    assert _reference(payload, program, tmp_path) == "preserved"


@pytest.mark.skipif(_PYTHON is None, reason="Set PSI4_PYTHON for reference checks")
@pytest.mark.parametrize("intentional", [False, True])
def test_relaxed_symmetry_is_accepted_by_real_molecule_reader(
    intentional: bool, tmp_path: Path
) -> None:
    """Read every atom after automatic or intentional computational symmetry lowering.

    Args:
        intentional: Select C1 explicitly instead of retaining a residual mirror plane.
        tmp_path: Isolated directory for the real Psi4 reader.
    """
    geometry = Molecule.from_xyz(
        "3\nWater\nO 0 0 0\nH 0 .757 .586\nH 0 -.757 .586\n"
    ) | with_symmetry("c2v")
    if intentional:
        geometry = geometry | with_symmetry("c1")
    target = angstrom(1.2 if intentional else 0.9573113891159639)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", SymmetryChangedWarning)
        changed = geometry | set_distance(("a1", "a2"), target, moving=("a2",))
    if intentional:
        assert not caught
    else:
        assert caught
        assert len(caught) == 1
    source = render_job(compose(molecule("m", changed)))
    program = """import json,sys,psi4
psi4.core.set_output_file('/dev/null',False)
source,group = json.loads(sys.stdin.read())
namespace = {}
exec(compile(psi4.process_input(source,print_level=0),'<symmetry>','exec'),namespace)
m = namespace['m']
m.update_geometry()
assert m.natom() == 3
assert m.symmetry_from_input() == group
assert m.schoenflies_symbol() == group
print('accepted')
"""
    assert (
        _reference(json.dumps((source, changed.symmetry)), program, tmp_path)
        == "accepted"
    )
