#!/usr/bin/python3.4
# -*- encoding: utf-8 -*-
"""Helper module for transformation of netCDF to GeoJSON."""

import xarray as xr
from matplotlib import pyplot as plt
import numpy as np
import geojsoncontour
import os
import sys


def load(ncfile):
    return xr.open_dataset(ncfile)


def get_lat_lon_vars(ncdataset):
    return [k for k, _ in ncdataset.variables.items()
            if ('lat' in getattr(ncdataset, k).dims and
                'lon' in getattr(ncdataset, k).dims and
                'time' in getattr(ncdataset, k).dims and
                len(getattr(ncdataset, k).dims) == 3 and
                k[-5:] != '_bnds' and
                k != 'msk_rgn'
                )]


def setup(filename, var):
    data = xr.open_dataset(filename)
    lon_range = data.variables['lon'].data
    lat_range = data.variables['lat'].data
    lon_range, lat_range
    X, Y = np.meshgrid(lon_range, lat_range)
    mini = np.nanmin(data.variables[var].data)
    maxi = np.nanmax(data.variables[var].data)
    unit = data.variables[var].attrs['units']
    n_contours = 20
    levels = np.linspace(start=mini, stop=maxi, num=n_contours)
    Z = getattr(data, var)
    return X, Y, Z, levels, unit


def netcdf_to_geojson(ncfile, var, fourth_dim=None):
    realpath = os.path.realpath(ncfile)
    name, ext = os.path.splitext(realpath)
    X, Y, Z, levels, unit = setup(ncfile, var)
    figure = plt.figure()
    ax = figure.add_subplot(111)
    for t in range(len(Z.time)):
        third = Z.isel(time=t)
        position = 0
        if len(third.dims) == 3:
            position = len(getattr(third, third.dims[0]))-1
            third = third[position, ]
        # local min max
        levels = np.linspace(start=np.nanmin(third),
                             stop=np.nanmax(third), num=20)
        contourf = ax.contourf(X, Y, third, levels=levels, cmap=plt.cm.viridis)
        geojsoncontour.contourf_to_geojson(
            contourf=contourf,
            geojson_filepath='{}_{}_t{}_{}.geojson'.format(name, var,
                                                           t, position),
            ndigits=3,
            min_angle_deg=None,
            unit=unit
        )


if __name__ == '__main__':
    nc = sys.argv[1]
    var = sys.argv[2]
    netcdf_to_geojson(nc, var)
