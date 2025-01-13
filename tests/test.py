import os
import unittest
import filecmp

import numpy
import matplotlib as mpl
mpl.use('Agg')  # create plots without running X-server
import matplotlib.pyplot as plt
import geojsoncontour


class TestContourToGeoJson(unittest.TestCase):
    dirname = os.path.dirname(__file__)
    geojson_file = os.path.join(dirname, 'test1.geojson')
    geojson_properties_file = os.path.join(dirname, 'test_properties.geojson')
    benchmark_geojson_file = os.path.join(dirname, 'benchmark_test1.geojson')
    benchmark_geojson_properties_file = os.path.join(dirname, 'benchmark_test_properties.geojson')
    geojson_file_contourf = os.path.join(dirname, 'contourf.geojson')
    benchmark_geojson_file_contourf = os.path.join(dirname, 'benchmark_contourf.geojson')
    geojson_file_multipoly = os.path.join(dirname, 'multipolycontourf.geojson')
    benchmark_geojson_file_multipoly = os.path.join(dirname, 'benchmark_multipolycontourf.geojson')


    @classmethod
    def setUpClass(cls):
        cls.config = ContourPlotConfig(level_lower=0.0, level_upper=202.0, unit='[unit]')
        if os.path.exists(cls.geojson_file):
            os.remove(cls.geojson_file)
        if os.path.exists(cls.geojson_properties_file):
            os.remove(cls.geojson_properties_file)
        if os.path.exists(cls.geojson_file_contourf):
            os.remove(cls.geojson_file_contourf)
        if os.path.exists(cls.geojson_file_multipoly):
            os.remove(cls.geojson_file_multipoly)

    def create_contour(self):
        latrange, lonrange, Z = TestContourToGeoJson.create_grid_data()
        figure = plt.figure()
        ax = figure.add_subplot(111)
        return ax.contour(
            lonrange, latrange, Z,
            levels=self.config.levels,
            cmap=self.config.colormap
        )

    def create_contourf(self):
        latrange, lonrange, Z = TestContourToGeoJson.create_grid_data()
        figure = plt.figure()
        ax = figure.add_subplot(111)
        return ax.contourf(
            lonrange, latrange, Z,
            levels=self.config.levels,
            cmap=self.config.colormap
        )

    def test_matplotlib_contour_to_geojson(self):
        contours = self.create_contour()
        ndigits = 3
        geojsoncontour.contour_to_geojson(
            contour=contours,
            geojson_filepath=self.geojson_file,
            min_angle_deg=self.config.min_angle_between_segments,
            ndigits=ndigits,
            unit=self.config.unit,
            stroke_width=5
        )
        self.assertTrue(os.path.exists(self.geojson_file))
        self.assertTrue(filecmp.cmp(self.benchmark_geojson_file, self.geojson_file))
        os.remove(self.geojson_file)

    def test_matplotlib_contour_to_geojson_none_min_angle(self):
        contours = self.create_contour()
        ndigits = 3
        geojsoncontour.contour_to_geojson(
            contour=contours,
            geojson_filepath=self.geojson_file,
            min_angle_deg=None,
            ndigits=ndigits,
            unit=self.config.unit,
            stroke_width=5
        )
        self.assertTrue(os.path.exists(self.geojson_file))
        os.remove(self.geojson_file)

    def test_return_string_if_destination_file_not_provided(self):
        contours = self.create_contour()
        ndigits = 3
        result = geojsoncontour.contour_to_geojson(
            contour=contours,
            min_angle_deg=self.config.min_angle_between_segments,
            ndigits=ndigits,
            unit=self.config.unit,
            stroke_width=5
        )
        self.assertTrue(isinstance(result, str))

    def test_return_string_if_strdump_argument_provided(self):
        contours = self.create_contour()
        ndigits = 3
        result = geojsoncontour.contour_to_geojson(
            geojson_filepath=self.geojson_file,
            strdump=True,
            contour=contours,
            min_angle_deg=self.config.min_angle_between_segments,
            ndigits=ndigits,
            unit=self.config.unit,
            stroke_width=5
        )
        self.assertTrue(isinstance(result, str))

    def test_return_python_object_if_serialize_argument_false(self):
        contours = self.create_contour()
        ndigits = 3
        result = geojsoncontour.contour_to_geojson(
            serialize=False,
            geojson_filepath=self.geojson_file,
            strdump=True,
            contour=contours,
            min_angle_deg=self.config.min_angle_between_segments,
            ndigits=ndigits,
            unit=self.config.unit,
            stroke_width=5
        )
        self.assertTrue(isinstance(result, dict))
        self.assertEqual(result["type"], "FeatureCollection")

    def test_contour_to_geojson_extra_properties(self):
        contour = self.create_contour()
        ndigits = 3
        geojson_properties = {
            'description': 'A description',
            'stroke-opacity': 1.0
        }
        geojsoncontour.contour_to_geojson(
            contour=contour,
            geojson_filepath=self.geojson_properties_file,
            min_angle_deg=self.config.min_angle_between_segments,
            ndigits=ndigits,
            unit=self.config.unit,
            stroke_width=5,
            geojson_properties=geojson_properties
        )
        self.assertTrue(os.path.exists(self.geojson_properties_file))
        self.assertTrue(filecmp.cmp(self.benchmark_geojson_properties_file, self.geojson_properties_file))
        os.remove(self.geojson_properties_file)

    def test_matplotlib_contourf_to_geojson(self):
        contourf = self.create_contourf()
        ndigits = 3
        geojsoncontour.contourf_to_geojson(
            contourf=contourf,
            geojson_filepath=self.geojson_file_multipoly,
            min_angle_deg=self.config.min_angle_between_segments,
            ndigits=ndigits,
            unit=self.config.unit
        )
        self.assertTrue(os.path.exists(self.geojson_file_multipoly))
        self.assertTrue(filecmp.cmp(self.benchmark_geojson_file_multipoly, self.geojson_file_multipoly))
        os.remove(self.geojson_file_multipoly)

    def test_matplotlib_contourf_to_geojson_overlap(self):
        contourf = self.create_contourf()
        ndigits = 3
        geojsoncontour.contourf_to_geojson_overlap(
            contourf=contourf,
            geojson_filepath=self.geojson_file_contourf,
            min_angle_deg=self.config.min_angle_between_segments,
            ndigits=ndigits,
            unit=self.config.unit
        )
        self.assertTrue(os.path.exists(self.geojson_file_contourf))
        self.assertTrue(filecmp.cmp(self.benchmark_geojson_file_contourf, self.geojson_file_contourf))
        os.remove(self.geojson_file_contourf)

    @staticmethod
    def create_grid_data():
        grid_size = 1.0
        lat_min = -90.0
        lat_max = 90.0
        lon_min = -180.0
        lon_max = 180.0
        latrange = numpy.arange(lat_min, lat_max, grid_size)
        lonrange = numpy.arange(lon_min, lon_max, grid_size)
        X, Y = numpy.meshgrid(lonrange, latrange)
        Z = numpy.sqrt(X*X + Y*Y)
        return latrange, lonrange, Z

    def test_orientation_order_gh31(self):
        # Flipping x should still result in CCW orientation
        # of final polygon
        x = numpy.linspace(0, 10, 14)[::-1]
        y = numpy.linspace(10, 20, 15)
        x, y = numpy.meshgrid(x, y)
        z = numpy.sin(x) * numpy.cos(y)
        contourf = plt.contourf(x, y, z)
        mp = geojsoncontour.contourf_to_geojson(contourf, ndigits=3)

class ContourPlotConfig(object):
    def __init__(self, level_lower=0.0, level_upper=100.0, colormap=plt.cm.jet, unit=''):  # jet, jet_r, YlOrRd, gist_rainbow
        self.n_contours = 10
        self.min_angle_between_segments = 15
        self.level_lower = level_lower
        self.level_upper = level_upper
        self.colormap = colormap
        self.unit = unit
        self.levels = numpy.linspace(
            start=self.level_lower,
            stop=self.level_upper,
            num=self.n_contours
        )


if __name__ == '__main__':
    unittest.main()
