"""Check full-basis fragment identities and ghost assignments before execution."""

from psi4_parser import validate
from psi4_parser.builder import ElectronicState, Molecule, assemble_fragments, molecule
from psi4_parser.formal import (
    CapabilityCatalog,
    Plan,
    ScientificRequest,
    SubsystemGoal,
    propose,
    render,
    verify,
)


def test_full_basis_subsystem_retains_the_parent_coordinate_source() -> None:
    """Construct a monomer in the dimer basis without inventing new coordinates."""
    helium = Molecule.from_xyz(
        "1\nHe\nHe 0 0 0\n", state=ElectronicState(charge=0, multiplicity=1)
    )
    partner = Molecule.from_xyz(
        "1\nHe\nHe 0 0 3\n", state=ElectronicState(charge=0, multiplicity=1)
    )
    assembly = assemble_fragments(
        ("A", helium), ("B", partner), state=ElectronicState(charge=0, multiplicity=1)
    )
    # Fixed frame is explicit for parent and subsystem coordinates.
    assembly = Molecule(
        atoms=assembly.atoms,
        fragments=assembly.fragments,
        state=assembly.state,
        fixed_com=True,
        fixed_orientation=True,
    )
    declaration = molecule("dimer", assembly).model_dump_json()
    source = """{
      "molecules": [],
      "steps": [
        {"kind":"subsystem", "id":"monomer_a", "geometry":"dimer",
         "real_fragments":["A"], "state":{"charge":0,"multiplicity":1}},
        {"kind":"calculation", "id":"a", "driver":"energy", "geometry":"monomer_a",
         "model":{"method":"scf","basis":"sto-3g","reference":"rhf"}}
      ],
      "requirements":[{"kind":"uses_geometry","calculation":"a","geometry":"monomer_a"}]
    }"""
    plan = Plan.model_validate_json(
        source.replace('"molecules": []', f'"molecules": [{declaration}]')
    )

    report = verify(plan)
    generated = render(plan)

    assert report.status == "proved"
    assert report.geometries[1].source == "dimer"
    assert report.quantities[0].system == "monomer_a"
    assert "set_ghost_fragment" in generated
    assert validate(generated) == ()


def test_a_request_without_any_calculation_is_reported_invalid(
    formal_profile: CapabilityCatalog,
) -> None:
    """Explain a geometry-only request instead of crashing while building a plan.

    Args:
        formal_profile: Synthetic capability declarations.
    """
    geometry = Molecule.from_xyz(
        "2\nH2\nH 0 0 0\nH 0 0 .85\n", state=ElectronicState(charge=0, multiplicity=1)
    )
    request = ScientificRequest(
        molecules=(molecule("h2", geometry),),
        goals=(
            SubsystemGoal(
                id="part",
                geometry="h2",
                real_fragments=("A",),
                state=ElectronicState(charge=0, multiplicity=1),
            ),
        ),
    )

    proposal = propose(request, formal_profile)

    assert proposal.status == "invalid"
    assert proposal.diagnostics[0].code == "request_calculation"
