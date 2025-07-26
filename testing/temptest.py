from herbie import Herbie
from toolbox import EasyMap, pc
import pytz
import numpy as np
import metpy
import matplotlib as mpl
from tutil import regions
import matplotlib.pyplot as plt
from datetime import datetime
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.colors import LinearSegmentedColormap, Normalize


est = pytz.timezone('US/Eastern')

region_coords = regions()
hour = 0


# "2024-06-29 12:00
H = Herbie("2022-12-24 12:00", model="hrrr", fxx=hour)
href = H.xarray(":RH:2 m")
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
bounds = np.array([0, 5, 10, 15, 20, 25, 30, 35, 40, 50, 60, 70, 80, 90, 100])
# Convert to Celsius (approximate)
linear_cmap = LinearSegmentedColormap.from_list("nws.rh", colors)
mpl.colormaps.register(cmap=linear_cmap, force=True)
norm = Normalize(bounds.min(), bounds.max())


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


sm = metpy.calc.smooth_gaussian(href.r2, 5)


p = ax.contour(
    href.longitude,
    href.latitude,
    sm,
    transform=pc,
    zorder=3,
    levels=np.linspace(0,100, 21),
    cmap="nws.rh",
    norm=norm
)
plt.clabel(p, inline=1, fontsize=10)
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
    f"{href.model.upper()}: 2 Meter Relative Humidity (%)\nValid: {valid.astimezone(est).strftime('%I:%M %p EST - %d %b %Y')}",
    loc="left",
)

ax.set_title(
    f"Hour: {str(hour)}\nInit: " + href.time.dt.strftime('%Hz - %d %b %Y').item(), loc="right")
plt.tight_layout()


plt.savefig("test" + str(hour+1) + ".png", bbox_inches='tight')
