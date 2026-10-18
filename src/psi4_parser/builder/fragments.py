"""Assemble named molecular fragments without inferring their electronic states."""

from psi4_parser.builder._model import evolve
from psi4_parser.builder.molecular import (
    Anchor,
    Atom,
    Bond,
    Cartesian,
    CartesianValue,
    ElectronicState,
    Fragment,
    GeometryParameter,
    Molecule,
    Parameter,
    ZMatrix,
)
from psi4_parser.builder.symmetry import reconcile_symmetry


def _namespace(atom: Atom, prefix: str, parameters: set[str]) -> Atom:
    def parameter(value: CartesianValue) -> CartesianValue:
        return (
            evolve(value, name=prefix + "_" + value.name)
            if isinstance(value, Parameter) and value.name in parameters
            else value
        )

    coordinates = atom.coordinates
    if isinstance(coordinates, Cartesian):
        coordinates = evolve(
            coordinates,
            x=parameter(coordinates.x),
            y=parameter(coordinates.y),
            z=parameter(coordinates.z),
        )
    else:
        anchors = tuple(
            Anchor(
                atom=prefix + ":" + a.atom,
                value=evolve(a.value, name=prefix + "_" + a.value.name)
                if isinstance(a.value, Parameter) and a.value.name in parameters
                else a.value,
            )
            for a in coordinates.anchors
        )
        coordinates = ZMatrix(anchors=anchors)
    return evolve(atom, id=prefix + ":" + atom.id, coordinates=coordinates)


def assemble_fragments(
    *parts: tuple[str, Molecule], state: ElectronicState | None = None
) -> Molecule:
    """Return a molecular assembly with namespaced identities and explicit states.

    Nested fragment states cannot represent an additional subsystem-wide state
    in Psithon; such inputs must be flattened explicitly by the caller.

    Raises:
        ValueError: Fragment names, states, sources, or frame directives conflict.
    """
    if (
        not parts
        or len({name for name, _ in parts}) != len(parts)
        or any(not name for name, _ in parts)
    ):
        raise ValueError("Fragment assembly requires distinct nonempty names")
    atoms: list[Atom] = []
    bonds: list[Bond] = []
    fragments: list[Fragment] = []
    parameters: list[GeometryParameter] = []
    for name, part in parts:
        if part.sources or part.efp:
            raise ValueError("Fragment assembly requires resolved atom specifications")
        if part.fragments and part.state is not None:
            raise ValueError(
                "Flatten nested fragments with subsystem-wide "
                "electronic states explicitly"
            )
        parameter_names = {p.name for p in part.parameters}
        atoms.extend(_namespace(a, name, parameter_names) for a in part.atoms)
        bonds.extend(
            evolve(b, atoms=(name + ":" + b.atoms[0], name + ":" + b.atoms[1]))
            for b in part.bonds
        )
        parameters.extend(evolve(p, name=name + "_" + p.name) for p in part.parameters)
        members = part.fragments or (
            Fragment(
                name=name, atom_ids=tuple(a.id for a in part.atoms), state=part.state
            ),
        )
        fragments.extend(
            evolve(
                f,
                name=name + ":" + f.name if part.fragments else name,
                atom_ids=tuple(name + ":" + a for a in f.atom_ids),
            )
            for f in members
        )
    first = parts[0][1]
    if any(
        (part.fixed_com, part.fixed_orientation, part.symmetry)
        != (first.fixed_com, first.fixed_orientation, first.symmetry)
        for _, part in parts
    ):
        raise ValueError("Fragment frame and symmetry directives must agree")
    result = Molecule(
        atoms=tuple(atoms),
        bonds=tuple(bonds),
        fragments=tuple(fragments),
        state=state,
        parameters=tuple(parameters),
        fixed_com=first.fixed_com,
        fixed_orientation=first.fixed_orientation,
        symmetry=first.symmetry,
    )
    return reconcile_symmetry(result)
