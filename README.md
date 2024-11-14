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

### 4. Summary File
- **STAT628 Module3 Summary.pdf.pdf**: A two-page summary of the project, including an overview of the analysis and key findings.

### 5. Presentation
- **stat628_group8_module3.pptx**: The final presentation slides used during the project presentation.

## How to Use the Code

### Prerequisites
Make sure you have R and the necessary packages installed `FNN`, `ggplot`, `glmnet`, `car`, `shiny`. You can install missing packages with the following command:

```bash
pip install scikit-learn matplotlib glmnet statsmodels shiny
```
The version for these packages are shown below:
- scikit-learn>=1.1.4
- matplotlib>=3.5.1
- glmnet>=4.1.8
- statsmodels>=0.14.0
- shiny>=1.9.1

  
## Running the Analysis
1. Open and run **analysis.Rmd** to perform the data cleaning, model building, and analysis.
2. If you want to see the Shiny app, use [Shiny App](https://stat628module3.shinyapps.io/apppy/).

## Contact
For any questions or inquiries about this project, feel free to contact:
- **Meiyi Yan**: myan49@wisc.edu
- **Siyu Wang**: swang2379@wisc.edu
- **Minyuan Zhao**: mzhao246@wisc.edu

## Acknowledgements
We would like to thank all contributors and open-source libraries used in this project.

## Contributing
Contributions are welcome! If you have suggestions or improvements, feel free to open an issue or submit a pull request. Please review the contribution guidelines in the `CONTRIBUTING.md` file.
