from herbie import Herbie
from toolbox import EasyMap, pc
from paint.radar2 import cm_reflectivity
import pytz
import metpy
import os
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
    print(os.listdir("./data"))
    break
      
  except:
    print('ea')
    print(current_utc_time.strftime('%Y-%m-%d %H:00'))

    current_utc_time = current_utc_time - timedelta(hours=1)

