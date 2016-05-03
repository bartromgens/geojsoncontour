import math


from matplotlib.colors import rgb2hex

from geojson import Feature, LineString, FeatureCollection
import geojson


def dotproduct(v1, v2):
    return sum((a * b) for a, b in zip(v1, v2))


def length(v):
    return math.sqrt(dotproduct(v, v))


def angle(v1, v2):
    cos_angle = dotproduct(v1, v2) / (length(v1) * length(v2))
    cos_angle = min(1.0, max(cos_angle, -1.0))
    assert cos_angle <= 1.0
    assert cos_angle >= -1.0
    return math.acos(cos_angle)


def contour_to_geojson(contour, geojson_filepath, contour_levels, min_angle_deg=2,
                       ndigits=5, unit='', stroke_width=5):
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
            long = round(v[0][1], ndigits)
            coordinates.append((lat, long))
            for i in range(1, len(v) - 2):
                v2 = v[i + 1] - v[i - 1]
                diff_angle = math.fabs(angle(v1, v2) * 180.0 / math.pi)
                if diff_angle > min_angle_deg:
                    lat = round(v[i][0], ndigits)
                    long = round(v[i][1], ndigits)
                    coordinates.append((lat, long))
                    v1 = v[i] - v[i - 1]
            lat = round(v[-1][0], ndigits)
            long = round(v[-1][1], ndigits)
            coordinates.append((lat, long))
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