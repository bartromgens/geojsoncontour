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
             cmap='viridis', levels=100, vmin=None, vmax=None):
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
               multipolys=True, *args, **kwargs):
    temp = _matplot(**_matplot_preprocessing(da))
    gjc.to_geojson(contour=temp, strdump=strdump,
                   geojson_filepath=geojson_filepath,
                   multipolys=multipolys, *args, **kwargs)


if __name__ == '__main__':
    curdir = os.path.dirname(__file__)
    relpath = '../tests/sresa1b_ncar_ccsm3-example.nc'
    da = xr.open_dataset(os.path.join(curdir, relpath)).tas
    if da.lon.units == 'degrees_east':
        midpoint = int(da.lon.size/2.)
        rot1 = da.shift(lon=-midpoint).dropna(dim='lon')
        rot1['lon'] = rot1['lon'] - 180
        rot2 = da.shift(lon=midpoint).dropna(dim='lon')
        rot2['lon'] = rot2['lon'] - 180
        da = xr.merge([rot1, rot2]).tas
    gjson = os.path.join(curdir, 'out_contourf.geojson')
    to_geojson(da, geojson_filepath=gjson, min_angle_deg=0, )
