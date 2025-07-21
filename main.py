from herbie import Herbie
from toolbox import EasyMap, pc
from paint.radar2 import cm_reflectivity
import pytz
import metpy
import os
import time
import sys
import matplotlib as mpl
from utils import regions
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.colors import LinearSegmentedColormap


est = pytz.timezone('US/Eastern')

region_coords = regions()
hour = 0

# get current utc time
current_utc_time = datetime.now(pytz.utc)
while True:
  try:
    H = Herbie(current_utc_time.strftime(
        '%Y-%m-%d %H:00'), model="hrrr", fxx=hour)
    href = H.xarray(":REFC:")
    print("Loaded successfully!")
    hour = 0
    max_hours = 18 if current_utc_time.hour % 6 != 0 else 48
    existing = (os.listdir("./data"))
    if (current_utc_time.strftime('%Y-%m-%d-%H-00')) in existing:
      if (len(os.listdir("./data/" + current_utc_time.strftime('%Y-%m-%d-%H-00') + "/")) == max_hours+1):
        print("All hours already downloaded")
        current_utc_time = datetime.now(pytz.utc)
      else:
        hour = len(os.listdir("./data/" + current_utc_time.strftime('%Y-%m-%d-%H-00') + "/"))
        print("Starting at hour " + str(hour))
    else:
      print("Creating folder")
      dirs = (["./data/" + str(x) +"/" for x in os.listdir("./data")])
      if (len(dirs) == 10):
        oldest_directory = min(dirs, key=os.path.getmtime)

        os.rmdir(oldest_directory)
      
      os.mkdir("./data/" + current_utc_time.strftime('%Y-%m-%d-%H-00'))
      sys.exit(1)
    while True:
      try:
        H = Herbie(current_utc_time.strftime(
            '%Y-%m-%d %H:00'), model="hrrr", fxx=hour)
        href = H.xarray(":REFC:")
        fig = plt.figure(figsize=(10, 8))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.set_extent(region_coords["Long Island"], ccrs.PlateCarree())

        states = cfeature.NaturalEarthFeature(
            category='cultural',
            name='admin_1_states_provinces',
            scale='10m',
            facecolor='none'
        )
        ax.add_feature(cfeature.LAKES.with_scale('10m'),
                      alpha=1, linewidth=0.3, zorder=1)

        ax.add_feature(cfeature.BORDERS.with_scale('10m'), linewidth=0.2)
        ax.add_feature(cfeature.COASTLINE.with_scale('10m'), linewidth=0.3)
        ax.add_feature(cfeature.LAND.with_scale('10m'), edgecolor='black')
        ax.add_feature(states, edgecolor='black', linewidth=0.4)
        ax.add_feature(cfeature.RIVERS.with_scale('10m'), alpha=1, linewidth=0.3)
        ax.add_feature(cfeature.OCEAN.with_scale('10m'),
                      alpha=1, linewidth=0.3, zorder=2)

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
        cmap = LinearSegmentedColormap.from_list("custom_css_cmap", stops)

        kw = cm_reflectivity().cmap_kwargs
        kw["norm"] = norm
        kw["cmap"] = cmap
        kw["cmap"].set_under("white")
        sm = metpy.calc.smooth_gaussian(href.refc, 3)


        p = ax.pcolormesh(
            href.longitude,
            href.latitude,
            sm,
            transform=pc,
            zorder=10,
            **kw
        )
        print(cm_reflectivity().cbar_kwargs)
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


        plt.savefig("./data/" + current_utc_time.strftime('%Y-%m-%d-%H-00') + "/" + str(hour) + ".png", bbox_inches='tight')

        if (hour == max_hours):
          break
        else:
          hour += 1
        plt.clf()
      except Exception as e:
        print(e)
        time.sleep(1)


    time.sleep(5)
    current_utc_time = datetime.now(pytz.utc)
      
  except Exception as e:

    print(e)
    print(current_utc_time.strftime('%Y-%m-%d %H:00'))

    current_utc_time = current_utc_time - timedelta(hours=1)

