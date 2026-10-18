"""Fail when native grammar productions or model types lack an AST mapping."""

import re
from pathlib import Path

from pydantic import JsonValue, TypeAdapter

from psi4_parser.job import Job
from psi4_parser.job.model import Model
from psi4_parser.job.reader import BUILDERS
from psi4_parser.maintenance.audit import compare_cases

_GRAMMAR = Path(__file__).resolve().parents[1] / "grammar/PsithonParser.g4"

# Every native production has an explicit data destination or syntax boundary.
# These are reviewed mappings, checked against the grammar rather than counted
# from whichever fixtures happen to be present.
_DESTINATIONS = {
    "molecule_block": "Molecule",
    "molecule_name": "Molecule.name",
    "molecule_body": "Molecule.records",
    "molecule_line": "MoleculeRecord discriminated union",
    "xyz_header": "XYZHeader",
    "charge_multiplicity": "ElectronicState",
    "geometry_variable": "GeometryVariable",
    "unit_name": "Units.name",
    "atom_line": "Atom",
    "nucleus": "Nucleus",
    "nucleus_label": "Nucleus.label",
    "isotope_mass": "Nucleus.mass",
    "coordinate": "Scalar discriminated union",
    "anchor_pair": "Anchor",
    "efp_fragment": "EFPFragment",
    "numeric_xyz": "EFPFragment.points",
    "set_command": "SetOptions(style=inline)",
    "set_block": "SetOptions(style=block)",
    "module_list": "SetOptions.modules",
    "module_name": "SetOptions.modules element",
    "module_piece": "SetOptions.modules element spelling",
    "option_key": "OptionAssignment.key",
    "option_assignment": "OptionAssignment",
    "inline_option_value": "OptionValue discriminated union",
    "set_option_value": "OptionValue discriminated union",
    "set_option_array": "OptionArray",
    "set_option_piece": "OptionExpression or nested OptionArray",
    "inline_option_scalar": "OptionExpression or OptionReference",
    "inline_option_piece": "OptionExpression.source",
    "option_reference": "OptionReference",
    "memory_line": "Memory",
    "basis_block": "Basis",
    "basis_line": "BasisRecord discriminated union",
    "basis_assignment": "BasisAssignment",
    "basis_name": "BasisAssignment.basis or BasisLabel.name",
    "basis_label": "BasisLabel",
    "basis_record": "BasisData embedded GBS/ECP payload",
    "external_block": "External",
    "external_line": "ExternalRecord discriminated union",
    "external_basis_line": "ExternalBasis",
    "external_basis_key": "ExternalBasis.role",
    "pcm_block": "PCM",
    "pcm_body": "PCM.body embedded PCMSolver payload",
    "cfour_block": "CFour",
    "header_label": "Basis.name, External.name, PCM.name, CFour.name",
    "header_space": "syntax: normalized header separators",
    "native_word": "syntax: spelling retained in its owning field",
    "native_identifier": "syntax: spelling retained in its owning field",
    "literal_line": "GeometrySource.value or XYZHeader.title",
    "literal_piece": "syntax: spelling retained in an explicit reader payload",
}


def test_every_native_production_has_a_destination() -> None:
    """Make additions or removals in native grammar rules require an AST review."""
    source = _GRAMMAR.read_text()
    section = source[source.index("\nmolecule_block\n") : source.index("\nparam_end\n")]
    productions = {
        match[1]
        for match in re.finditer(r"^([a-z][a-z_]*)\s*\n\s*:", section, re.MULTILINE)
    }

    assert productions == set(_DESTINATIONS)


def test_every_native_entry_point_has_a_builder() -> None:
    """Reject native directives that would otherwise be retained as Python text."""
    source = _GRAMMAR.read_text()
    entry_points = {
        match[1]
        for match in re.finditer(
            r"^([a-z][a-z_]*)\s*\n\s*:\s*PSI_", source, re.MULTILINE
        )
    }

    assert entry_points == set(BUILDERS)


def test_all_ast_models_are_reachable_from_the_schema() -> None:
    """Require new model variants to participate in the serializable job graph."""
    adapter = TypeAdapter(JsonValue)
    schema = adapter.validate_python(Job.model_json_schema())  # type: ignore[misc]
    assert isinstance(schema, dict)
    definitions = schema["$defs"]
    assert isinstance(definitions, dict)
    model_names = {model.__name__ for model in Model.__subclasses__()}

    # Fragment is a construction/view model compiled into native ordered records.
    assert model_names - {"Fragment", "Job"} <= set(definitions)


def test_upgrade_audit_requires_native_ast_acceptance() -> None:
    """Reject a reference-accepted job that cannot enter the native AST layer."""
    failures = compare_cases(
        [
            {
                "name": "accepted",
                "source": "set basis [\n",
                "expected": True,
                "upstream": False,
            }
        ],
        {"accepted": {"name": "accepted", "digest": "accepted", "error": ""}},
    )

    assert failures
    assert "native AST" in failures[0]["error"]
