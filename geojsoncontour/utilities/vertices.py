from collections.abc import Generator

import numpy as np
import numpy.typing as npt
from matplotlib.path import Path

def get_vertices_from_path(path: Path) -> Generator[npt.NDArray[float], None, None]:
    """Splits the vertices from path into continous lines,
    by taking into account path.codes

    See https://matplotlib.org/stable/api/path_api.html for a
    description of path.vertices/path.codes
    """
    # path = path.cleaned(curves=False, simplify=False)
    vertices = path.vertices
    codes = path.codes
    if codes is None:
        codes = [Path.MOVETO] + [Path.LINETO]*(len(vertices)-1)
    current_vertice = []
    for (v, c) in zip(vertices, codes):
        if c == Path.STOP:
            if len(current_vertice) != 0:
                yield np.array(current_vertice)
                current_vertice = []
        elif c == Path.MOVETO:
            if len(current_vertice) != 0:
                yield np.array(current_vertice)
            current_vertice = [v]
        elif c == Path.LINETO:
            current_vertice.append(v)
        elif c == Path.CLOSEPOLY:
            if len(current_vertice) != 0:
                current_vertice.append(current_vertice[0])
                yield np.array(current_vertice)
                current_vertice = []
        else:
            raise Exception(f"Unknown code {c} encountered")
    if len(current_vertice) != 0:
        yield np.array(current_vertice)
