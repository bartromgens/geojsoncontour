#!/usr/bin/python3.4
# -*- encoding: utf-8 -*-
"""Transform matplotlib.contour(f) to GeoJSON."""

import geojson
import numpy as np
from matplotlib.colors import rgb2hex
from geojson import Feature, LineString, Polygon, FeatureCollection


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


def contour_to_geojson(contour, geojson_filepath, contour_levels,
                       min_angle_deg=2,
                       ndigits=3, unit='', stroke_width=3):
    """Transform matplotlib.contour to geojson."""
    collections = contour.collections
    total_points = 0
    total_points_original = 0
    contour_index = 0
    assert len(contour_levels) == len(collections)
    line_features = []
    for collection in collections:
        paths = collection.get_paths()
        color = collection.get_edgecolor()
        for path in paths:
            v = path.vertices
            if len(v) < 6:
                continue
            coordinates = []
            v1 = v[1] - v[0]
            lat = round(v[0][0], ndigits)
            lon = round(v[0][1], ndigits)
            coordinates.append((lat, lon))
            for i in range(1, len(v) - 2):
                v2 = v[i + 1] - v[i - 1]
                diff_angle = np.fabs(angle(v1, v2) * 180.0 / np.pi)
                if diff_angle > min_angle_deg:
                    lat = round(v[i][0], ndigits)
                    lon = round(v[i][1], ndigits)
                    coordinates.append((lat, lon))
                    v1 = v[i] - v[i - 1]
            lat = round(v[-1][0], ndigits)
            lon = round(v[-1][1], ndigits)
            coordinates.append((lat, lon))
            total_points += len(coordinates)
            total_points_original += len(v)
            line = LineString(coordinates)
            properties = {
                "stroke-width": stroke_width,
                "stroke": rgb2hex(color[0]),
                "title": "%.2f" % contour_levels[contour_index] + ' ' + unit,
            }
            line_features.append(Feature(geometry=line, properties=properties))
        contour_index += 1

    if total_points_original > 0:
        print('total points: ' + str(total_points) + ', compression: ' + str(
            int((1.0 - total_points / total_points_original) * 100)) + '%')
    else:
        print('no points found')

    feature_collection = FeatureCollection(line_features)
    dump = geojson.dumps(feature_collection, sort_keys=True)
    with open(geojson_filepath, 'w') as fileout:
        fileout.write(dump)


def contourf_to_geojson(contourf, geojson_filepath, contour_levels,
                        min_angle_deg=None,
                        ndigits=3, unit='', fill_opacity=.9, stroke_width=1):
    """Transform matplotlib.contourf to geojson."""
    polygon_features = []
    contourf_index = 0
    for coll in contourf.collections:
        color = coll.get_facecolor()
        for path in coll.get_paths():
            for coord in path.to_polygons():
                coord = np.around(coord, ndigits) if ndigits else coord
                polygon = Polygon(coordinates=[coord.tolist()])
                fcolor = rgb2hex(color[0])
                properties = {
                    "stroke": fcolor,
                    "stroke-width": stroke_width,
                    "stroke-opacity": 1,
                    "fill": fcolor,
                    "fill-opacity": fill_opacity,
                    "title": "%.2f" % contour_levels[contourf_index] + ' ' + unit
                }
                feature = Feature(geometry=polygon, properties=properties)
                polygon_features.append(feature)
        contourf_index += 1
    collection = FeatureCollection(polygon_features)
    with open(geojson_filepath, 'w') as fileout:
        geojson.dump(collection, fileout)
