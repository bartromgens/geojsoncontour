#!/usr/bin/python3.4
# -*- encoding: utf-8 -*-
"""Helper module for transformation of matplotlib.contour(f) to GeoJSON."""
from geojson import MultiPolygon
import numpy as np


class MP(object):
    """Class for easy MultiPolygon generation.

    This class converts a matplotlib PathCollection into a GeoJSON MultiPolygon.
    """

    def __init__(self, path_collection, min_angle_deg, ndigits):
        self.coords = []
        for path in path_collection.get_paths():
            polygon = []
            for linestring in path.to_polygons():
                if min_angle_deg:
                    linestring = keep_high_angle(linestring, min_angle_deg)
                if ndigits:
                    linestring = np.around(linestring, ndigits)
                polygon.append(linestring.tolist())
            self.coords.append(polygon)

    def mpoly(self):
        """Output of GeoJSON MultiPolygon object."""
        return MultiPolygon(coordinates=self.coords)


def unit_vector(vector):
    """Return the unit vector of the vector."""
    return vector / np.linalg.norm(vector)


def angle(v1, v2):
    """Return the angle in radians between vectors 'v1' and 'v2'."""
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


def set_contourf_properties(stroke_width, fcolor, fill_opacity, level, unit):
    """Set property values for Polygon."""
    return {
        "stroke": fcolor,
        "stroke-width": stroke_width,
        "stroke-opacity": 1,
        "fill": fcolor,
        "fill-opacity": fill_opacity,
        "title": "{} {}".format(level, unit)
    }


def get_contourf_levels(levels, extend):
    mid_levels = ["%.2f" % levels[i] + '-' + "%.2f" % levels[i+1] for i in range(len(levels)-1)]
    if extend == 'both':
        return ["<%.2f" % levels[0], *mid_levels, ">%.2f" % levels[-1]]
    elif extend == 'max':
        return [*mid_levels, ">%.2f" % levels[-1]]
    elif extend == 'min':
        return ["<%.2f" % levels[0], *mid_levels]
    else:
        return mid_levels
