#!/usr/bin/python3.4
# -*- encoding: utf-8 -*-
"""Transform matplotlib.contour(f) to GeoJSON."""

import geojson
import numpy as np
from matplotlib.colors import rgb2hex
from geojson import Feature, LineString
from geojson import Polygon, FeatureCollection
from .helper import MP, keep_high_angle, set_properties


def contour_to_geojson(contour, geojson_filepath, contour_levels,
                       min_angle_deg=2,
                       ndigits=3, unit='', stroke_width=3):
    """Transform matplotlib.contour to geojson."""
    collections = contour.collections
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
            coordinates = keep_high_angle(v, min_angle_deg)
            if ndigits:
                coordinates = np.around(coordinates, ndigits)
            line = LineString(coordinates.tolist())
            properties = {
                "stroke-width": stroke_width,
                "stroke": rgb2hex(color[0]),
                "title": "%.2f" % contour_levels[contour_index] + ' ' + unit,
            }
            line_features.append(Feature(geometry=line, properties=properties))
        contour_index += 1
    feature_collection = FeatureCollection(line_features)
    dump = geojson.dumps(feature_collection, sort_keys=True,
                         separators=(',', ':'))
    with open(geojson_filepath, 'w') as fileout:
        fileout.write(dump)


def contourf_to_geojson(contourf, geojson_filepath, contour_levels,
                        min_angle_deg=None,
                        ndigits=3, unit='', fill_opacity=.9, stroke_width=1):
    """Transform matplotlib.contourf to geojson."""
    polygon_features = []
    contourf_idx = 0
    for coll in contourf.collections:
        color = coll.get_facecolor()
        for path in coll.get_paths():
            for coord in path.to_polygons():
                if min_angle_deg:
                    coord = keep_high_angle(coord, min_angle_deg)
                coord = np.around(coord, ndigits) if ndigits else coord
                polygon = Polygon(coordinates=[coord.tolist()])
                fcolor = rgb2hex(color[0])
                properties = set_properties(stroke_width, fcolor, fill_opacity,
                                            contour_levels, contourf_idx,
                                            unit)
                feature = Feature(geometry=polygon, properties=properties)
                polygon_features.append(feature)
        contourf_idx += 1
    collection = FeatureCollection(polygon_features)
    with open(geojson_filepath, 'w') as fileout:
        geojson.dump(collection, fileout,
                     sort_keys=True, separators=(',', ':'))


def contourf_to_multipolygeojson(contourf, geojson_filepath, contour_levels,
                                 unit='', fill_opacity=.9,
                                 ndigits=3, min_angle_deg=5, stroke_width=1):
    """Transform matplotlib.contourf to geojson with MultiPolygons."""
    polygon_features = []
    mps = []
    contourf_idx = 0
    for coll in contourf.collections:
        color = coll.get_facecolor()
        for path in coll.get_paths():
            for coord in path.to_polygons():
                if min_angle_deg:
                    coord = keep_high_angle(coord, min_angle_deg)
                coord = np.around(coord, ndigits) if ndigits else coord
                op = MP(contour_levels[contourf_idx], rgb2hex(color[0]))
                if op in mps:
                    for i, k in enumerate(mps):
                        if k == op:
                            mps[i].add_coords(coord.tolist())
                else:
                    op.add_coords(coord.tolist())
                    mps.append(op)
        contourf_idx += 1
    # starting here the multipolys will be extracted
    for muli in mps:
        polygon = muli.mpoly()
        fcolor = muli.color
        properties = set_properties(stroke_width, fcolor, fill_opacity,
                                    contour_levels, contourf_idx,
                                    unit)
        feature = Feature(geometry=polygon, properties=properties)
        polygon_features.append(feature)
    collection = FeatureCollection(polygon_features)
    with open(geojson_filepath, 'w') as fileout:
        geojson.dump(collection, fileout,
                     sort_keys=True, separators=(',', ':'))
