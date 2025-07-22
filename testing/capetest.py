from herbie import Herbie
from toolbox import EasyMap, pc
from paint.radar2 import cm_reflectivity
import pytz
import metpy
import matplotlib as mpl
from tutil import regions
import matplotlib.pyplot as plt
from datetime import datetime
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.colors import LinearSegmentedColormap


est = pytz.timezone('US/Eastern')

region_coords = regions()

rklist = (list(region_coords.keys()))
for r in rklist:
    # aspect ratio
    coords = region_coords[r]
    print(r)
    print((coords[1] - coords[0]) / (coords[3] - coords[2]))
hour = 28


# "2024-06-29 12:00
H = Herbie("2025-07-19 18:00", model="hrrr", fxx=hour)
href = H.xarray(":CAPE:surface")
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
    rgbc.append([up[0] + d1*i, up[1] + d2*i, up[2] + d3*i])
  for i in range(5):
    l += 200
    bounds.append(l)

l += 200
bounds.append(l)
rgbc.append([255, 122, 244])  # Upper bound
for item in rgbc:
  for i in range(3):
    rgbc2.append([item[0]/255.0, item[1]/255.0, item[2]/255.0])
cmap = mpl.colors.ListedColormap(rgbc2)
norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
cmap.set_under("white", alpha=0)
sm = metpy.calc.smooth_gaussian(href.cape, 3)


p = ax.pcolormesh(
    href.longitude,
    href.latitude,
    sm,
    transform=pc,
    zorder=3,
    cmap=cmap,
    norm=norm,
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
    f"{href.model.upper()}: {href.cape.GRIB_name}\nValid: {valid.astimezone(est).strftime('%I:%M %p EST - %d %b %Y')}",
    loc="left",
)

ax.set_title(
    f"Hour: {str(hour)}\nInit: " + href.time.dt.strftime('%Hz - %d %b %Y').item(), loc="right")
plt.tight_layout()


plt.savefig("test" + str(hour+1) + ".png", bbox_inches='tight')
