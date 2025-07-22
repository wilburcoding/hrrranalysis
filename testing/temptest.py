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
href = H.xarray(":TMP:2 m")
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
linear_cmap = LinearSegmentedColormap.from_list("nws.temp", colors)
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


sm = metpy.calc.smooth_gaussian((href.t2m-273)*(9/5) + 32, 5)


p = ax.contour(
    href.longitude,
    href.latitude,
    sm,
    transform=pc,
    zorder=3,
    levels=np.linspace(-65, 125, 39),
    cmap="nws.temp",
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
    f"{href.model.upper()}: {href.t2m.GRIB_name}\nValid: {valid.astimezone(est).strftime('%I:%M %p EST - %d %b %Y')}",
    loc="left",
)

ax.set_title(
    f"Hour: {str(hour)}\nInit: " + href.time.dt.strftime('%Hz - %d %b %Y').item(), loc="right")
plt.tight_layout()


plt.savefig("test" + str(hour+1) + ".png", bbox_inches='tight')
