"""Transform matplotlib.contour(f) to GeoJSON."""

import geojson
import numpy as np
from matplotlib.colors import rgb2hex
from geojson import Feature, LineString
from geojson import Polygon, FeatureCollection
from .utilities.multipoly import MP, keep_high_angle, set_contourf_properties


def contour_to_geojson(contour, geojson_filepath=None, min_angle_deg=None,
                       ndigits=5, unit='', stroke_width=1, geojson_properties=None, strdump=False,
                       serialize=True):
    """Transform matplotlib.contour to geojson."""
    collections = contour.collections
    contour_index = 0
    line_features = []
    for collection in collections:
        color = collection.get_edgecolor()
        for path in collection.get_paths():
            v = path.vertices
            if len(v) < 3:
                continue
            coordinates = keep_high_angle(v, min_angle_deg) if min_angle_deg else v
            coordinates = np.around(coordinates, ndigits) if ndigits is not None else coordinates
            line = LineString(coordinates.tolist())
            properties = {
                "stroke-width": stroke_width,
                "stroke": rgb2hex(color[0]),
                "title": "%.2f" % contour.levels[contour_index] + ' ' + unit,
                "level-value": float("%.6f" % contour.levels[contour_index]),
                "level-index": contour_index
            }
            if geojson_properties:
                properties.update(geojson_properties)
            line_features.append(Feature(geometry=line, properties=properties))
        contour_index += 1
    feature_collection = FeatureCollection(line_features)
    return _render_feature_collection(feature_collection, geojson_filepath, strdump, serialize)


def contourf_to_geojson_overlap(contourf, geojson_filepath=None, min_angle_deg=None,
                                ndigits=5, unit='', stroke_width=1, fill_opacity=.9,
                                geojson_properties=None, strdump=False, serialize=True):
    """Transform matplotlib.contourf to geojson with overlapping filled contours."""
    polygon_features = []
    contourf_idx = 0
    for collection in contourf.collections:
        color = collection.get_facecolor()
        for path in collection.get_paths():
            for coord in path.to_polygons():
                if min_angle_deg:
                    coord = keep_high_angle(coord, min_angle_deg)
                coord = np.around(coord, ndigits) if ndigits else coord
                polygon = Polygon(coordinates=[coord.tolist()])
                fcolor = rgb2hex(color[0])
                properties = set_contourf_properties(stroke_width, fcolor, fill_opacity, contourf.levels, contourf_idx, unit)
                if geojson_properties:
                    properties.update(geojson_properties)
                feature = Feature(geometry=polygon, properties=properties)
                polygon_features.append(feature)
        contourf_idx += 1
    feature_collection = FeatureCollection(polygon_features)
    return _render_feature_collection(feature_collection, geojson_filepath, strdump, serialize)


def contourf_to_geojson(contourf, geojson_filepath=None, min_angle_deg=None,
                        ndigits=5, unit='', stroke_width=1, fill_opacity=.9,
                        geojson_properties=None, strdump=False, serialize=True):
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
                op = MP(contourf.levels[contourf_idx], rgb2hex(color[0]))
                if op in mps:
                    for i, k in enumerate(mps):
                        if k == op:
                            mps[i].add_coords(coord.tolist())
                else:
                    op.add_coords(coord.tolist())
                    mps.append(op)
        contourf_idx += 1
    # starting here the multipolys will be extracted
    contourf_idx = 0
    for muli in mps:
        polygon = muli.mpoly()
        fcolor = muli.color
        properties = set_contourf_properties(stroke_width, fcolor, fill_opacity, contourf.levels, contourf_idx, unit)
        if geojson_properties:
            properties.update(geojson_properties)
        feature = Feature(geometry=polygon, properties=properties)
        polygon_features.append(feature)
        contourf_idx += 1
    feature_collection = FeatureCollection(polygon_features)
    return _render_feature_collection(feature_collection, geojson_filepath, strdump, serialize)


def _render_feature_collection(feature_collection, geojson_filepath, strdump, serialize):
    if not serialize:
        return feature_collection
    if strdump or not geojson_filepath:
        return geojson.dumps(feature_collection, sort_keys=True, separators=(',', ':'))
    with open(geojson_filepath, 'w') as fileout:
        geojson.dump(feature_collection, fileout, sort_keys=True, separators=(',', ':'))
