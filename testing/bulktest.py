from matplotlib.colors import LinearSegmentedColormap, Normalize
import cartopy.feature as cfeature
import cartopy.crs as ccrs
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from tutil import regions
import matplotlib as mpl
import sys
import time
import os
import shutil
import metpy
import numpy as np
import pytz
import xarray as xr
from herbie import Herbie


est = pytz.timezone('US/Eastern')

region_coords = regions()
hour = 0

# get current utc time
current_utc_time = datetime.now(pytz.utc)
while True:
    try:
        hour = 0
        H = Herbie(current_utc_time.strftime(
            '%Y-%m-%d %H:00'), model="hrrr", fxx=hour)
        href = H.xarray(":REFC:")
        print("Loaded successfully!")
        max_hours = 18 if current_utc_time.hour % 6 != 0 else 48
        existing = (os.listdir("./data"))
        contin = False
        if (current_utc_time.strftime('%Y-%m-%d-%H-00')) in existing:
            if (len(os.listdir("./data/" + current_utc_time.strftime('%Y-%m-%d-%H-00') + "/refc")) == max_hours+1):
                print("All hours already downloaded")
                current_utc_time = datetime.now(pytz.utc)

            else:
                hour = int(len(os.listdir(
                    "./data/" + current_utc_time.strftime('%Y-%m-%d-%H-00') + "/refc")))
                print("Starting at hour " + str(hour))
                contin = True
        else:
            print("Creating folders")
            dirs = (["./data/" + str(x) + "/" for x in os.listdir("./data")])
            if (len(dirs) == 10):
                oldest_directory = min(dirs, key=os.path.getmtime)
                shutil.rmtree(oldest_directory)
                os.rmdir(oldest_directory)
            os.mkdir("./data/" + current_utc_time.strftime('%Y-%m-%d-%H-00'))
            os.mkdir(
                "./data/" + current_utc_time.strftime('%Y-%m-%d-%H-00') + "/t2m")
            os.mkdir(
                "./data/" + current_utc_time.strftime('%Y-%m-%d-%H-00') + "/refc")
            os.mkdir(
                "./data/" + current_utc_time.strftime('%Y-%m-%d-%H-00') + "/sbcape")
            os.mkdir(
                "./data/" + current_utc_time.strftime('%Y-%m-%d-%H-00') + "/gust")
            os.mkdir(
                "./data/" + current_utc_time.strftime('%Y-%m-%d-%H-00') + "/r2m")
            os.mkdir(
                "./data/" + current_utc_time.strftime('%Y-%m-%d-%H-00') + "/ptype")

            contin = True
        if (contin == True):
            print("Starting downloading")
            while True:
                try:
                    now_time = datetime.now()
                    H = Herbie(current_utc_time.strftime(
                        '%Y-%m-%d %H:00'), model="hrrr", fxx=hour)
                    ds = H.xarray(
                        ":REFC:|(:TCDC:entire atmosphere)|:TMP:2 m|:CAPE:surface|:GUST:surface|:RH:2 m|:CSNOW:|:CICEP:|:CFRZR:|:CRAIN:|:PRATE:")  #
                    print(ds)
                    fig = plt.figure(figsize=(10, 8))
                    ax = plt.axes(projection=ccrs.PlateCarree())
                    ax.set_extent(
                        region_coords["Long Island"], ccrs.PlateCarree())

                    states = cfeature.NaturalEarthFeature(
                        category='cultural',
                        name='admin_1_states_provinces',
                        scale='10m',
                        facecolor='none'
                    )
                    href = ds[0]
                    ax.add_feature(cfeature.BORDERS.with_scale('10m'),
                                   linewidth=0.6, edgecolor="#9cc2ff", zorder=5)
                    ax.add_feature(cfeature.COASTLINE.with_scale(
                        '10m'), linewidth=0.6, edgecolor="#9cc2ff", zorder=5)
                    ax.add_feature(states, edgecolor='#9cc2ff',
                                   linewidth=0.7, zorder=5)
                    vmin = -32
                    norm = mpl.colors.Normalize(vmin=vmin, vmax=95)
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
                    cmap = LinearSegmentedColormap.from_list(
                        "custom_css_cmap", stops)

                    kw = {"norm": [], "cmap": []}
                    kw["norm"] = norm
                    kw["cmap"] = cmap
                    kw["cmap"].set_under("white")
                    sm = metpy.calc.smooth_gaussian(href.refc, 3)
                    norm2 = mpl.colors.Normalize(vmin=0.1, vmax=100)

                    sm2 = metpy.calc.smooth_gaussian(href.tcc, 3)
                    cmap2 = LinearSegmentedColormap.from_list(
                        "white gradient", [(93/255, 93/255, 93/255, 1), (1, 1, 1, 1)], N=100)
                    p = ax.pcolormesh(
                        href.longitude,
                        href.latitude,
                        sm,
                        zorder=4,
                        **kw
                    )
                    p2 = ax.pcolormesh(
                        href.longitude,
                        href.latitude,
                        sm2,
                        zorder=3,
                        norm=norm2,
                        cmap=cmap2,
                        shading='nearest'
                    )
                    ti = str(href.valid_time.dt.strftime(
                        "%Y-%m-%dT%H:%M:%S").item())
                    valid = datetime.strptime(ti, "%Y-%m-%dT%H:%M:%S")
                    valid = pytz.utc.localize(valid)
                    ax.set_title(
                        f"{href.model.upper()}: Maximum Reflectivity (dBZ)\nValid: {valid.astimezone(est).strftime('%I:%M %p EST - %d %b %Y')}",
                        loc="left",
                    )

                    ax.set_title(
                        f"Hour: {str(hour)}\nInit: " + href.time.dt.strftime('%Hz - %d %b %Y').item(), loc="right")
                    plt.tight_layout()

                    plt.savefig("./data/" + current_utc_time.strftime('%Y-%m-%d-%H-00') +
                                "/refc/" + str(hour) + ".png", bbox_inches='tight')
                    plt.clf()
                    print("REFC + TCC")
                    print(datetime.now() - now_time)

                    # TEMPERATURE (2 meter)

                    href = ds[1]

                    fig = plt.figure(figsize=(10, 8))
                    ax = plt.axes(projection=ccrs.PlateCarree())
                    ax.set_extent(
                        region_coords["Long Island"], ccrs.PlateCarree())

                    states = cfeature.NaturalEarthFeature(
                        category='cultural',
                        name='admin_1_states_provinces',
                        scale='10m',
                        facecolor='none'
                    )
                    colors = np.array(
                        [
                            "#91003f",
                            "#ce1256",
                            "#e7298a",
                            "#df65b0",
                            "#ff73df",
                            "#ffbee8",
                            "#ffffff",
                            "#dadaeb",
                            "#bcbddc",
                            "#9e9ac8",
                            "#756bb1",
                            "#54278f",
                            "#0d007d",
                            "#0d3d9c",
                            "#0066c2",
                            "#299eff",
                            "#4ac7ff",
                            "#73d7ff",
                            "#adffff",
                            "#30cfc2",
                            "#009996",
                            "#125757",
                            "#066d2c",
                            "#31a354",
                            "#74c476",
                            "#a1d99b",
                            "#d3ffbe",
                            "#ffffb3",
                            "#ffeda0",
                            "#fed176",
                            "#feae2a",
                            "#fd8d3c",
                            "#fc4e2a",
                            "#e31a1c",
                            "#b10026",
                            "#800026",
                            "#590042",
                            "#280028",
                        ]
                    )
                    # NWS bounds in Fahrenheit
                    bounds = np.linspace(-65, 125, len(colors) + 1)
                    # Convert to Celsius (approximate)
                    linear_cmap = LinearSegmentedColormap.from_list(
                        "nws.temp", colors)
                    mpl.colormaps.register(cmap=linear_cmap, force=True)
                    norm = mpl.colors.BoundaryNorm(bounds, linear_cmap.N)

                    ax.add_feature(cfeature.LAND.with_scale('10m'), edgecolor='black',
                                   zorder=1, facecolor="#282f40")

                    ax.add_feature(states, edgecolor='black',
                                   linewidth=0.4, zorder=4)
                    ax.add_feature(cfeature.RIVERS.with_scale(
                        '10m'), alpha=1, linewidth=0.3)
                    ax.add_feature(cfeature.OCEAN.with_scale('10m'),
                                   zorder=1, facecolor="#3c414d")
                    ax.add_feature(cfeature.BORDERS.with_scale(
                        '10m'), linewidth=0.2, zorder=4)
                    ax.add_feature(cfeature.COASTLINE.with_scale(
                        '10m'), linewidth=0.3, zorder=4)
                    sm = metpy.calc.smooth_gaussian(
                        (href.t2m-273)*(9/5) + 32, 5)
                    p = ax.pcolormesh(
                        href.longitude,
                        href.latitude,
                        sm,
                        zorder=3,
                        cmap="nws.temp",
                        linewidths=2,
                        norm=norm
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
                    ti = str(href.valid_time.dt.strftime(
                        "%Y-%m-%dT%H:%M:%S").item())
                    valid = datetime.strptime(ti, "%Y-%m-%dT%H:%M:%S")
                    valid = pytz.utc.localize(valid)
                    ax.set_title(
                        f"{href.model.upper()}: 2 Meter Temperature (F)\nValid: {valid.astimezone(est).strftime('%I:%M %p EST - %d %b %Y')}",
                        loc="left",
                    )

                    ax.set_title(
                        f"Hour: {str(hour)}\nInit: " + href.time.dt.strftime('%Hz - %d %b %Y').item(), loc="right")
                    plt.tight_layout()

                    plt.savefig("./data/" + current_utc_time.strftime('%Y-%m-%d-%H-00') +
                                "/t2m/" + str(hour) + ".png", bbox_inches='tight')
                    plt.clf()
                    fig = plt.figure(figsize=(10, 8))
                    ax = plt.axes(projection=ccrs.PlateCarree())
                    ax.set_extent(
                        region_coords["Long Island"], ccrs.PlateCarree())

                    states = cfeature.NaturalEarthFeature(
                        category='cultural',
                        name='admin_1_states_provinces',
                        scale='10m',
                        facecolor='none'
                    )
                    colors = np.array(
                        [
                            "#910022",
                            "#a61122",
                            "#bd2e24",
                            "#d44e33",
                            "#e36d42",
                            "#fa8f43",
                            "#fcad58",
                            "#fed884",
                            "#fff2aa",
                            "#e6f49d",
                            "#bce378",
                            "#71b55c",
                            "#26914b",
                            "#00572e",
                        ]
                    )
                    bounds = np.array(
                        [0, 5, 10, 15, 20, 25, 30, 35, 40, 50, 60, 70, 80, 90, 100])
                    # Convert to Celsius (approximate)
                    linear_cmap = LinearSegmentedColormap.from_list(
                        "nws.rh", colors)
                    mpl.colormaps.register(cmap=linear_cmap, force=True)
                    norm = mpl.colors.BoundaryNorm(bounds, linear_cmap.N)

                    ax.add_feature(cfeature.LAND.with_scale('10m'), edgecolor='black',
                                   zorder=1, facecolor="#282f40")

                    ax.add_feature(states, edgecolor='black',
                                   linewidth=0.4, zorder=4)
                    ax.add_feature(cfeature.RIVERS.with_scale(
                        '10m'), alpha=1, linewidth=0.3)
                    ax.add_feature(cfeature.OCEAN.with_scale('10m'),
                                   zorder=1, facecolor="#3c414d")
                    ax.add_feature(cfeature.LAKES.with_scale('10m'),
                                   alpha=1, linewidth=0.3, zorder=2)
                    ax.add_feature(cfeature.BORDERS.with_scale(
                        '10m'), linewidth=0.2, zorder=4)
                    ax.add_feature(cfeature.COASTLINE.with_scale(
                        '10m'), linewidth=0.3, zorder=4)

                    sm = metpy.calc.smooth_gaussian(href.r2, 5)

                    p = ax.pcolormesh(
                        href.longitude,
                        href.latitude,
                        sm,
                        zorder=3,
                        cmap="nws.rh",
                        norm=norm
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
                    ti = str(href.valid_time.dt.strftime(
                        "%Y-%m-%dT%H:%M:%S").item())
                    valid = datetime.strptime(ti, "%Y-%m-%dT%H:%M:%S")
                    valid = pytz.utc.localize(valid)
                    ax.set_title(
                        f"{href.model.upper()}: 2 Meter Relative Humidity (%)\nValid: {valid.astimezone(est).strftime('%I:%M %p EST - %d %b %Y')}",
                        loc="left",
                    )

                    ax.set_title(
                        f"Hour: {str(hour)}\nInit: " + href.time.dt.strftime('%Hz - %d %b %Y').item(), loc="right")
                    plt.tight_layout()

                    plt.savefig("./data/" + current_utc_time.strftime('%Y-%m-%d-%H-00') +
                                "/r2m/" + str(hour) + ".png", bbox_inches='tight')
                    plt.clf()
                    print("T2M + R2M")
                    print(datetime.now() - now_time)

                    # SURFACE BASED CAPE + GUST + PTYPE
                    href = ds[2]
                    fig = plt.figure(figsize=(10, 8))
                    ax = plt.axes(projection=ccrs.PlateCarree())
                    ax.set_extent(
                        region_coords["Long Island"], ccrs.PlateCarree())

                    states = cfeature.NaturalEarthFeature(
                        category='cultural',
                        name='admin_1_states_provinces',
                        scale='10m',
                        facecolor='none'
                    )

                    ax.add_feature(cfeature.LAND.with_scale(
                        '10m'), edgecolor='black', zorder=1)

                    ax.add_feature(states, edgecolor='black',
                                   linewidth=0.4, zorder=4)
                    ax.add_feature(cfeature.RIVERS.with_scale(
                        '10m'), alpha=1, linewidth=0.3)
                    ax.add_feature(cfeature.OCEAN.with_scale('10m'),
                                   alpha=1, linewidth=0.3, zorder=2)
                    ax.add_feature(cfeature.LAKES.with_scale('10m'),
                                   alpha=1, linewidth=0.3, zorder=2)
                    ax.add_feature(cfeature.BORDERS.with_scale(
                        '10m'), linewidth=0.2, zorder=4)
                    ax.add_feature(cfeature.COASTLINE.with_scale(
                        '10m'), linewidth=0.3, zorder=4)

                    vmin = 100
                    norm = mpl.colors.Normalize(vmin=vmin, vmax=10000)
                    # kw = cm_wind(units="mph").cmap_kwargs
                    # kw["norm"] = norm
                    # kw["cmap"].set_under("white")
                    rgbc = [[212, 212, 212], [186, 186, 186], [150, 150, 150],
                            [115, 115, 115], [77, 77, 77], [59, 59, 59]]
                    rgbc2 = []
                    lims = [[[135, 195, 255], [0, 43, 87]], [
                        [255, 210, 156], [173, 101, 14]], [[251, 255, 145], [205, 212, 21]], [[166, 255, 167], [6, 207, 8]], [[215, 156, 255], [118, 17, 186]]]
                    bounds = [100, 200, 400, 600, 800,
                              1000]
                    l = 1000
                    for item in lims:
                        up = item[0]
                        bo = item[1]
                        d1 = (bo[0] - up[0])/7.0
                        d2 = (bo[1] - up[1])/7.0
                        d3 = (bo[2] - up[2])/7.0
                        for i in range(7):
                            rgbc.append(
                                [up[0] + d1*i, up[1] + d2*i, up[2] + d3*i])
                        for i in range(5):
                            l += 200
                            bounds.append(l)

                    l += 200
                    bounds.append(l)
                    rgbc.append([255, 122, 244])  # Upper bound
                    for item in rgbc:
                        for i in range(3):
                            rgbc2.append(
                                [item[0]/255.0, item[1]/255.0, item[2]/255.0])
                    cmap = mpl.colors.ListedColormap(rgbc2)
                    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
                    cmap.set_under("white", alpha=0)
                    sm = metpy.calc.smooth_gaussian(href.cape, 3)

                    p = ax.pcolormesh(
                        href.longitude,
                        href.latitude,
                        sm,
                        zorder=3,
                        cmap=cmap,
                        norm=norm,
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
                    ti = str(href.valid_time.dt.strftime(
                        "%Y-%m-%dT%H:%M:%S").item())
                    valid = datetime.strptime(ti, "%Y-%m-%dT%H:%M:%S")
                    valid = pytz.utc.localize(valid)
                    ax.set_title(
                        f"{href.model.upper()}: Surface Based CAPE (J/kg)\nValid: {valid.astimezone(est).strftime('%I:%M %p EST - %d %b %Y')}",
                        loc="left",
                    )

                    ax.set_title(
                        f"Hour: {str(hour)}\nInit: " + href.time.dt.strftime('%Hz - %d %b %Y').item(), loc="right")
                    plt.tight_layout()

                    plt.savefig("./data/" + current_utc_time.strftime('%Y-%m-%d-%H-00') +
                                "/sbcape/" + str(hour) + ".png", bbox_inches='tight')
                    plt.clf()
                    fig = plt.figure(figsize=(10, 8))
                    ax = plt.axes(projection=ccrs.PlateCarree())
                    ax.set_extent(
                        region_coords["Long Island"], ccrs.PlateCarree())

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
                        [0.0, 5, 10, 15, 20, 25, 30, 35, 40, 45,
                            50, 60, 70, 80, 100, 120, 140, 160]
                    )
                    linear_cmap = LinearSegmentedColormap.from_list(
                        "nws.wind", colors)
                    mpl.colormaps.register(cmap=linear_cmap, force=True)
                    norm2 = mpl.colors.BoundaryNorm(bounds, linear_cmap.N)

                    ax.add_feature(states, edgecolor='black',
                                   linewidth=0.4, zorder=4)
                    ax.add_feature(cfeature.BORDERS.with_scale(
                        '10m'), linewidth=0.2, zorder=4)
                    ax.add_feature(cfeature.COASTLINE.with_scale(
                        '10m'), linewidth=0.3, zorder=4)

                    sm = metpy.calc.smooth_gaussian(href.gust*2.23694, 5)

                    p = ax.pcolormesh(
                        href.longitude,
                        href.latitude,
                        sm,
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
                    ti = str(href.valid_time.dt.strftime(
                        "%Y-%m-%dT%H:%M:%S").item())
                    valid = datetime.strptime(ti, "%Y-%m-%dT%H:%M:%S")
                    valid = pytz.utc.localize(valid)
                    ax.set_title(
                        f"{href.model.upper()}: Surface Wind Gusts (mph)\nValid: {valid.astimezone(est).strftime('%I:%M %p EST - %d %b %Y')}",
                        loc="left",
                    )

                    ax.set_title(
                        f"Hour: {str(hour)}\nInit: " + href.time.dt.strftime('%Hz - %d %b %Y').item(), loc="right")
                    plt.tight_layout()

                    plt.savefig("./data/" + current_utc_time.strftime('%Y-%m-%d-%H-00') +
                                "/gust/" + str(hour) + ".png", bbox_inches='tight')
                    plt.clf()
                    print("SBCAPE + GUST")
                    print(datetime.now() - now_time)

                    def func(sn, ice, fr, rain, prate):
                        threshold = 0.0005
                        result = np.zeros_like(prate, dtype=float)
                        prate = np.where((sn == 1) & (ice == 0) & (fr == 0) & (rain == 0),
                                         np.minimum(prate, 1.99/10),
                                         np.minimum(prate, 1.99/6))

                        # Condition 1: Only snow (sn=1, others=0) AND prate >= threshold -> 2 + prate
                        snow_only = (prate >= threshold) & (sn == 1) & (
                            ice == 0) & (fr == 0) & (rain == 0)
                        result = np.where(snow_only, prate*10, result)

                        # Condition 2: Only rain (rain=1, others=0) AND prate >= threshold -> prate
                        rain_only = (prate >= threshold) & (rain == 1) & (
                            sn == 0) & (ice == 0) & (fr == 0)
                        result = np.where(rain_only, 6+(prate*6), result)

                        # Condition 3: Only freezing (fr=1, others=0) AND prate >= threshold -> 4 + prate
                        fr_only = (prate >= threshold) & (fr == 1) & (
                            sn == 0) & (ice == 0) & (rain == 0)
                        result = np.where(fr_only, 2 + prate*6, result)

                        # Condition 4: Any weather condition present AND prate >= threshold -> 6 + prate
                        # (but not already covered by the specific single-condition cases above)
                        any_weather = (sn == 1) | (
                            ice == 1) | (fr == 1) | (rain == 1)
                        mixed_weather = (prate >= threshold) & any_weather & ~(
                            snow_only | rain_only | fr_only)
                        result = np.where(mixed_weather, 4 + prate*6, result)

                        # Apply threshold: set values under threshold to 0
                        result = np.where(result < threshold, 0, result)

                        return result

                    colors = [
                        (0.7, 0.9, 1.0, 1.0),      # Light blue (start of 0-2)
                        (0.0, 0.4, 0.8, 1.0),      # Dark blue (end of 0-2)
                        (1.0, 0.7, 0.8, 1.0),      # Light pink (start of 2-4)
                        (0.8, 0.2, 0.5, 1.0),      # Dark pink (end of 2-4)
                        (0.9, 0.7, 1.0, 1.0),      # Light purple (start of 4-6)
                        (0.5, 0.2, 0.8, 1.0),      # Dark purple (end of 4-6)
                        (0.7, 1.0, 0.7, 1.0),      # Light green (start of 6-8)
                        (0.2, 0.6, 0.2, 1.0)       # Dark green (end of 6-8)
                    ]

                    positions = [0.0, 0.25, 0.25, 0.5, 0.5, 0.75, 0.75, 1.0]
                    cmap = LinearSegmentedColormap.from_list('precipitation',
                                                             list(
                                                                 zip(positions, colors)),
                                                             N=256)

                    cmap.set_under(color=(0, 0, 0, 0))
                    norm = mpl.colors.Normalize(vmin=0.001, vmax=8)

                    mhref = xr.apply_ufunc(
                        func,
                        href.csnow, href.cicep, href.cfrzr, href.crain, metpy.calc.smooth_gaussian(
                            href.prate*0.0393701 * 3600, 5),
                    )
                    print(mhref.min())
                    print(mhref.max())

                    fig = plt.figure(figsize=(10, 8))
                    ax = plt.axes(projection=ccrs.PlateCarree())
                    ax.set_extent(
                        region_coords["Long Island"], ccrs.PlateCarree())

                    states = cfeature.NaturalEarthFeature(
                        category='cultural',
                        name='admin_1_states_provinces',
                        scale='10m',
                        facecolor='none'
                    )

                    ax.add_feature(cfeature.LAND.with_scale(
                        '10m'), edgecolor='black', zorder=1)
                    ax.add_feature(states, edgecolor='black',
                                   linewidth=0.4, zorder=4)
                    ax.add_feature(cfeature.RIVERS.with_scale(
                        '10m'), alpha=1, linewidth=0.3)
                    ax.add_feature(cfeature.OCEAN.with_scale('10m'),
                                   alpha=1, linewidth=0.3, zorder=2)
                    ax.add_feature(cfeature.LAKES.with_scale('10m'),
                                   alpha=1, linewidth=0.3, zorder=2)
                    ax.add_feature(cfeature.BORDERS.with_scale(
                        '10m'), linewidth=0.2, zorder=4)
                    ax.add_feature(cfeature.COASTLINE.with_scale(
                        '10m'), linewidth=0.3, zorder=4)
                    p = ax.pcolormesh(
                        href.longitude,
                        href.latitude,
                        mhref,
                        zorder=3,
                        cmap=cmap,
                        norm=norm

                    )
                    cbar = plt.colorbar(
                        p,
                        ax=ax,
                        orientation="horizontal",
                        pad=0.01,
                        shrink=0.7,
                        aspect=25,
                        spacing="proportional"
                    )
                    cbar.set_ticks([1, 3, 5, 7])
                    cbar.set_ticklabels(['Snow', "Ice", "Mix", "Rain"])
                    cbar.set_label("")
                    ti = str(href.valid_time.dt.strftime(
                        "%Y-%m-%dT%H:%M:%S").item())
                    valid = datetime.strptime(ti, "%Y-%m-%dT%H:%M:%S")
                    valid = pytz.utc.localize(valid)
                    ax.set_title(
                        f"{href.model.upper()}: Precipitation Type\nValid: {valid.astimezone(est).strftime('%I:%M %p EST - %d %b %Y')}",
                        loc="left",
                    )

                    ax.set_title(
                        f"Hour: {str(hour)}\nInit: " + href.time.dt.strftime('%Hz - %d %b %Y').item(), loc="right")
                    plt.tight_layout()

                    plt.savefig("./data/" + current_utc_time.strftime('%Y-%m-%d-%H-00') +
                                "/ptype/" + str(hour) + ".png", bbox_inches='tight')
                    plt.clf()
                    print(datetime.now() - now_time)
                    if (hour == max_hours):
                        break
                    else:
                        hour += 1
                except Exception as e:
                    print(e)
                    if ("No such file or directory" in str(e)):
                        os.mkdir(
                            "./data/" + current_utc_time.strftime('%Y-%m-%d-%H-00'))
                        os.mkdir(
                            "./data/" + current_utc_time.strftime('%Y-%m-%d-%H-00') + "/t2m")
                        os.mkdir(
                            "./data/" + current_utc_time.strftime('%Y-%m-%d-%H-00') + "/refc")
                        os.mkdir(
                            "./data/" + current_utc_time.strftime('%Y-%m-%d-%H-00') + "/sbcape")
                        os.mkdir(
                            "./data/" + current_utc_time.strftime('%Y-%m-%d-%H-00') + "/gust")
                        os.mkdir(
                            "./data/" + current_utc_time.strftime('%Y-%m-%d-%H-00') + "/r2m")
                        os.mkdir(
                            "./data/" + current_utc_time.strftime('%Y-%m-%d-%H-00') + "/ptype")

                    time.sleep(10)

        time.sleep(20)
        current_utc_time = datetime.now(pytz.utc)

    except Exception as e:

        print(e)
        print(current_utc_time.strftime('%Y-%m-%d %H:00'))

        current_utc_time = current_utc_time - timedelta(hours=1)
