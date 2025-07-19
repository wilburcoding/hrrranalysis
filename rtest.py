from utils import regions

region_coords = regions()
rklist = (list(region_coords.keys()))


for r in rklist:
  # aspect ratio
  coords = region_coords[r]
  print(r)
  print((coords[1] - coords[0]) / (coords[3] - coords[2]))