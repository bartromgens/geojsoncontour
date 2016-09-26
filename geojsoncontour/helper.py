#!/usr/bin/python3.4
# -*- encoding: utf-8 -*-
"""Helper module for transformation of matplotlib.contour(f) to GeoJSON."""
from geojson import MultiPolygon
import numpy as np


class MP(object):
    """Class for easy MultiPolygon generation.

    Just a helper class for easy identification of
    similar matplotlib.collections.
    """

    def __init__(self, title, color):
        """Destinction based on title and color."""
        self.title = title
        self.color = color
        self.coords = []

    def add_coords(self, coords):
        """Add new coordinate set for MultiPolygon."""
        self.coords.append(coords)

    def __eq__(self, other):
        """Comparison of two MP instances."""
        return (self.title == getattr(other, 'title', False) and
                self.color == getattr(other, 'color', False))

    def mpoly(self):
        """Output of GeoJSON MultiPolygon object."""
        return MultiPolygon(coordinates=[self.coords])


def unit_vector(vector):
    """Return the unit vector of the vector."""
    return vector / np.linalg.norm(vector)


def angle(v1, v2):
    """Return the angle in radians between vectors 'v1' and 'v2'.

    >>> angle_between((1, 0, 0), (0, 1, 0))
    1.5707963267948966
    >>> angle_between((1, 0, 0), (1, 0, 0))
    0.0
    >>> angle_between((1, 0, 0), (-1, 0, 0))
    3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


def keep_high_angle(vertices, min_angle_deg):
    """Keep vertices with angles higher then given minimum."""
    accepted = []
    v = vertices
    v1 = v[1] - v[0]
    accepted.append((v[0][0], v[0][1]))
    for i in range(1, len(v) - 2):
        v2 = v[i + 1] - v[i - 1]
        diff_angle = np.fabs(angle(v1, v2) * 180.0 / np.pi)
        if diff_angle > min_angle_deg:
            accepted.append((v[i][0], v[i][1]))
            v1 = v[i] - v[i - 1]
    accepted.append((v[-1][0], v[-1][1]))
    return np.array(accepted, dtype=vertices.dtype)


def set_properties(stroke_width, fcolor, fill_opacity, contour_levels,
                   contourf_idx, unit):
    """Set property values for Polygon."""
    return {
        "stroke": fcolor,
        "stroke-width": stroke_width,
        "stroke-opacity": 1,
        "fill": fcolor,
        "fill-opacity": fill_opacity,
        "title": "%.2f" % contour_levels[contourf_idx] + ' ' + unit
    }
