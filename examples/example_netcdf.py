import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import geojsoncontour as gjc
import os


def _matplot_preprocessing(da, *args, **kwargs):
    if 'time' in da.dims:
        da = da.isel(time=0)
    assert da.dims == ('lat', 'lon'), "Not only lat,lon dimensions"
    lon = getattr(da, 'lon').data
    lat = getattr(da, 'lat').data
    X, Y = np.meshgrid(lon, lat)
    unit = getattr(da, 'units')
    name = getattr(da, 'name')
    Z = da.data
    return dict(X=X, Y=Y, Z=Z, unit=unit, name=name)


def _matplot(X, Y, Z, unit, name, contourtype='contourf',
             cmap='viridis', levels=30, vmin=None, vmax=None):
    if not vmin:
        vmin = np.nanmin(Z)
    if not vmax:
        vmax = np.nanmax(Z)
    _fig = plt.figure()
    _ax = _fig.add_subplot(111)
    contourtype = getattr(_ax, contourtype)
    cmap = getattr(plt.cm, cmap)
    levels = np.linspace(start=vmin, stop=vmax, num=levels)
    c = contourtype(X, Y, Z, levels=levels, cmap=cmap)
    setattr(c, 'da_name', name)
    setattr(c, 'da_unit', unit)
    return c


def to_geojson(da, strdump=False, geojson_filepath='out.geojson',
               multipolys=True):
    temp = _matplot(**_matplot_preprocessing(da))
    gjc.to_geojson(contour=temp, strdump=strdump,
                   geojson_filepath=geojson_filepath,
                   multipolys=multipolys)


if __name__ == '__main__':
    curdir = os.path.dirname(__file__)
    relpath = '../tests/sresa1b_ncar_ccsm3-example.nc'
    da = xr.open_dataset(os.path.join(curdir, relpath)).tas
    gjson = os.path.join(curdir, 'out.geojson')
    to_geojson(da, geojson_filepath=gjson)
