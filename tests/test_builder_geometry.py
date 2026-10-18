"""Check molecular transformations, selections, and verified coordinate conversion."""

from math import cos, dist, radians, sin
from pathlib import Path

import numpy as np
import pytest
from pydantic import ValidationError

from psi4_parser.builder import (
    Anchor,
    AnchorLayout,
    Angle,
    Atom,
    Bond,
    Cartesian,
    DegenerateGeometryError,
    ElectronicState,
    GeometryParameter,
    IncompatibleCoordinatesError,
    LayoutSearchExhaustedError,
    Length,
    Molecule,
    NamedCoordinate,
    Nucleus,
    Parameter,
    ZMatrix,
    angle,
    angstrom,
    assemble_fragments,
    bohr,
    connected_side,
    degrees,
    dihedral,
    distance,
    positions,
    reorder_atoms,
    rotate,
    set_angle,
    set_dihedral,
    set_distance,
    to_cartesian,
    to_zmatrix,
    translate,
    with_parameter,
)

type CoordinateMatrix = np.ndarray[tuple[int, int], np.dtype[np.float64]]


def _peroxide() -> Molecule:
    return Molecule.from_xyz("4\nPeroxide\nH 1 0 0\nO 0 0 0\nO 0 0 1.4\nH 0 1 1.4\n")


def test_rigid_transform_preserves_identity_and_distances() -> None:
    """Translate and rotate without altering identity, connectivity, or inputs."""
    original = _peroxide()
    changed = (
        original
        | translate((bohr(1), angstrom(2), angstrom(0)))
        | rotate((0.0, 0.0, 1.0), degrees(90))
    )
    before, after = positions(original), positions(changed)
    assert tuple(after) == tuple(before)
    assert changed.atoms[0].nucleus == original.atoms[0].nucleus
    assert after["a2"] == pytest.approx((-2.0, 0.52917721067, 0.0))
    for a in before:
        for b in before:
            assert dist(before[a], before[b]) == pytest.approx(dist(after[a], after[b]))
    assert positions(original)["a1"] == (1.0, 0.0, 0.0)


@pytest.mark.parametrize(
    "target", [-179.0, -90.0, -30.0, 0.0, 45.0, 90.0, 179.0, 270.0]
)
def test_torsion_edit_reaches_target(target: float) -> None:
    """Keep the fixed side unchanged and expose the requested signed torsion.

    Args:
        target: Target angle in degrees, including wraparound.
    """
    original = _peroxide()
    changed = original | set_dihedral(
        ("a1", "a2", "a3", "a4"), degrees(target), moving=("a4",)
    )
    requested = NamedCoordinate(name="D", coordinate=dihedral("a1", "a2", "a3", "a4"))
    internal = to_zmatrix(changed, frame="canonical", requested=(requested,))
    quantity = internal.parameters[0].value
    assert isinstance(quantity, Angle)
    assert quantity.degrees == pytest.approx((target + 180) % 360 - 180)
    for key in ("a1", "a2", "a3"):
        assert positions(changed)[key] == positions(original)[key]


def test_distance_and_angle_edits() -> None:
    """Move the selected endpoint while preserving unrelated atoms."""
    changed = _peroxide() | set_distance(("a2", "a1"), angstrom(1.2), moving=("a1",))
    changed = changed | set_angle(("a1", "a2", "a3"), degrees(120), moving=("a3", "a4"))
    result = to_zmatrix(
        changed,
        frame="canonical",
        requested=(
            NamedCoordinate(name="R", coordinate=distance("a1", "a2")),
            NamedCoordinate(name="A", coordinate=angle("a1", "a2", "a3")),
        ),
    )
    parameters = {p.name: p.value for p in result.parameters}
    length, angular = parameters["R"], parameters["A"]
    assert isinstance(length, Length)
    assert isinstance(angular, Angle)
    assert length.angstroms == pytest.approx(1.2)
    assert angular.degrees == pytest.approx(120)


@pytest.mark.parametrize(
    "moving", [(), ("a1",), ("a1", "a4"), ("missing",), ("a4", "a4")]
)
def test_invalid_moving_selections(moving: tuple[str, ...]) -> None:
    """Reject selections that move references, omit the endpoint, or use bad IDs.

    Args:
        moving: Invalid moving-side selection.
    """
    with pytest.raises(ValueError, match="selection"):
        _peroxide() | set_dihedral(("a1", "a2", "a3", "a4"), degrees(30), moving=moving)


def test_symbolic_cartesian_geometry_requires_explicit_resolution() -> None:
    """Numerical edits must not silently discard parameter relationships."""
    source = Molecule(
        atoms=(
            Atom(
                id="a1",
                nucleus=Nucleus(label="H"),
                coordinates=Cartesian(x=Parameter(name="R"), y=0.0, z=0.0),
            ),
        ),
        parameters=(GeometryParameter(name="R", value=angstrom(1)),),
    )
    with pytest.raises(ValueError, match="to_cartesian"):
        source | translate((angstrom(1), angstrom(0), angstrom(0)))
    changed = source | with_parameter("R", angstrom(2)) | to_cartesian
    assert positions(changed)["a1"] == (2.0, 0.0, 0.0)
    with pytest.raises(ValueError, match="dimension"):
        source | with_parameter("R", degrees(30))


def test_connectivity_selection_rejects_rings() -> None:
    """Traverse an explicit bond graph and reject ambiguous ring cuts."""
    source = _peroxide()
    chain = Molecule(
        atoms=source.atoms,
        bonds=(
            Bond(atoms=("a1", "a2")),
            Bond(atoms=("a2", "a3")),
            Bond(atoms=("a3", "a4")),
        ),
    )
    assert connected_side(chain, "a2", "a3") == ("a3", "a4")
    ring = Molecule(atoms=chain.atoms, bonds=(*chain.bonds, Bond(atoms=("a1", "a4"))))
    with pytest.raises(ValueError, match="ring"):
        connected_side(ring, "a2", "a3")


def test_conversion_frame_and_explicit_layout() -> None:
    """Reject an unrepresentable laboratory frame and allow an explicit layout."""
    source = _peroxide()
    with pytest.raises(IncompatibleCoordinatesError, match="laboratory frame"):
        to_zmatrix(source, frame="preserve")
    layout = (
        AnchorLayout(atom="a1", references=()),
        AnchorLayout(atom="a2", references=("a1",)),
        AnchorLayout(atom="a3", references=("a2", "a1")),
        AnchorLayout(atom="a4", references=("a3", "a2", "a1")),
    )
    internal = to_zmatrix(source, frame="canonical", layout=layout, max_states=0)
    assert tuple(a.id for a in internal.atoms) == tuple(a.id for a in source.atoms)
    roundtrip = to_cartesian(internal)
    for a in source.atoms:
        for b in source.atoms:
            assert dist(
                positions(source)[a.id], positions(source)[b.id]
            ) == pytest.approx(
                dist(positions(roundtrip)[a.id], positions(roundtrip)[b.id]), abs=1e-8
            )


def test_requested_coordinate_can_require_atom_reordering() -> None:
    """Keep stable IDs when reordering to expose a requested torsion."""
    source = _peroxide()
    request = NamedCoordinate(name="D", coordinate=dihedral("a1", "a4", "a3", "a2"))
    with pytest.raises(IncompatibleCoordinatesError, match="ordering"):
        to_zmatrix(source, frame="canonical", requested=(request,))
    changed = source | to_zmatrix(frame="canonical", requested=(request,), reorder=True)
    assert {a.id for a in changed.atoms} == {a.id for a in source.atoms}
    assert tuple(a.id for a in changed.atoms) != tuple(a.id for a in source.atoms)
    with pytest.raises(LayoutSearchExhaustedError, match="budget"):
        to_zmatrix(source, frame="canonical", requested=(request,), max_states=1)


def test_linear_geometry_requires_dummy_opt_in() -> None:
    """Use a dummy reference plane without making undefined requested torsions valid."""
    source = Molecule.from_xyz("4\nLinear\nH 0 0 0\nC 0 0 1\nC 0 0 2\nH 0 0 3\n")
    with pytest.raises(DegenerateGeometryError):
        to_zmatrix(source, frame="canonical")
    result = to_zmatrix(source, frame="canonical", allow_dummies=True)
    assert len(result.atoms) == len(source.atoms) + 1
    assert sum(a.nucleus.dummy for a in result.atoms) == 1
    with pytest.raises(DegenerateGeometryError):
        to_zmatrix(
            source,
            frame="canonical",
            allow_dummies=True,
            requested=(
                NamedCoordinate(name="D", coordinate=dihedral("a1", "a2", "a3", "a4")),
            ),
        )


def test_fragments_keep_states_and_namespaced_atom_ids() -> None:
    """Retain explicit subsystem states without inferring the combined multiplicity."""
    source = _peroxide()
    monomer = Molecule(
        atoms=source.atoms, state=ElectronicState(charge=0, multiplicity=1)
    )
    dimer = assemble_fragments(
        ("left", monomer),
        ("right", monomer),
        state=ElectronicState(charge=0, multiplicity=1),
    )
    assert dimer.fragments[0].state == monomer.state
    assert dimer.fragments[1].atom_ids[0] == "right:a1"
    assert dimer.atoms[0].id == "left:a1"
    assert Molecule.model_validate_json(dimer.model_dump_json()) == dimer
    with pytest.raises(ValueError, match="fragment order"):
        dimer | reorder_atoms(tuple(a.id for a in reversed(dimer.atoms)))


def test_file_import_retains_ghosts_isotopes_and_explicit_bond_perception(
    tmp_path: Path,
) -> None:
    """Read XYZ without inventing connectivity or losing native nucleus labels.

    Args:
        tmp_path: Isolated directory for molecular input.
    """
    path = tmp_path / "hydrogen.xyz"
    path.write_text("2\nHydrogen\n2H 0 0 0\n@H 0 0 0.74\n", encoding="utf-8")
    source = Molecule.from_file(path)
    assert source.atoms[0].nucleus.label == "2H"
    assert source.atoms[1].nucleus.ghost == "at"
    assert source.bonds == ()
    bonded = Molecule.from_xyz(
        "2\nHydrogen\nH 0 0 0\nH 0 0 0.74\n", perceive_bonds=True
    )
    assert len(bonded.bonds) == 1
    with pytest.raises(ValueError, match="one complete"):
        Molecule.from_xyz("1\nOne\nHe 0 0 0\n1\nTwo\nHe 0 0 1\n")


@pytest.mark.parametrize("number", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_geometry_is_rejected(number: float) -> None:
    """Reject nonfinite quantities before numerical work or emission.

    Args:
        number: Nonfinite numerical input.
    """
    with pytest.raises(ValidationError):
        angstrom(number)


def test_reordering_can_avoid_an_unnecessary_dummy() -> None:
    """Find a noncollinear reference plane by reordering atoms."""
    source = Molecule.from_xyz("4\nBent\nC 0 0 0\nC 0 0 1\nC 0 0 2\nH 1 0 1\n")
    result = to_zmatrix(source, frame="canonical", reorder=True)
    assert not any(a.nucleus.dummy for a in result.atoms)
    assert tuple(a.id for a in result.atoms) != tuple(a.id for a in source.atoms)


def test_requested_distances_can_be_incompatible() -> None:
    """Reject three independently named edges of a triangle in one Z-matrix."""
    source = _peroxide()
    requests = tuple(
        NamedCoordinate(name=name, coordinate=distance(*atoms))
        for name, atoms in (
            ("R1", ("a1", "a2")),
            ("R2", ("a2", "a3")),
            ("R3", ("a1", "a3")),
        )
    )
    with pytest.raises(IncompatibleCoordinatesError, match="layout"):
        to_zmatrix(source, frame="canonical", requested=requests, reorder=True)


@pytest.mark.parametrize("tolerance", [0.0, -1.0, float("nan"), float("inf")])
def test_conversion_tolerances_are_finite_and_positive(tolerance: float) -> None:
    """Reject tolerance values that could bypass reconstruction verification.

    Args:
        tolerance: Invalid position tolerance.
    """
    with pytest.raises(ValidationError):
        to_zmatrix(_peroxide(), frame="canonical", position_tolerance=tolerance)


@pytest.mark.parametrize("connect", [False, True])
def test_pdb_connectivity_does_not_require_distance_perception(
    connect: bool, tmp_path: Path
) -> None:
    """Retain CONECT records while leaving distance-based bonding opt-in.

    Args:
        connect: Whether the file explicitly supplies the bond.
        tmp_path: Isolated molecular-file directory.
    """
    path = tmp_path / "hydrogen.pdb"
    source = (
        "HETATM    1  H1  UNK A   1       0.000   0.000   0.000 "
        " 1.00  0.00           H\n"
        "HETATM    2  H2  UNK A   1       0.000   0.000   0.740 "
        " 1.00  0.00           H\n"
    )
    if connect:
        source += "CONECT    1    2\n"
    path.write_text(source + "END\n", encoding="utf-8")
    imported = Molecule.from_file(path)
    assert bool(imported.bonds) == connect
    assert len(Molecule.from_file(path, perceive_bonds=True).bonds) == 1


def test_native_isotope_mass_is_retained_on_import() -> None:
    """Preserve an explicit mass separately from the ghost nucleus label."""
    imported = Molecule.from_xyz("1\nIsotope\n@H@2.014 0 0 0\n")
    assert imported.atoms[0].nucleus.mass == pytest.approx(2.014)
    assert imported.atoms[0].nucleus.label == "H"
    assert imported.atoms[0].nucleus.ghost == "at"


def test_symbolic_water_roundtrip_has_known_cartesian_geometry() -> None:
    """Resolve mixed-unit parameters and recover both requested internal coordinates."""
    water = Molecule(
        atoms=(
            Atom(id="o", nucleus=Nucleus(label="O"), coordinates=ZMatrix()),
            Atom(
                id="h1",
                nucleus=Nucleus(label="H"),
                coordinates=ZMatrix(
                    anchors=(Anchor(atom="o", value=Parameter(name="R")),)
                ),
            ),
            Atom(
                id="h2",
                nucleus=Nucleus(label="H"),
                coordinates=ZMatrix(
                    anchors=(
                        Anchor(atom="o", value=Parameter(name="R")),
                        Anchor(atom="h1", value=Parameter(name="A")),
                    )
                ),
            ),
        ),
        parameters=(
            GeometryParameter(name="R", value=bohr(1.8)),
            GeometryParameter(name="A", value=degrees(104.5)),
        ),
        symmetry="c2v",
    )
    changed = water | with_parameter("R", angstrom(1.1))
    assert changed.atoms == water.atoms
    assert changed.symmetry == water.symmetry
    changed_positions = positions(changed)
    assert dist(changed_positions["o"], changed_positions["h1"]) == pytest.approx(1.1)
    assert dist(changed_positions["o"], changed_positions["h2"]) == pytest.approx(1.1)
    assert Molecule.model_validate_json(changed.model_dump_json()) == changed
    cart = to_cartesian(water)
    assert cart.symmetry == water.symmetry
    length = 0.952518979206
    assert positions(cart)["o"] == (0.0, 0.0, 0.0)
    assert positions(cart)["h1"] == pytest.approx((0.0, 0.0, length))
    assert positions(cart)["h2"] == pytest.approx(
        (0.0, length * sin(radians(104.5)), length * cos(radians(104.5)))
    )
    restored = to_zmatrix(
        cart,
        frame="canonical",
        requested=(
            NamedCoordinate(name="R_out", coordinate=distance("o", "h2")),
            NamedCoordinate(name="A_out", coordinate=angle("h1", "o", "h2")),
        ),
    )
    parameters = {parameter.name: parameter.value for parameter in restored.parameters}
    restored_length, restored_angle = parameters["R_out"], parameters["A_out"]
    assert isinstance(restored_length, Length)
    assert isinstance(restored_angle, Angle)
    assert restored_length.angstroms == pytest.approx(length)
    assert restored_angle.degrees == pytest.approx(104.5)


def test_chiral_tetrahedron_conversion_preserves_handedness() -> None:
    """Preserve a signed tetrahedral volume as well as all pairwise distances."""
    source = Molecule.from_xyz(
        "5\nChiral tetrahedron\nC 0 0 0\nH 1 1 1\nF -1 -1 1\nCl -1 1 -1\nBr 1 -1 -1\n"
    )
    converted = to_cartesian(to_zmatrix(source, frame="canonical"))
    before, after = positions(source), positions(converted)
    corners: CoordinateMatrix = np.asarray(
        tuple(after[key] for key in ("a2", "a3", "a4", "a5")), dtype=np.float64
    )
    edges: CoordinateMatrix = corners[1:] - corners[:1]
    signed_volume = float(np.linalg.det(edges))
    assert signed_volume == pytest.approx(16.0, abs=1e-8)
    for first in before:
        for second in before:
            assert dist(before[first], before[second]) == pytest.approx(
                dist(after[first], after[second]), abs=1e-8
            )


def test_fragment_conversion_retains_states_order_and_isotopes() -> None:
    """Keep fragment metadata and stable IDs across both coordinate representations."""
    singlet = ElectronicState(charge=0, multiplicity=1)
    left = Molecule.from_xyz(
        "2\nIsotopic hydrogen\n2H 0 0 0\nH@2.014 0 0 0.74\n", state=singlet
    )
    right = Molecule.from_xyz("2\nHydrogen\nH 3 0 0\nH 3 0 0.74\n", state=singlet)
    source = assemble_fragments(("left", left), ("right", right), state=singlet)
    converted = to_cartesian(to_zmatrix(source, frame="canonical"))
    assert converted.fragments == source.fragments
    assert converted.state == source.state
    assert tuple(atom.id for atom in converted.atoms) == tuple(
        atom.id for atom in source.atoms
    )
    assert tuple(atom.nucleus for atom in converted.atoms) == tuple(
        atom.nucleus for atom in source.atoms
    )
    before, after = positions(source), positions(converted)
    for first in before:
        for second in before:
            assert dist(before[first], before[second]) == pytest.approx(
                dist(after[first], after[second]), abs=1e-8
            )
