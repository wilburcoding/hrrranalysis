from herbie import Herbie
from toolbox import EasyMap, pc
import pytz
import numpy as np
import metpy
import matplotlib as mpl
from tutil import regions
import xarray as xr
import matplotlib.pyplot as plt
from datetime import datetime
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.colors import LinearSegmentedColormap, Normalize


est = pytz.timezone('US/Eastern')

region_coords = regions()
now_time = datetime.now()
for hour in range(17):

    H = Herbie("2025-07-28 18:00", model="hrrr", fxx=hour)
    href = H.xarray(":GUST:surface")
    fig = plt.figure(figsize=(10, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent(region_coords["Long Island"], ccrs.PlateCarree())

    states = cfeature.NaturalEarthFeature(
        category='cultural',
        name='admin_1_states_provinces',
        scale='10m',
        facecolor='none'
    )
    colors = np.array(
        [
            "#103f78",
            "#225ea8",
            "#1d91c0",
            "#41b6c4",
            "#7fcdbb",
            "#b4d79e",
            "#dfff9e",
            "#ffffa6",
            "#ffe873",
            "#ffc400",
            "#ffaa00",
            "#ff5900",
            "#ff0000",
            "#a80000",
            "#6e0000",
            "#ffbee8",
            "#ff73df",
        ]
    )
    bounds = np.array(
        [0.0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 100, 120, 140, 160]
    )
    linear_cmap = LinearSegmentedColormap.from_list("nws.wind", colors)
    mpl.colormaps.register(cmap=linear_cmap, force=True)
    norm2 = mpl.colors.BoundaryNorm(bounds, linear_cmap.N)


    ax.add_feature(cfeature.LAND.with_scale('10m'), edgecolor='black',
                zorder=1, facecolor="#282f40")

    ax.add_feature(states, edgecolor='black', linewidth=0.4, zorder=4)
    ax.add_feature(cfeature.RIVERS.with_scale('10m'), alpha=1, linewidth=0.3)
    ax.add_feature(cfeature.OCEAN.with_scale('10m'), facecolor="#282f40",
                alpha=0.4, linewidth=0.3, zorder=2)
    ax.add_feature(cfeature.LAKES.with_scale('10m'),
                alpha=1, linewidth=0.3, zorder=2)
    ax.add_feature(cfeature.BORDERS.with_scale('10m'), linewidth=0.2, zorder=4)
    ax.add_feature(cfeature.COASTLINE.with_scale('10m'), linewidth=0.3, zorder=4)


    sm = metpy.calc.smooth_gaussian(href.gust*2.23694, 5)


    p = ax.pcolormesh(
        href.longitude,
        href.latitude,
        sm,
        transform=pc,
        zorder=3,
        cmap="nws.wind",
        norm=norm2
    )
    plt.colorbar(
        p,
        ax=ax,
        orientation="horizontal",
        pad=0.01,
        shrink=0.7,
        aspect=25,
        label="",
        spacing="proportional"
    )
    ti = str(href.valid_time.dt.strftime("%Y-%m-%dT%H:%M:%S").item())
    valid = datetime.strptime(ti, "%Y-%m-%dT%H:%M:%S")
    valid = pytz.utc.localize(valid)
    ax.set_title(
        f"{href.model.upper()}: {href.gust.GRIB_name}\nValid: {valid.astimezone(est).strftime('%I:%M %p EST - %d %b %Y')}",
        loc="left",
    )

    ax.set_title(
        f"Hour: {str(hour)}\nInit: " + href.time.dt.strftime('%Hz - %d %b %Y').item(), loc="right")
    plt.tight_layout()


    plt.savefig("testoutput/" + str(hour+1) + ".png", bbox_inches='tight')
    print(datetime.now() - now_time)
