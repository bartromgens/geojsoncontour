#!/usr/bin/python3.4
# -*- encoding: utf-8 -*-
"""Transform matplotlib.contour(f) to GeoJSON."""

import geojson
import numpy as np
from matplotlib.colors import rgb2hex
from geojson import Feature, LineString
from geojson import Polygon, FeatureCollection
from .utilities.multipoly import MP, keep_high_angle, set_properties
import matplotlib


def contour_to_geojson(contour,
                       min_angle_deg=2,
                       geojson_filepath=None, strdump=False,
                       ndigits=3, unit='', stroke_width=3):
    """Transform matplotlib.contour to geojson."""
    contour_levels = contour.levels
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
    if strdump or not geojson_filepath:
        return geojson.dumps(collection, sort_keys=True, separators=(',', ':'))
    with open(geojson_filepath, 'w') as fileout:
        geojson.dump(feature_collection, fileout,
                     sort_keys=True, separators=(',', ':'))


def contourf_to_geojson(contourf,
                        min_angle_deg=None, strdump=False,
                        geojson_filepath=None,
                        ndigits=3, unit='', fill_opacity=.9, stroke_width=1):
    """Transform matplotlib.contourf to geojson."""
    contour_levels = contourf.levels
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
    if strdump or not geojson_filepath:
        return geojson.dumps(collection, sort_keys=True, separators=(',', ':'))
    with open(geojson_filepath, 'w') as fileout:
        geojson.dump(collection, fileout,
                     sort_keys=True, separators=(',', ':'))


def contourf_to_multipolygeojson(contourf,
                                 unit='', fill_opacity=.9, strdump=False,
                                 geojson_filepath=None,
                                 ndigits=3, min_angle_deg=5, stroke_width=1):
    """Transform matplotlib.contourf to geojson with MultiPolygons."""
    contour_levels = contourf.levels
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
    if strdump or not geojson_filepath:
        return geojson.dumps(collection, sort_keys=True, separators=(',', ':'))
    with open(geojson_filepath, 'w') as fileout:
        geojson.dump(collection, fileout,
                     sort_keys=True, separators=(',', ':'))


def to_geojson(contour, multipolys=False, strdump=False, *args, **kwargs):
    message = 'Expected QuadContourSet, got {}'.format(type(contour))
    assert isinstance(contour, matplotlib.contour.QuadContourSet), message
    unit = contour.da_unit
    if not contour.filled:
        return contour_to_geojson(contour,
                                  strdump=strdump, unit=unit, *args, **kwargs)
    elif multipolys:
        return contourf_to_multipolygeojson(contour,
                                            strdump=strdump,
                                            unit=unit,
                                            *args, **kwargs)
    else:
        return contourf_to_geojson(contour,
                                   unit=unit, strdump=strdump, *args, **kwargs)
