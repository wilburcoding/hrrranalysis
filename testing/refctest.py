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
for hour in range(1):

    H = Herbie("2024-08-10 12:00", model="hrrr", fxx=hour)

    href = H.xarray(":REFC:|(:TCDC:entire atmosphere:anl)")
    print(href)
    fig = plt.figure(figsize=(10, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([-74.76189,-71.78799, 40.496105, 41.7138137], ccrs.PlateCarree())

    states = cfeature.NaturalEarthFeature(
        category='cultural',
        name='admin_1_states_provinces',
        scale='10m',
        facecolor='none'
    )
    
    ax.add_feature(cfeature.LAKES.with_scale('10m'),
                   alpha=1, facecolor="none", zorder=5, linewidth=0.4, edgecolor="#9cc2ff")
    ax.add_feature(cfeature.BORDERS.with_scale('10m'),
                linewidth=0.6, edgecolor="#9cc2ff", zorder=5)
    ax.add_feature(cfeature.COASTLINE.with_scale(
        '10m'), linewidth=0.6, edgecolor="#9cc2ff", zorder=5)
    ax.add_feature(states, edgecolor='#9cc2ff', linewidth=0.7, zorder=5)
    
    

    vmin = -32
    norm = mpl.colors.Normalize(vmin=vmin, vmax=95)
    norm2 = mpl.colors.Normalize(vmin=0.1, vmax=100)
    stops = [
        (0.00, (0, 0, 0, 0)),
        (0.2913, (0, 0, 0, 0)),
        (0.2913, (29, 37, 60, 1)),
        (0.3858, (89, 155, 171, 1)),
        (0.4252, (33, 186, 72, 1)),
        (0.5039, (5, 101, 1, 1)),
        (0.5433, (251, 252, 0, 1)),
        (0.5827, (199, 176, 0, 1)),
        (0.5827, (253, 149, 2, 1)),
        (0.6457, (172, 92, 2, 1)),
        (0.6457, (253, 38, 0, 1)),
        (0.7244, (135, 43, 22, 1)),
        (0.7244, (193, 148, 179, 1)),
        (0.8031, (200, 23, 119, 1)),
        (0.8031, (165, 2, 215, 1)),
        (0.8425, (64, 0, 146, 1)),
        (0.8425, (135, 255, 253, 1)),
        (0.8819, (54, 120, 142, 1)),
        (0.8819, (173, 99, 64, 1)),
        (0.9213, (105, 0, 4, 1)),
        (1.00, (0, 0, 0, 1))
    ]

    # Convert RGBA 0–255 → 0–1
    stops = [(pos, tuple(c/255 for c in color[:3]) + (color[3],))
            for pos, color in stops]

    # Build the colormap
    cmap = LinearSegmentedColormap.from_list("custom_css_cmap", stops)
    kw = {}

    kw["norm"] = norm
    kw["cmap"] = cmap
    kw["cmap"].set_under("white")
    sm = metpy.calc.smooth_gaussian(href.refc, 3)
    sm2 = metpy.calc.smooth_gaussian(href.tcc, 3)

    N = 256
    cmap2 = LinearSegmentedColormap.from_list(
        "white gradient", [(93/255, 93/255, 93/255, 1), (1, 1, 1, 1)], N=100)
    p = ax.pcolormesh(
        href.longitude,
        href.latitude,
        sm,
        transform=pc,
        zorder=4,
        **kw
    )
    p2 = ax.pcolormesh(
        href.longitude,
        href.latitude,
        sm2,
        transform=pc,
        zorder=3,
        norm=norm2,
        cmap=cmap2,
        shading='nearest'
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
        f"{href.model.upper()}: {href.refc.GRIB_name}\nValid: {valid.astimezone(est).strftime('%I:%M %p EST - %d %b %Y')}",
        loc="left",
    )

    ax.set_title(
        f"Hour: {str(hour)}\nInit: " + href.time.dt.strftime('%Hz - %d %b %Y').item(), loc="right")
    plt.tight_layout()
    plt.savefig("testoutput/" + str(hour+1) + ".png", bbox_inches='tight')
    print(datetime.now() - now_time)
