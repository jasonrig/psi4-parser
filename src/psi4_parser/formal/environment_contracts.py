"""Check solvent construction and vertical electronic solvation differences."""

from fractions import Fraction

from psi4_parser.builder import Molecule
from psi4_parser.formal.algebra import Form
from psi4_parser.formal.models import Calculation, Diagnostic, Plan, Step
from psi4_parser.formal.science import ExpectedQuantity

_SOLVATION_TERMS = 2


def environment_assumptions(plan: Plan) -> tuple[str, ...]:
    """Return the physical assumptions attached to explicit solvent construction."""
    if not any(
        isinstance(step, Calculation) and step.model.environment is not None
        for step in plan.steps
    ):
        return ()
    return (
        "Equilibrium continuum equations, dielectric values, cavity choices, "
        "and discretization are scientific inputs. An electronic "
        "solvation shift omits thermal, non-electrostatic, and standard-state terms.",
    )


def environment_issues(
    step: Calculation, molecule: Molecule, path: tuple[str | int, ...]
) -> tuple[Diagnostic, ...]:
    """Locate unsupported solvent drivers or ambiguous cavity centers.

    Returns:
        Scientific input findings, independent of runtime installation metadata.
    """
    environment = step.model.environment
    if environment is None:
        return ()
    location = (*path, "model", "environment")
    issues: list[Diagnostic] = []
    if (
        step.driver != "energy"
        or step.sapt is not None
        or step.analysis is not None
        or step.model.tdscf is not None
    ):
        issues.append(
            Diagnostic(
                path=location,
                code="solvent_driver",
                status="unsupported",
                message="Equilibrium solvent construction currently requires "
                "an ordinary energy call.",
            )
        )
    if any(
        atom.nucleus.ghost != "none" or atom.nucleus.dummy for atom in molecule.atoms
    ):
        issues.append(
            Diagnostic(
                path=location,
                code="solvent_cavity_centers",
                status="unsupported",
                message="The implicit solvent cavity contract requires real nuclei "
                "without dummy centers.",
            )
        )
    if environment.kind == "pcm" and step.model.reference == "rohf":
        issues.append(
            Diagnostic(
                path=(*path, "model", "reference"),
                code="solvent_reference",
                status="unsupported",
                message="The reviewed PCMSolver contract covers "
                "RHF and UHF references.",
            )
        )
    return tuple(issues)


def solvation_shift_issues(
    steps: dict[str, Step],
    form: Form,
    quantities: dict[str, ExpectedQuantity],
    path: tuple[str | int, ...],
) -> tuple[Diagnostic, ...]:
    """Require one solvated minus one vacuum energy at the same geometry.

    Returns:
        Located formula, geometry/state, or electronic-treatment disagreements.
    """
    sources: list[tuple[Calculation, Fraction]] = []
    for leaf, coefficient in form.items():
        source = steps[leaf]
        if (
            not isinstance(source, Calculation)
            or quantities[leaf].quantity.meaning != "electronic_energy"
        ):
            return (
                Diagnostic(
                    path=path,
                    code="solvation_formula",
                    message="Use two primary electronic energies "
                    "for the solvation shift.",
                ),
            )
        sources.append((source, coefficient))
    solvated = [
        item
        for item, weight in sources
        if item.model.environment is not None and weight == 1
    ]
    vacuum = [
        item
        for item, weight in sources
        if item.model.environment is None and weight == -1
    ]
    if len(sources) != _SOLVATION_TERMS or len(solvated) != 1 or len(vacuum) != 1:
        return (
            Diagnostic(
                path=path,
                code="solvation_formula",
                message="An electronic solvation shift is one solvated energy "
                "minus one vacuum energy.",
            ),
        )
    a, b = solvated[0], vacuum[0]
    issues: list[Diagnostic] = []
    if a.model.solvent_free_identity != b.model.solvent_free_identity:
        issues.append(
            Diagnostic(
                path=path,
                code="solvation_model",
                message="Preserve the electronic treatment when adding the solvent.",
            )
        )
    first, second = quantities[a.id], quantities[b.id]
    if (
        first.geometry != second.geometry
        or first.system != second.system
        or first.state != second.state
    ):
        issues.append(
            Diagnostic(
                path=path,
                code="solvation_geometry",
                message="A vertical electronic solvation shift requires common "
                "geometry, system, and state provenance.",
            )
        )
    return tuple(issues)
