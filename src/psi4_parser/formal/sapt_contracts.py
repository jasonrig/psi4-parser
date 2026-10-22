"""Check explicit SAPT partitions and state choices before native construction."""

from typing import Literal

from psi4_parser.builder import Molecule
from psi4_parser.formal.models import Calculation, Diagnostic


def _finding(
    path: tuple[str | int, ...],
    code: str,
    message: str,
    status: Literal["violated", "unknown", "unsupported"] = "violated",
) -> Diagnostic:
    return Diagnostic(path=path, code=code, message=message, status=status)


def _partition_issues(
    step: Calculation, molecule: Molecule, path: tuple[str | int, ...]
) -> tuple[Diagnostic, ...]:
    analysis = step.sapt
    if analysis is None:
        return ()
    expected: tuple[str, ...] = analysis.fragments
    if analysis.midbond_fragment is not None:
        expected += (analysis.midbond_fragment,)
    if tuple(fragment.name for fragment in molecule.fragments) != expected:
        return (
            _finding(
                path,
                "sapt_fragments",
                "SAPT needs its real fragments in A/B order, followed only "
                "by the optional midbond fragment.",
            ),
        )
    atoms = {atom.id: atom for atom in molecule.atoms}
    issues: list[Diagnostic] = []
    for fragment in molecule.fragments:
        selected = [atoms[name] for name in fragment.atom_ids if name in atoms]
        midbond = fragment.name == analysis.midbond_fragment
        if any(atom.nucleus.dummy for atom in selected):
            issues.append(
                _finding(
                    path,
                    "sapt_dummy",
                    "Resolve dummy centers before SAPT construction.",
                    "unsupported",
                )
            )
        if not selected or any(
            (atom.nucleus.ghost != "none") != midbond for atom in selected
        ):
            issues.append(
                _finding(
                    path,
                    "sapt_centers",
                    "SAPT monomers require real nuclei; the midbond fragment "
                    "requires only ghost centers.",
                )
            )
        if (
            midbond
            and fragment.state is not None
            and (fragment.state.charge != 0 or fragment.state.multiplicity != 1)
        ):
            issues.append(
                _finding(
                    path,
                    "sapt_midbond_state",
                    "A midbond fragment requires charge zero and multiplicity one.",
                )
            )
    return tuple(issues)


def _state_issues(
    step: Calculation, molecule: Molecule, path: tuple[str | int, ...]
) -> tuple[Diagnostic, ...]:
    analysis = step.sapt
    if analysis is None:
        return ()
    monomers = {fragment.name: fragment.state for fragment in molecule.fragments}
    states = tuple(monomers.get(name) for name in analysis.fragments)
    if any(state is None for state in states) or molecule.state is None:
        return (
            _finding(
                path,
                "sapt_state",
                "Supply both monomer states and the complex state explicitly.",
                "unknown",
            ),
        )
    resolved = tuple(state for state in states if state is not None)
    issues: list[Diagnostic] = []
    if step.model.reference == "rhf" and any(
        state.multiplicity != 1 for state in resolved
    ):
        issues.append(
            _finding(
                path, "sapt_reference", "RHF SAPT requires two closed-shell monomers."
            )
        )
    if (
        molecule.state.multiplicity
        != sum(state.multiplicity - 1 for state in resolved) + 1
    ):
        issues.append(
            _finding(
                path,
                "sapt_high_spin",
                "Use the high-spin coupling of the SAPT monomer states.",
            )
        )
    if step.model.reference == "rohf" and analysis.coupled_induction:
        issues.append(
            _finding(
                path,
                "sapt_induction",
                "ROHF SAPT requires an explicit uncoupled-induction request.",
            )
        )
    return tuple(issues)


def sapt_issues(
    step: Calculation, molecule: Molecule, path: tuple[str | int, ...]
) -> tuple[Diagnostic, ...]:
    """Check native SAPT choices and required explicit fitting information.

    Returns:
        Located partition, state, operation, setting, or missing-fitting findings.
    """
    if step.sapt is None:
        return ()
    location = (*path, "sapt")
    issues = [
        *_partition_issues(step, molecule, location),
        *_state_issues(step, molecule, location),
    ]
    if step.driver != "energy" or step.analysis is not None:
        issues.append(
            _finding(
                location,
                "sapt_driver",
                "SAPT requires the scalar energy driver and its own context.",
                "unsupported",
            )
        )
    reserved = {
        "sapt_level",
        "coupled_induction",
        "do_third_order",
        "do_ccd_disp",
        "sapt0_e10",
        "sapt0_e20ind",
        "sapt0_e20disp",
    }
    if any(
        setting.key[0] in {"", "sapt"} and setting.key[1] in reserved
        for setting in step.model.settings
    ):
        issues.append(
            _finding(
                location,
                "sapt_settings",
                "Use the method and SAPT analysis fields for level, induction, "
                "and complete-component routing.",
            )
        )
    roles = {item.role.casefold() for item in step.model.auxiliary_bases}
    required = {"df_basis_sapt", "df_basis_elst"}
    if any(
        setting.key == ("", "scf_type")
        and isinstance(setting.value, str)
        and setting.value.casefold() == "df"
        for setting in step.model.settings
    ):
        required.add("df_basis_scf")
    if missing := sorted(required - roles):
        issues.append(
            _finding(
                location,
                "sapt_fitting",
                f"Supply explicit SAPT fitting bases for: {', '.join(missing)}.",
                "unknown",
            )
        )
    return tuple(issues)
