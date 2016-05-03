import os
import unittest
import filecmp

import numpy
import matplotlib.pyplot as plt

import geojsoncontour


class TestContourToGeoJson(unittest.TestCase):
    dirname = os.path.dirname(__file__)
    geojson_file = os.path.join(dirname, 'test1.geojson')
    benchmark_geojson_file = os.path.join(dirname, 'benchmark_test1.geojson')

    def setUp(self):
        if os.path.exists(self.geojson_file):
            os.remove(self.geojson_file)

    def test_matplotlib_contour_to_geojson(self):
        latrange, lonrange, Z = self.create_grid_data()
        config = ContourPlotConfig(level_lower=0, level_upper=202)

        figure = plt.figure()
        ax = figure.add_subplot(111)
        contours = ax.contour(
            lonrange, latrange, Z,
            levels=config.levels,
            cmap=config.colormap
        )

        ndigits = 3
        geojsoncontour.contour_to_geojson(
            contour=contours,
            geojson_filepath=self.geojson_file,
            contour_labels=config.levels,
            min_angle_deg=config.min_angle_between_segments,
            ndigits=ndigits,
            unit=config.unit
        )
        self.assertTrue(os.path.exists(self.geojson_file))
        self.assertTrue(filecmp.cmp(self.benchmark_geojson_file, self.geojson_file))
        os.remove(self.geojson_file)

    def create_grid_data(self):
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


class ContourPlotConfig(object):
    def __init__(self, level_lower=0, level_upper=100, colormap=plt.cm.jet, unit=''):  # jet, jet_r, YlOrRd, gist_rainbow
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