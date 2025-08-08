# HRRRAnalysis

This is a web application that allows users to view the outputs of weather forecasting models.
Data is downloaded from the AWS HRRR database and processed to generate images of certain fields (ex. radar, wind gust, 2 meter temperature), and the web application is used to access these images. 
There's a lot of other testing stuff (ex. images for different states, utility) that I'm unable to implement due to RAM and storage limitations on Nest (optimization has limited me to a maximum of 6 different fields).

To use the web application:
 - Use the sidebar to select a model run date and field
 - Use the slider underneath to select a hour

## Usage Instructions
Main data processing and image generation server
 - `matplolib`, `cartopy`, `metpy`, `pytz`, and `herbie-data` need to be installed using `conda install`
 - Command to run is `python main.py` (within conda prompt)

Web application
 - `Flask` needs to be installed using `pip install`
 - Command to run is `python server.py`
 
Local simple image generations with additional options
 - Multiple testing files in `/testing` directory
 - `matplolib`, `cartopy`, `metpy`, `pytz`, and `herbie-data` need to be installed using `conda install`
 - Command to run is `python ./testing/[FILE]` (within conda prompt)

