# Flight Delays and Cancellations Project

This repository contains the data, code, image and analysis for the project on Flight Delays and Cancellations Project. Below is a summary of the repository structure and the contents of each folder.

## Repository Structure

### 1. Code Folder
This folder contains the code for data cleaning, analysis, and building the Shiny app:
1. **climate_download.ipynb**: A jupyter notebook file using API to down load historical climate data.
2. **visualization.ipynb**: A jupyter notebook file used to visualize data.
3. **stat628_module3.py**: A py file used to merge data.
4. **model.ipynb**: A jupyter notebook file used to fit data.
5. **app.py**: A py file used to create shiny app.
6. **STAT628_Module3_coding_part.ipynb**: A jupyter notebook file contains all the code used to clean and analysis data, and the shiny app part, including stat628_module3.py, model.ipynb and app.py.

### 2. Data Folder
This folder includes a .txt file containing a Google Drive link. In that Google Drive, there is a folder named data with data from three zips inside.
1. **1_flight.zip**: A zip file contians historical flight data on holiday season(Nov. 1st to Jan. 31st) from 2018 to 2024. The data is from [Bureau of Transportation Statistics](https://www.transtats.bts.gov/).
2. **climate.zip**: A zip file contians historical climate data on holiday season(Nov. 1st to Jan. 31st) from 2018 to 2024. The data is from [NCEI Object Store Explorer](https://www.ncei.noaa.gov/oa/local-climatological-data/index.html#v2/).
3. **combined_data.zip**: A zip file contians the merged and cleaned data on holiday season(Nov. 1st to Jan. 31st) from 2018 to 2024.

### 3. Image Folder
This folder contains 4 figures generated from the 2023 holiday season:
1. **Average Delay Time by Airline in 2023 Holiday season.png**: Bar chart showing average delay time for different airlines.
2. **Average Delay Time by Scheduled Arrival Time during 2023 Holiday Season.png**: Line chart showing the average delay times for different scheduled arrival time throughout the day across various days of the week.
3. **Average Delay Time by Scheduled Departure Time during 2023 Holiday Season.png**: Line chart showing the average delay time for different scheduled departure times throughout the day across various days of the week.
4. **Cancelled Rate by Airline in 2023 Holiday season.png**: Bar chart showing flight cancelled rate for different airlines.
5. **Cancelled Rate by Scheduled Departure Time during 2023 Holiday Season.png**: Line chart showing the flight cancelled rate for different scheduled departure times throughout the day across various days of the week.
6. **Random Forest Feature Importances for Cancel.png**: Line chart showing the random forest result of cancelled filghts model.
7. **Random Forest Feature Importances for Delay.png**: Line chart showing the random forest result of delay flights model.

