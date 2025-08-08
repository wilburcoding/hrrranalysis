# HRRRAnalysis

This is a web application that allows users to view the outputs of weather forecasting models.
Data is downloaded from the AWS HRRR database and processed to generate images of certain fields (ex. radar, wind gust, 2 meter temperature), and the web application is used to access these images. 
There's a lot of other testing stuff (ex. images for different states, utility) that I'm unable to implement due to RAM and storage limitations on Nest (optimization has limited me to a maximum of 6 different fields).

To use the web application:
 - Use the sidebar to select a model run date and field
 - Use the slider underneath to select a hour