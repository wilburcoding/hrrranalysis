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
hour = 5


def func(sn, ice, fr, rain, prate):
    prate = np.where(prate < 0.01, 0, prate)
    result = np.zeros_like(prate)

    # Condition 1: Only snow (sn=1, others=0) -> 2 + prate
    snow_only = (sn == 1) & (ice == 0) & (fr == 0) & (rain == 0)
    result = np.where(snow_only, prate, result)

    # Condition 2: Only rain (rain=1, others=0) -> prate
    rain_only = (rain == 1) & (sn == 0) & (ice == 0) & (fr == 0)
    result = np.where(rain_only, 6+prate, result)

    # Condition 3: Only freezing (fr=1, others=0) -> 4 + prate
    fr_only = (fr == 1) & (sn == 0) & (ice == 0) & (rain == 0)
    result = np.where(fr_only, 2 + prate, result)

    # Condition 4: Any weather condition present -> 6 + prate
    # (but not already covered by the specific single-condition cases above)
    any_weather = (sn == 1) | (ice == 1) | (fr == 1) | (rain == 1)
    mixed_weather = any_weather & ~(snow_only | rain_only | fr_only)
    result = np.where(mixed_weather, 4 + prate, result)

    return result


colors = [
    (0.7, 0.9, 1.0),      # Light blue (start of 0-2)
    (0.0, 0.4, 0.8),      # Dark blue (end of 0-2)
    (1.0, 0.7, 0.8),      # Light pink (start of 2-4)
    (0.8, 0.2, 0.5),      # Dark pink (end of 2-4)
    (0.9, 0.7, 1.0),      # Light purple (start of 4-6)
    (0.5, 0.2, 0.8),      # Dark purple (end of 4-6)
    (0.7, 1.0, 0.7),      # Light green (start of 6-8)
    (0.2, 0.6, 0.2)       # Dark green (end of 6-8)
]

# Define the positions for each color (normalized to 0-1)
positions = [0.0, 0.25, 0.25, 0.5, 0.5, 0.75, 0.75, 1.0]

# Define the positions for each color (normalized to 0-1)
# We'll map: 0->0, 2->0.2, 4->0.4, 6->0.6, 10->1.0

# Create the colormap
cmap = LinearSegmentedColormap.from_list('precipitation',
                                         list(zip(positions, colors)),
                                         N=256)

# Set values <= 0 to be transparent
cmap.set_under(color=(0, 0, 0, 0))
norm = mpl.colors.Normalize(vmin=0.001, vmax=8)
# "2024-06-29 12:00
H = Herbie("2024-01-16 12:00", model="hrrr", fxx=hour)
href = H.xarray(":CSNOW:|:CICEP:|:CFRZR:|:CRAIN:|:PRATE:")
print(href)
print(href["csnow"])
mhref = xr.apply_ufunc(
    func,
    href.csnow, href.cicep, href.cfrzr, href.crain, href.prate*0.0393701 * 3600,
)
ne = href.prate*0.0393701 * 3600
print(ne.min())
print(ne.max())


fig = plt.figure(figsize=(10, 8))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent(region_coords["Long Island"], ccrs.PlateCarree())

states = cfeature.NaturalEarthFeature(
    category='cultural',
    name='admin_1_states_provinces',
    scale='10m',
    facecolor='none'
)

ax.add_feature(cfeature.LAND.with_scale('10m'), edgecolor='black', zorder=1)
ax.add_feature(states, edgecolor='black', linewidth=0.4, zorder=4)
ax.add_feature(cfeature.RIVERS.with_scale('10m'), alpha=1, linewidth=0.3)
ax.add_feature(cfeature.OCEAN.with_scale('10m'),
               alpha=1, linewidth=0.3, zorder=2)
ax.add_feature(cfeature.LAKES.with_scale('10m'),
               alpha=1, linewidth=0.3, zorder=2)
ax.add_feature(cfeature.BORDERS.with_scale('10m'), linewidth=0.2, zorder=4)
ax.add_feature(cfeature.COASTLINE.with_scale('10m'), linewidth=0.3, zorder=4)
p = ax.pcolormesh(
    href.longitude,
    href.latitude,
    mhref,
    zorder=4,
    transform=pc,
    cmap=cmap,
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
ti = str(href.valid_time.dt.strftime("%Y-%m-%dT%H:%M:%S").item())
valid = datetime.strptime(ti, "%Y-%m-%dT%H:%M:%S")
valid = pytz.utc.localize(valid)
ax.set_title(
    f"{href.model.upper()}: Precipitation Type\nValid: {valid.astimezone(est).strftime('%I:%M %p EST - %d %b %Y')}",
    loc="left",
)

ax.set_title(
    f"Hour: {str(hour)}\nInit: " + href.time.dt.strftime('%Hz - %d %b %Y').item(), loc="right")
plt.tight_layout()


plt.savefig("test" + str(hour+1) + ".png", bbox_inches='tight')
