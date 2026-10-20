"""Read, edit, and write Psi4 input as ordered Python and native components.

read_job(source) returns a Job whose body contains typed molecule, settings,
basis, and other native blocks alongside Python text. Construct a new input
with Job(body=(...)), and write it with emit_job(job).

Molecules expose atom IDs for coordinate edits and preserve the order of their
records. Number stores input spelling such as "1.2D-3"; Variable names a
geometry parameter. Use model_dump_json(), model_validate_json(), and
model_json_schema() on Job to save, load, and describe the document format.

For geometry transformations and calculation helpers, use psi4_parser.builder.
"""

from psi4_parser.job.emitter import emit_job
from psi4_parser.job.model import (
    FragmentSeparator,
    Nucleus,
    Number,
    Scalar,
    Units,
    Variable,
)
from psi4_parser.job.molecule import (
    Anchor,
    Atom,
    AtomReference,
    Cartesian,
    Coordinates,
    EFPFragment,
    ElectronicState,
    Fragment,
    FrameDirective,
    GeometrySource,
    GeometryVariable,
    LabelReference,
    Molecule,
    MoleculeRecord,
    Symmetry,
    XYZHeader,
    ZMatrix,
)
from psi4_parser.job.nodes import (
    PCM,
    Basis,
    BasisAssignment,
    BasisData,
    BasisLabel,
    BasisRecord,
    CFour,
    External,
    ExternalAtom,
    ExternalBasis,
    ExternalRecord,
    Job,
    Memory,
    NativeNode,
    Node,
    OptionArray,
    OptionAssignment,
    OptionExpression,
    OptionReference,
    OptionValue,
    PointCharge,
    Python,
    PythonTemplate,
    SetOptions,
    TemplatePart,
)
from psi4_parser.job.reader import JobSyntaxError, read_job

__all__ = [
    "PCM",
    "Anchor",
    "Atom",
    "AtomReference",
    "Basis",
    "BasisAssignment",
    "BasisData",
    "BasisLabel",
    "BasisRecord",
    "CFour",
    "Cartesian",
    "Coordinates",
    "EFPFragment",
    "ElectronicState",
    "External",
    "ExternalAtom",
    "ExternalBasis",
    "ExternalRecord",
    "Fragment",
    "FragmentSeparator",
    "FrameDirective",
    "GeometrySource",
    "GeometryVariable",
    "Job",
    "JobSyntaxError",
    "LabelReference",
    "Memory",
    "Molecule",
    "MoleculeRecord",
    "NativeNode",
    "Node",
    "Nucleus",
    "Number",
    "OptionArray",
    "OptionAssignment",
    "OptionExpression",
    "OptionReference",
    "OptionValue",
    "PointCharge",
    "Python",
    "PythonTemplate",
    "Scalar",
    "SetOptions",
    "Symmetry",
    "TemplatePart",
    "Units",
    "Variable",
    "XYZHeader",
    "ZMatrix",
    "emit_job",
    "read_job",
]
