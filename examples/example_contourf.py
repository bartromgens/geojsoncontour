import numpy
import matplotlib.pyplot as plt
import geojsoncontour

# Create lat and lon vectors and grid data
grid_size = 1.0
latrange = numpy.arange(-90.0, 90.0, grid_size)
lonrange = numpy.arange(-180.0, 180.0, grid_size)
X, Y = numpy.meshgrid(lonrange, latrange)
Z = numpy.sqrt(X * X + Y * Y)

n_contours = 20
levels = numpy.linspace(start=0, stop=100, num=n_contours)

# Create a contour plot plot from grid (lat, lon) data
figure = plt.figure()
ax = figure.add_subplot(111)
contourf = ax.contourf(lonrange, latrange, Z, levels=levels, cmap=plt.cm.jet)

# Convert matplotlib contourf to geojson
geojson = geojsoncontour.contourf_to_multipolygeojson(
    contourf=contourf,
    contour_levels=levels,
    min_angle_deg=3.0,
    ndigits=3,
    stroke_width=2,
    fill_opacity=0.5
)

print(geojson)