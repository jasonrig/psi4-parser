"""Build executable inputs only after every requested relationship is proved."""

from itertools import groupby
from typing import Literal

from psi4_parser import builder
from psi4_parser.formal.capabilities import CapabilityCatalog
from psi4_parser.formal.contracts import inspect_contracts, primary_quantity
from psi4_parser.formal.intent import ScientificRequest
from psi4_parser.formal.models import (
    Calculation,
    Combination,
    Limits,
    Plan,
    Product,
    Report,
    Subsystem,
)
from psi4_parser.formal.products import PRIMARY_SCALAR_PRODUCTS
from psi4_parser.formal.science import Rational, Setting
from psi4_parser.formal.verification import verify


def _setting_module(setting: Setting) -> str | None:
    return setting.module


def _local_options(
    step: Calculation,
    units: Literal["angstrom", "bohr"],
    *,
    output_label: str | None = None,
    tdscf_moments: bool = False,
) -> tuple[builder.Options, ...]:
    result = tuple(
        builder.options(
            modules=(module,) if module else (),
            **{item.name: item.value for item in settings},
        )
        for module, settings in groupby(
            step.model.engine_settings_for(units), key=_setting_module
        )
    )
    if step.analysis is not None:
        conditions = step.analysis.conditions
        result += (
            builder.options(
                modules=("THERMO",),
                T=conditions.temperature_kelvin,
                P=conditions.pressure_pascal,
                ROTATIONAL_SYMMETRY_NUMBER=step.analysis.rotational_symmetry_number,
            ),
        )
    if output_label is not None:
        result += (
            builder.options(WRITER_FILE_LABEL=output_label),
            builder.options(modules=("FINDIF",), HESSIAN_WRITE=True),
        )
    if step.sapt is not None:
        result += (
            builder.options(
                modules=("SAPT",), COUPLED_INDUCTION=step.sapt.coupled_induction
            ),
        )
    if tdscf_moments:
        result += (builder.options(modules=("SCF",), TDSCF_TDM_PRINT=("E_TDM_LEN",)),)
    return result


def _keywords(step: Calculation) -> tuple[builder.components.Keyword, ...]:
    keywords: list[builder.components.Keyword] = []
    if step.sapt is not None:
        keywords.append(
            builder.components.Keyword(
                name="sapt_basis", value=builder.LiteralValue(value=step.sapt.basis)
            )
        )
    if step.analysis is not None:
        keywords.extend(
            (
                builder.components.Keyword(
                    name="project_trans",
                    value=builder.LiteralValue(
                        value=step.analysis.project_translations
                    ),
                ),
                builder.components.Keyword(
                    name="project_rot",
                    value=builder.LiteralValue(value=step.analysis.project_rotations),
                ),
            )
        )
    if step.derivative_route != "automatic":
        order = 2 if step.driver in {"hessian", "frequency"} else 1
        keywords.append(
            builder.components.Keyword(
                name="dertype",
                value=builder.LiteralValue(
                    value=order if step.derivative_route == "analytic" else 0
                ),
            )
        )
    if step.properties:
        keywords.append(
            builder.components.Keyword(
                name="properties",
                value=builder.SequenceValue(
                    items=tuple(
                        builder.LiteralValue(value=name) for name in step.properties
                    )
                ),
            )
        )
    if step.model.external_potential is not None:
        keywords.append(
            builder.components.Keyword(
                name="external_potentials", value=step.model.external_potential
            )
        )
    return tuple(keywords)


def _coefficient(value: int | Rational) -> str:
    if isinstance(value, Rational):
        rational = value.fraction
        return f"({rational.numerator} / {rational.denominator})"
    return str(value)


class VerificationError(ValueError):
    """Expose diagnostics or counterexamples when a plan cannot authorize a job.

    Attributes:
        report: Full verification result for the rejected plan.
    """

    def __init__(self, report: Report) -> None:
        """Retain the rejected report and summarize its failed checks."""
        self.report = report
        messages = [item.message for item in report.diagnostics]
        messages.extend(
            f"requirements[{item.index}]: {item.message}"
            for item in report.obligations
            if item.status != "proved"
        )
        super().__init__(f"Plan verification {report.status}: " + "; ".join(messages))


def build(
    plan: Plan,
    *,
    limits: Limits | None = None,
    request: ScientificRequest | None = None,
    catalog: CapabilityCatalog | None = None,
) -> builder.JobSpec:
    """Return a builder job only when all supplied relationships are proved.

    Args:
        plan: Molecular inputs, ordered steps, and independently stated requirements.
        limits: Bounds on solver checks; None uses the default limits.
        request: Independent scientific intent to check before construction.
        catalog: Application capability evidence used for scientific-request checks.

    Returns:
        A self-contained builder job. Runtime dictionaries formal_results and
        formal_geometries retain direct return values, expressions using those
        values, and input or optimized molecules. Secondary products and their
        dependent expressions remain recipes for a separate consumer; use bundle
        export to retain that handoff. Named frequency products request native
        vibrational record files. Runtime dictionaries exist only after execution.

    Raises:
        VerificationError: A requirement is violated, unsupported, or undecided.
    """
    plan = Plan.model_validate(plan)
    report = verify(plan, limits=limits, request=request, catalog=catalog)
    if report.status != "proved":
        raise VerificationError(report)
    return _lower(plan)


def _subsystem_job(
    job: builder.JobSpec,
    step: Subsystem,
    source: str,
    molecule: builder.Molecule,
    index: int,
) -> tuple[builder.JobSpec, str]:
    name = f"formal_subsystem_{index}"
    job = job | builder.MoleculeClone(name=name, source=builder.Reference(name=source))
    for fragment_index, fragment in enumerate(molecule.fragments, 1):
        operation = (
            "set_active_fragment"
            if fragment.name in step.real_fragments
            else "set_ghost_fragment"
        )
        job = job | builder.call(f"{name}.{operation}", fragment_index)
    job = job | builder.call(f"{name}.set_molecular_charge", step.state.charge)
    job = job | builder.call(f"{name}.set_multiplicity", step.state.multiplicity)
    job = job | builder.call(f"{name}.update_geometry")
    return job, name


def _lower(plan: Plan, *, expressions: bool = True) -> builder.JobSpec:
    # Callers establish plan validity before reaching this backend boundary.
    job = builder.compose()
    geometries: dict[str, str] = {}
    results: dict[str, str] = {}
    inspection = inspect_contracts(plan)
    contexts = inspection.contexts
    output_labels = {item.producer: item.label for item in inspection.native_outputs}
    tdscf_moments = {
        step.calculation
        for step in plan.steps
        if isinstance(step, Product)
        and step.name == "electric_transition_dipole_length"
    }
    calculations = {
        step.id: step for step in plan.steps if isinstance(step, Calculation)
    }
    for index, declaration in enumerate(plan.molecules):
        name = f"formal_input_{index}"
        job = job | builder.molecule(name, declaration.geometry)
        geometries[declaration.name] = name
    for index, step in enumerate(plan.steps):
        if isinstance(step, Product):
            if expressions and (
                step.name == primary_quantity(calculations[step.calculation]).meaning
                or step.name in PRIMARY_SCALAR_PRODUCTS
            ):
                results[step.id] = results[step.calculation]
            continue
        if isinstance(step, Subsystem):
            job, name = _subsystem_job(
                job, step, geometries[step.geometry], contexts[step.geometry], index
            )
            geometries[step.id] = name
            continue
        if isinstance(step, Combination) and (
            not expressions or any(term.result not in results for term in step.terms)
        ):
            continue
        result = f"formal_energy_{index}"
        if isinstance(step, Calculation):
            geometry = f"formal_geometry_{index}"
            job = job | builder.call("psi4.core.clean")
            job = job | builder.MoleculeClone(
                source=builder.Reference(name=geometries[step.geometry]), name=geometry
            )
            job = job | builder.Calculation(
                driver=step.driver,
                method=builder.LiteralValue(value=step.model.method.strip()),
                molecule=builder.Reference(name=geometry),
                local_options=_local_options(
                    step,
                    contexts[step.geometry].units,
                    output_label=output_labels.get(step.id),
                    tdscf_moments=step.id in tdscf_moments,
                ),
                isolate_options=True,
                pcm_input=(
                    step.model.environment.pcm.input_text(
                        step.model.environment.solvent
                    )
                    if step.model.environment and step.model.environment.kind == "pcm"
                    else None
                ),
                kwargs=_keywords(step),
                constraints=step.constraints,
                assign=result,
            )
            if step.driver == "optimize":
                geometries[step.id] = geometry
        else:
            expression = " + ".join(
                f"({_coefficient(term.coefficient)} * {results[term.result]})"
                for term in step.terms
            )
            job = job | builder.Python(
                source=f"{result} = {expression}", provides=(result,)
            )
        results[step.id] = result
    for name, mapping in (
        ("formal_results", results),
        ("formal_geometries", geometries),
    ):
        entries = ", ".join(f"{key!r}: {value}" for key, value in mapping.items())
        job = job | builder.Python(source=f"{name} = {{{entries}}}", provides=(name,))
    return job


def render(
    plan: Plan,
    *,
    limits: Limits | None = None,
    request: ScientificRequest | None = None,
    catalog: CapabilityCatalog | None = None,
) -> str:
    """Return Psi4 input after proving the plan's requested relationships.

    Args:
        plan: Molecular inputs, ordered steps, and independently stated requirements.
        limits: Bounds on solver checks; None uses the default limits.
        request: Independent scientific intent to check before construction.
        catalog: Application capability evidence used for scientific-request checks.

    Returns:
        Formatted Psithon text whose construction is authorized by verification.
        Successful rendering establishes the encoded relationships and syntax;
        execute separately to check installed capabilities and calculation results.

    Raises:
        VerificationError: The supplied plan cannot authorize construction.
        builder.CompilationError: Generated input fails builder syntax validation.
    """  # noqa: DOC502 - Verification and syntax failures propagate from callees.
    return builder.render_job(
        build(plan, limits=limits, request=request, catalog=catalog)
    )
