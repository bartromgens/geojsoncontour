# geojsoncontour
A Python 3 module to convert matplotlib contour plots to geojson.

Designed to show geographical [contour plots](http://matplotlib.org/examples/pylab_examples/contour_demo.html), 
created with [matplotlib/pyplot](https://github.com/matplotlib/matplotlib), as vector layer on interactive maps interactive slippy maps like [OpenLayers](https://github.com/openlayers/ol3) and [Leaflet](https://github.com/Leaflet/Leaflet).

## Installation
The recommended way to install is via pip,
```
$ pip install geojsoncontour
```

## Usage
##### contour plot to geojson
```python
import numpy
import matplotlib.pyplot as plt
import geojsoncontour

# Create contour data lon_range, lat_range, Z
<your code here>

# Create a contour plot plot from grid (lat, lon) data
figure = plt.figure()
ax = figure.add_subplot(111)
contour = ax.contour(lon_range, lat_range, Z, levels=levels, cmap=plt.cm.jet)

# Convert matplotlib contour to geojson
geojsoncontour.contour_to_geojson(
    contour=contour,
    geojson_filepath='out.geojson',
    contour_labels=levels,
    ndigits=3,
    unit='m'
)

```
See [example1.py](geojsoncontour/examples/example1.py) for a basic but complete example.

### Show the geojson on a map
An easy way to show the generated geojson on a map is the online geojson renderer [geojson.io](http://geojson.io).

