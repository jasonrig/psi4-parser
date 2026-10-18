"""Type the documented MolSym 1.2 constructor and point-group API.

MolSym does not ship a py.typed marker. These declarations cover the interfaces
used by the adapter, including its list-valued axes for linear molecules.
"""

import numpy as np
from numpy.typing import NDArray

type SymmetryAxis = NDArray[np.float64] | list[int] | list[float]
type PointGroupResult = tuple[str, tuple[SymmetryAxis, SymmetryAxis]]

class Molecule:
    tol: float

    def __init__(
        self,
        atoms: NDArray[np.str_],
        coords: NDArray[np.float64],
        masses: NDArray[np.float64],
    ) -> None: ...

def find_point_group(
    molecule: Molecule,
) -> PointGroupResult: ...
