import fsspec
import cartopy.crs as ccrs
import kerchunk
from kerchunk.combine import MultiZarrToZarr
import json
import os
import xarray as xr
import dask
import matplotlib.pyplot as plt
import geopandas as gp
import boto3
import pandas as pd
import numpy as np


from datetime import date, datetime, timedelta
import panel as pn #version 0.9.5
import xarray as xr #version 0.11.3
import hvplot.xarray #version 0.5.2
import hvplot.pandas #version 0.5.2
import geoviews as gv #version 1.8.1
import cartopy.io.shapereader as shpreader



def make_kc_zarr_df(date,run):
    fs_s3 = fsspec.filesystem('s3', anon = False)
    #combined = fs_s3.glob(f"s3://arco-ibf/fcst/gefs_ens/{date}/{run}/gep*")
    year = date[:4]
    month = date[4:6]
    combined = fs_s3.glob(f"s3://s3-bucket-name/fcst/gefs_ens/{year}/{month}/{date}/{run}/gep*")
    combined1=['s3://'+f for f in combined]
    mzz = MultiZarrToZarr(combined1, 
                    remote_protocol='s3',
                    remote_options={'anon':False},
                    concat_dims = ['number'],
                    identical_dims = ['valid_time', 'longitude', 'latitude'])
    out = mzz.translate()
    fs_ = fsspec.filesystem("reference", fo=out, remote_protocol='s3', remote_options={'anon':True})
    m = fs_.get_mapper("")
    ds=xr.open_dataset(m, engine="zarr", backend_kwargs=dict(consolidated=False))
    return ds


# Note how I've removed the decorator
def make_plot(cropped_ds,dataset, memVal,timeVal):
    # Convert Date object to Datetime to work-around Date object / timedelta error panel was showing
    #sDate = datetime(dateVal.year, dateVal.month, dateVal.day)
    # create title string 
    quad_title = str("GEFS Ens Member" + str(memVal) + "Time Step"+ str(timeVal))
    #                datetime.strftime(sDate + timedelta(days=-1), "%Y-%m-%d"))
    # select data
    #df = cropped_ds.sel(time=[sDate],number=[0], method='nearest')         
    df = cropped_ds.isel(number=memVal,valid_time=timeVal)         
    #print(df)
    # create quadmesh plot
    #state_lines = shpreader.Reader('/home/bulbul/Documents/ea_shapefiles/ea_ghcf_icpac.shp')
    s3 = fsspec.filesystem("s3")
    json_file = "s3://s3-bucket-name/vectors/ea_ghcf_simple.json"

    with s3.open(json_file, "r") as f:
        geom = json.load(f)

    gdf = gp.GeoDataFrame.from_features(geom)
    #state_lines = gv.Shape.from_records(geom.records())
    shp = gv.Polygons(gdf).opts('Polygons', line_color='black',fill_color=None)
    chart = df.hvplot.quadmesh(x='longitude', y='latitude',project=True,geo=True,
                               title=quad_title, rasterize=True, dynamic=False) * shp
    #chart='hi'
    return chart



