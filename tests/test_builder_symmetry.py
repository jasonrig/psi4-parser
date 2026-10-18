"""Check explicit symmetry, geometric edits, and full point-group detection."""

import warnings

import pytest

from psi4_parser.builder import (
    Atom,
    Cartesian,
    GeometryExpression,
    GeometryParameter,
    Molecule,
    Nucleus,
    Parameter,
    SymmetryChangedWarning,
    angstrom,
    compose,
    degrees,
    detect_point_group,
    molecule,
    render_job,
    rotate,
    set_distance,
    to_cartesian,
    to_zmatrix,
    translate,
    with_parameter,
    with_symmetry,
)


def _water() -> Molecule:
    imported = Molecule.from_xyz(
        "3\nWater\nO 0 0 0\nH 0 0.757 0.586\nH 0 -0.757 0.586\n"
    )
    return Molecule(atoms=imported.atoms, symmetry="c2v")


@pytest.mark.parametrize(
    ("xyz", "expected"),
    [
        ("3\nWater\nO 0 0 0\nH 0 .757 .586\nH 0 -.757 .586\n", "C2v"),
        ("5\nMethane\nC 0 0 0\nH 1 1 1\nH -1 -1 1\nH -1 1 -1\nH 1 -1 -1\n", "Td"),
        ("3\nHDO\nO 0 0 0\n2H 0 .757 .586\nH 0 -.757 .586\n", "Cs"),
    ],
)
def test_point_group_detection_keeps_original_geometry(xyz: str, expected: str) -> None:
    """Detect full point groups without adopting backend coordinate changes.

    Args:
        xyz: Complete geometry, including an isotopically substituted case.
        expected: Expected full molecular point-group symbol.
    """
    original = Molecule.from_xyz(xyz)
    before = original.model_dump_json()
    assert detect_point_group(original) == expected
    rotated = original | rotate((1.0, 2.0, 3.0), degrees(37))
    assert detect_point_group(rotated) == expected
    assert original.model_dump_json() == before


def test_broken_request_warns_and_adopts_residual_symmetry() -> None:
    """Stretch one water bond, retaining its mirror plane and all atom records."""
    original = _water()
    with pytest.warns(SymmetryChangedWarning, match="c2v.*cs"):
        changed = original | set_distance(("a1", "a2"), angstrom(1.2), moving=("a2",))
    assert original.symmetry == "c2v"
    assert changed.symmetry == "cs"
    assert tuple(atom.id for atom in changed.atoms) == tuple(
        atom.id for atom in original.atoms
    )
    assert tuple(atom.nucleus for atom in changed.atoms) == tuple(
        atom.nucleus for atom in original.atoms
    )
    source = render_job(compose(molecule("water", changed)))
    assert "symmetry cs" in source
    assert len(to_cartesian(changed).atoms) == 3


def test_explicit_relaxation_is_a_quiet_pipeline_stage() -> None:
    """Choose C1 before editing while retaining the complete specification."""
    original = _water()
    relaxed = original | with_symmetry("c1")
    assert relaxed.atoms == original.atoms
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        changed = relaxed | set_distance(("a1", "a2"), angstrom(1.2), moving=("a2",))
    assert not caught
    assert changed.symmetry == "c1"
    assert (changed | with_symmetry(None)).symmetry is None
    assert Molecule.model_validate_json(changed.model_dump_json()) == changed


def test_rigid_motion_and_conversion_keep_symmetry_quietly() -> None:
    """Retain a request through arbitrary rigid motion and canonical conversion."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        changed = (
            _water()
            | rotate((1.0, 2.0, 3.0), degrees(37))
            | translate((angstrom(2), angstrom(-1), angstrom(3)))
            | to_zmatrix(frame="canonical")
            | to_cartesian
        )
    assert changed.symmetry == "c2v"
    assert not caught


def test_explicit_selection_rejects_an_incompatible_group() -> None:
    """Check an intentional subgroup selection before changing the request."""
    with pytest.raises(ValueError, match="symmetry"):
        _water() | with_symmetry("d2h")
    with pytest.raises(ValueError, match="symmetry"):
        _water() | with_symmetry("td")


def test_symmetry_check_is_stricter_than_full_detector_tolerance() -> None:
    """Detect a mismatch below the general detector's 1e-6-angstrom tolerance."""
    with pytest.warns(SymmetryChangedWarning, match="c2v.*cs"):
        changed = _water() | set_distance(
            ("a1", "a2"), angstrom(0.9573113891159639), moving=("a2",)
        )
    assert changed.symmetry == "cs"
    assert detect_point_group(changed) == "C2v"


def test_loss_of_all_symmetry_adopts_c1() -> None:
    """Remove peroxide's twofold rotation without introducing a mirror plane."""
    original = Molecule.from_xyz(
        "4\nPeroxide\nH 1 0 0\nO 0 0 0\nO 0 0 1.4\nH 0 1 1.4\n"
    ) | with_symmetry("c2")
    with pytest.warns(SymmetryChangedWarning, match="c2.*c1"):
        changed = original | set_distance(("a2", "a1"), angstrom(1.2), moving=("a1",))
    assert changed.symmetry == "c1"
    assert tuple(atom.id for atom in changed.atoms) == tuple(
        atom.id for atom in original.atoms
    )


@pytest.mark.parametrize("substitution", ["2H", "H@2.014", "@H"])
def test_symmetry_selection_distinguishes_isotopes_masses_and_ghosts(
    substitution: str,
) -> None:
    """Keep spatially equivalent sites distinct when their nuclear roles differ.

    Args:
        substitution: Isotopic label, custom isotope mass, or ghost center.
    """
    geometry = Molecule.from_xyz(
        f"3\nSubstituted water\nO 0 0 0\n{substitution} 0 .757 .586\nH 0 -.757 .586\n"
    )
    with pytest.raises(ValueError, match="symmetry"):
        geometry | with_symmetry("c2v")
    selected = geometry | with_symmetry("cs")
    assert selected.symmetry == "cs"
    assert selected.atoms == geometry.atoms


def test_fixed_axis_request_is_relaxed_after_rotation() -> None:
    """Honor laboratory axes rather than validating only an abstract group name."""
    original = _water()
    fixed = Molecule(atoms=original.atoms, fixed_orientation=True) | with_symmetry(
        "c2vz"
    )
    with pytest.warns(SymmetryChangedWarning, match="c2vz.*c1"):
        changed = fixed | rotate((1.0, 2.0, 3.0), degrees(37))
    assert changed.symmetry == "c1"
    assert changed.fixed_orientation


def test_unresolved_parameter_edit_warns_without_losing_references() -> None:
    """Use C1 when a new symbolic value prevents verification of a request."""
    original = Molecule(
        atoms=(
            Atom(
                id="h",
                nucleus=Nucleus(label="H"),
                coordinates=Cartesian(x=Parameter(name="R"), y=0.0, z=0.0),
            ),
        ),
        parameters=(GeometryParameter(name="R", value=angstrom(0)),),
        symmetry="d2h",
    )
    with pytest.warns(SymmetryChangedWarning, match="unresolved.*c1"):
        changed = original | with_parameter("R", GeometryExpression(source="TDA"))
    assert changed.symmetry == "c1"
    assert changed.atoms == original.atoms
    assert changed.parameters[0].value == GeometryExpression(source="TDA")


def test_linear_point_group_and_dummy_references() -> None:
    """Identify linear symmetry while excluding inserted Z-matrix reference atoms."""
    linear = Molecule.from_xyz("4\nLinear\nH 0 0 0\nC 0 0 1\nC 0 0 2\nH 0 0 3\n")
    internal = to_zmatrix(linear, frame="canonical", allow_dummies=True)
    assert len(internal.atoms) > len(linear.atoms)
    assert detect_point_group(linear) == "Dinfh"
    assert detect_point_group(internal) == "Dinfh"


def test_full_detection_retains_custom_masses_and_rejects_ambiguous_roles() -> None:
    """Retain custom masses and reject ambiguous ghost roles."""
    isotope = Molecule.from_xyz(
        "3\nHDO\nO 0 0 0\nH@2.014 0 .757 .586\nH 0 -.757 .586\n"
    )
    assert detect_point_group(isotope) == "Cs"
    ghost = Molecule.from_xyz(
        "3\nGhost water\nO 0 0 0\n@H 0 .757 .586\nH 0 -.757 .586\n"
    )
    with pytest.raises(ValueError, match="ghost roles"):
        detect_point_group(ghost)
