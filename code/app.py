#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from shiny import App, ui, render, reactive, Session
from datetime import datetime
import pandas as pd
import folium
import nest_asyncio
import joblib
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import shiny

nest_asyncio.apply()

# Load data and models
airport_data = pd.read_csv("airport.csv")
weather_station_data = pd.read_csv("weather_station.csv")
closest_data = pd.read_csv("closest.csv")
test_data = pd.read_csv("combined_data.csv", low_memory=False)
cancel_model = joblib.load('cancel_model.pkl')
delay_model = joblib.load('delay_model.pkl')

# Data preparation
weather_station_data["station"] = weather_station_data["station"].str.strip()
closest_data["station_id"] = closest_data["station_id"].str.strip()
test_data["CRSDepTime"] = pd.to_datetime(test_data["CRSDepTime"], errors='coerce')
test_data["CRSArrTime"] = pd.to_datetime(test_data["CRSArrTime"], errors='coerce')

unique_airports = closest_data.merge(
    airport_data, how="left", left_on="airport_local_code", right_on="local_code"
).rename(columns={"latitude_deg": "Airport_Lat", "longitude_deg": "Airport_Long"})

filtered_weather_station_data = weather_station_data[
    weather_station_data["station"].isin(closest_data["station_id"])
].dropna(subset=["latitude", "longtitude"])

# Generate map HTML string
def generate_map_html(selected_airports=None):
    folium_map = folium.Map(location=[39.8283, -98.5795], zoom_start=4)
    for _, row in filtered_weather_station_data.iterrows():
        folium.CircleMarker(
            location=[row["latitude"], row["longtitude"]],
            radius=10,
            color="#db4e1e",
            weight=1,
            fill=True,
            fill_opacity=0.4,
            popup=f"Weather Station: {row['name']}"
        ).add_to(folium_map)
    
    for _, row in unique_airports.iterrows():
        color = "#ff7fef" if selected_airports and row["airport_local_code"] in selected_airports else "#00ffd6"
        weight = 10 if selected_airports and row["airport_local_code"] in selected_airports else 1
        folium.CircleMarker(
            location=[row["Airport_Lat"], row["Airport_Long"]],
            radius=10,
            color=color,
            fill=True,
            fill_opacity=0.6,
            weight=weight,
            popup=f"{row['airport_name']} ({row['airport_local_code']})"
        ).add_to(folium_map)
    
    return folium_map._repr_html_()

app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.style("""
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
            body { font-family: 'Montserrat', sans-serif; background-color: #97c1e7; }
            .title-panel { text-align: center; font-size: 30px; font-weight: bold; color: #00285e; }
            .control-label { color: #00285e; font-weight: bold; }
            .btn { background-color: #00285e; color: white; font-weight: bold; }
            .btn:hover, .btn:focus { background-color: #ffc758; color: #ee3124; font-weight: bold; }
            input, select, .selectize-input { background-color: #ffffff !important; }
        """)
    ),
    ui.output_ui("page_content")
)

# Page 1 UI
def page_one():
    return ui.page_fluid(
        ui.h2("Flight Information and Weather Data Retrieval", class_="title-panel"),
        ui.row(
            ui.column(4,
                ui.panel_well(
                    ui.h4("Input", class_="title-panel"),
                    ui.input_select("year", "Select Year", ["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]),
                    ui.input_date("departure_date", "Scheduled Departure Date", value="2018-11-01"),
                    ui.input_date("arrival_date", "Scheduled Arrival Date", value="2018-11-01"),
                    ui.input_text("departure_time", "Scheduled Departure Time (HH:MM)", value="12:00"),
                    ui.input_text("arrival_time", "Scheduled Arrival Time (HH:MM)", value="14:00"),
                    ui.input_selectize("departure_airport", "Departure Airport", sorted(unique_airports["airport_local_code"].unique()), options={"placeholder": "Enter airport code"}),
                    ui.input_selectize("arrival_airport", "Arrival Airport", sorted(unique_airports["airport_local_code"].unique()), options={"placeholder": "Enter airport code"}),
                    ui.input_action_button("get_weather", "Get Weather Data", class_="btn"),
                    ui.panel_well(
                        ui.h4("Output", class_="title-panel"),
                        ui.output_ui("weather_data_display")
                    ),
                ),
            ),
            ui.column(8,
                ui.panel_well(
                    ui.h4("Map Display", class_="title-panel"),
                    ui.output_ui("map_display"),
                )
            )
        ),
        ui.input_action_button("next_page", "Go to Analysis Page", class_="btn")
    )

# Page 2 UI with dynamic weather defaults
def page_two(weather_defaults):
    return ui.page_fluid(
        ui.h2("Flight Cancellation and Delay Prediction Analysis", class_="title-panel"),
        ui.row(
            ui.column(4,
                ui.panel_well(
                    ui.h4("Input Information", class_="title-panel"),
                    ui.input_select("year", "Select Year", ["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]),
                    ui.input_date("analysis_date", "Analysis Date", value="2018-11-01"),  # For reference
                    ui.input_select("ArrTimeOfDay_night", "Is Night Arrival (21:00-5:00)?", ["Yes", "No"]),
                    ui.input_selectize("departure_airport", "Departure Airport", sorted(unique_airports["airport_local_code"].unique()), options={"placeholder": "Enter airport code"}),
                    ui.input_selectize("arrival_airport", "Arrival Airport", sorted(unique_airports["airport_local_code"].unique()), options={"placeholder": "Enter airport code"}),
                    ui.input_numeric("Departure_HourlySeaLevelPressure", "Departure Sea Level Pressure", value=weather_defaults.get("Departure_HourlySeaLevelPressure", 1013)),
                    ui.input_numeric("Arrival_HourlySeaLevelPressure", "Arrival Sea Level Pressure", value=weather_defaults.get("Arrival_HourlySeaLevelPressure", 1015)),
                    ui.input_numeric("Departure_HourlyWetBulbTemperature", "Departure Wet Bulb Temp (°C)", value=weather_defaults.get("Departure_HourlyWetBulbTemperature", 18)),
                    ui.input_numeric("Arrival_HourlyWetBulbTemperature", "Arrival Wet Bulb Temp (°C)", value=weather_defaults.get("Arrival_HourlyWetBulbTemperature", 25)),
                    ui.input_numeric("Departure_HourlyDryBulbTemperature", "Departure Dry Bulb Temp (°C)", value=weather_defaults.get("Departure_HourlyDryBulbTemperature", 22)),
                    ui.input_numeric("Arrival_HourlyDryBulbTemperature", "Arrival Dry Bulb Temp (°C)", value=weather_defaults.get("Arrival_HourlyDryBulbTemperature", 23)),
                    ui.input_action_button("predict", "Predict", class_="btn")
                )
            ),
            ui.column(8,
                ui.panel_well(
                    ui.h4("Prediction Results", class_="title-panel"),
                    ui.panel_well(
                        ui.h4("Cancellation Prediction", class_="title-panel"),
                        ui.output_text("cancel_result")  # 添加取消结果的输出
                    ),
                    ui.panel_well(
                        ui.h4("Delay Prediction", class_="title-panel"),
                        ui.output_text("delay_result")  # 添加延迟结果的输出
                    )
                )
            )
        ),
        ui.input_action_button("prev_page", "Return to Data Page", class_="btn")
    )

# Server logic with date updating based on year selection
def server(input, output, session: Session):
    current_page = reactive.Value("page_one")
    weather_defaults = {}

    @output
    @render.ui
    def page_content():
        return page_one() if current_page() == "page_one" else page_two(weather_defaults)

    # Date updating logic based on the selected year
    @reactive.Effect
    def update_dates_based_on_year():
        selected_year = input.year()
        if selected_year in ["2018", "2019", "2020", "2021", "2022", "2023"]:
            default_date = f"{selected_year}-11-01"
            # 更新第一页的日期
            session.send_input_message("departure_date", {"value": default_date})
            session.send_input_message("arrival_date", {"value": default_date})

    # 切换到第二页时自动更新日期
    @reactive.Effect
    @reactive.event(input.next_page)
    def go_to_page_two():
        current_page.set("page_two")
        selected_year = input.year()
        if selected_year in ["2018", "2019", "2020", "2021", "2022", "2023"]:
            default_date = f"{selected_year}-11-01"
            session.send_input_message("analysis_date", {"value": default_date})

    @reactive.Effect
    @reactive.event(input.prev_page)
    def return_to_page_one():
        current_page.set("page_one")

    # Show map on the first page
    @output
    @render.ui
    def map_display():
        selected_airports = [input.departure_airport(), input.arrival_airport()]
        return ui.HTML(generate_map_html(selected_airports))

    @output
    @render.ui
    @reactive.event(input.get_weather)
    def weather_data_display():
        dep_airport = input.departure_airport()
        arr_airport = input.arrival_airport()
        dep_time = datetime.strptime(f"{input.departure_date()} {input.departure_time()}", "%Y-%m-%d %H:%M")
        arr_time = datetime.strptime(f"{input.arrival_date()} {input.arrival_time()}", "%Y-%m-%d %H:%M")

        weather_info = test_data[
            (test_data["Origin"] == dep_airport) &
            (test_data["Dest"] == arr_airport) &
            (test_data["CRSDepTime"] >= dep_time) &
            (test_data["CRSArrTime"] <= arr_time)
        ]

        if not weather_info.empty:
            row = weather_info.iloc[0]
            weather_data = {
                "Departure_HourlySeaLevelPressure": row.get("Departure_HourlySeaLevelPressure", "N/A"),
                "Arrival_HourlySeaLevelPressure": row.get("Arrival_HourlySeaLevelPressure", "N/A"),
                "Departure_HourlyWetBulbTemperature": row.get("Departure_HourlyWetBulbTemperature", "N/A"),
                "Arrival_HourlyWetBulbTemperature": row.get("Arrival_HourlyWetBulbTemperature", "N/A"),
                "Departure_HourlyDryBulbTemperature": row.get("Departure_HourlyDryBulbTemperature", "N/A"),
                "Arrival_HourlyDryBulbTemperature": row.get("Arrival_HourlyDryBulbTemperature", "N/A"),
            }
            weather_defaults.update(weather_data)
            table_rows = [ui.tags.tr(ui.tags.td(key), ui.tags.td(value)) for key, value in weather_data.items()]
            return ui.tags.table(*table_rows, style="width: 100%; border: 1px solid #ccc;")
        else:
            return ui.tags.div("No matching weather data found. Please check your inputs.", style="color: red; font-weight: bold;")

    @reactive.Effect
    @reactive.event(input.next_page)
    def go_to_page_two():
        current_page.set("page_two")

    @reactive.Effect
    @reactive.event(input.prev_page)
    def return_to_page_one():
        current_page.set("page_one")

    # Cancellation prediction, only triggered on "Predict" button click
    @output
    @render.text
    @reactive.event(input.predict)
    def cancel_result():
        arr_night = 1 if input.ArrTimeOfDay_night() == "Yes" else 0
        dest_airport = input.arrival_airport()
        dep_airport = input.departure_airport()
        dest_label = test_data[test_data["Dest"] == dest_airport]["Dest_Label"].iloc[0]
        origin_label = test_data[test_data["Origin"] == dep_airport]["Origin_Label"].iloc[0]

        cancel_data = [[arr_night, dest_label, input.Departure_HourlySeaLevelPressure(), 
                        input.Arrival_HourlySeaLevelPressure(), origin_label, 
                        input.Departure_HourlyWetBulbTemperature(), input.Arrival_HourlyWetBulbTemperature(), 
                        input.Departure_HourlyDryBulbTemperature(), input.Arrival_HourlyDryBulbTemperature(), 
                        int(input.year())]]
        cancel_prob = cancel_model.predict_proba(cancel_data)[0][1]
        cancel_prediction = "Yes" if cancel_prob > 0.5 else "No"
        return f"Cancellation Prediction: {cancel_prediction} (Probability: {cancel_prob:.2%})"

    # Delay prediction, only triggered on "Predict" button click
    @output
    @render.text
    @reactive.event(input.predict)
    def delay_result():
        arr_night = 1 if input.ArrTimeOfDay_night() == "Yes" else 0
        dest_airport = input.arrival_airport()
        dep_airport = input.departure_airport()
        dest_label = test_data[test_data["Dest"] == dest_airport]["Dest_Label"].iloc[0]
        origin_label = test_data[test_data["Origin"] == dep_airport]["Origin_Label"].iloc[0]
        
        delay_data = [[arr_night, dest_label, input.Departure_HourlySeaLevelPressure(), 
                       input.Arrival_HourlySeaLevelPressure(), origin_label, 
                       input.Departure_HourlyWetBulbTemperature(), input.Arrival_HourlyWetBulbTemperature(), 
                       input.Departure_HourlyDryBulbTemperature(), input.Arrival_HourlyDryBulbTemperature(), 
                       int(input.year())]]
        delay_time = delay_model.predict(delay_data)[0]
        delay_status = "On Time" if delay_time == 0 else ("Delayed" if delay_time > 0 else "Early")
        return f"Delay Prediction: {delay_status} (Time: {abs(delay_time):.2f} minutes)"

app = App(app_ui, server)
shiny.run_app(app, host="127.0.0.1", port=8000, launch_browser=True)

