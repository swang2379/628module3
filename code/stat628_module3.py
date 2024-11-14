import os
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Manager

airport_weather_map = pd.read_csv('closest.csv')

weather_columns = [
    'REPORT_TYPE', 'SOURCE', 'HourlyDewPointTemperature', 'HourlyDryBulbTemperature',
    'HourlyPrecipitation', 'HourlyPresentWeatherType', 'HourlyPressureChange',
    'HourlyPressureTendency', 'HourlyRelativeHumidity', 'HourlySeaLevelPressure',
    'HourlySkyConditions', 'HourlyStationPressure', 'HourlyVisibility',
    'HourlyWetBulbTemperature', 'HourlyWindDirection', 'HourlyWindGustSpeed', 'HourlyWindSpeed'
]

def load_weather_data(year):
    weather_folder = os.path.join('climate', f'{year}_data')
    weather_data = {}
    for filename in os.listdir(weather_folder):
        if filename.endswith(f'_{year}.csv'):
            station_id = filename[:-9]
            file_path = os.path.join(weather_folder, filename)

            if os.path.getsize(file_path) == 0:
                continue

            try:
                weather_df = pd.read_csv(file_path, encoding='ISO-8859-1', low_memory=False)
                if weather_df.empty or 'DATE' not in weather_df.columns:
                    continue

                weather_df['DATE'] = pd.to_datetime(weather_df['DATE'], errors='coerce')
                weather_df = weather_df.dropna(subset=['DATE']).sort_values('DATE')
                weather_data[station_id] = weather_df

            except pd.errors.EmptyDataError:
                continue

    return weather_data

def get_weather_for_time(station_id, flight_data, timezone, weather_data):
    if station_id not in weather_data:
        return pd.DataFrame()

    weather_df = weather_data[station_id]
    flight_data = flight_data.dropna(subset=[timezone])

    if flight_data.empty:
        return pd.DataFrame()

    merged_df = pd.merge_asof(
        flight_data.sort_values(timezone),
        weather_df.sort_values('DATE'),
        left_on=timezone,
        right_on='DATE',
        direction='backward'
    )
    return merged_df

def fetch_weather_data_for_batch(batch, weather_data):
    results = []
    for _, row in batch.iterrows():
        departure_station_id = airport_weather_map.loc[
            airport_weather_map['airport_local_code'] == row['Origin'], 'station_id'
        ].values[0] if not airport_weather_map.loc[
            airport_weather_map['airport_local_code'] == row['Origin'], 'station_id'
        ].empty else None

        arrival_station_id = airport_weather_map.loc[
            airport_weather_map['airport_local_code'] == row['Dest'], 'station_id'
        ].values[0] if not airport_weather_map.loc[
            airport_weather_map['airport_local_code'] == row['Dest'], 'station_id'
        ].empty else None

        if departure_station_id and not pd.isnull(row['CRSDepTime']):
            departure_weather = get_weather_for_time(departure_station_id, pd.DataFrame([row]), 'CRSDepTime', weather_data)
        else:
            departure_weather = pd.DataFrame()

        if arrival_station_id and not pd.isnull(row['CRSDepTime_Dest']):
            arrival_weather = get_weather_for_time(arrival_station_id, pd.DataFrame([row]), 'CRSDepTime_Dest', weather_data)
        else:
            arrival_weather = pd.DataFrame()

        for col in weather_columns:
            row[f'Departure_{col}'] = departure_weather[col].iloc[
                0] if not departure_weather.empty and col in departure_weather.columns else None
            row[f'Arrival_{col}'] = arrival_weather[col].iloc[
                0] if not arrival_weather.empty and col in arrival_weather.columns else None

        results.append(row)
    return results

def print_progress_bar(current, total, bar_length=40):
    progress = current / total
    arrow = '=' * int(progress * bar_length)
    spaces = ' ' * (bar_length - len(arrow))
    print(f"\r[{arrow}{spaces}] {current}/{total} processed", end="")

# 主程序
def main():
    with Manager() as manager:
        progress_bar = manager.Value('i', 0)

        for year in range(2018, 2024):
            print(f"\nProcessing data for year: {year}")
            flight_file = os.path.join('2_flight_merge', f'{year}.csv')
            flight_data = pd.read_csv(flight_file, low_memory=False)
            print('Finished reading flight data.')

            flight_data['CRSDepTime'] = pd.to_datetime(flight_data['CRSDepTime'], errors='coerce')
            flight_data['CRSDepTime_Dest'] = pd.to_datetime(flight_data['CRSDepTime_Dest'], errors='coerce')

            weather_data = load_weather_data(year)
            print('Finished reading weather data.')

            batch_size = 1000
            batches = [flight_data[i:i + batch_size] for i in range(0, len(flight_data), batch_size)]
            total_batches = len(batches)

            results = []
            with ProcessPoolExecutor(max_workers=16) as executor:
                for i, batch_result in enumerate(
                        executor.map(fetch_weather_data_for_batch, batches, [weather_data] * total_batches)):
                    results.extend(batch_result)
                    print_progress_bar(progress_bar.value + i + 1, total_batches)

            processed_data = pd.DataFrame(results)

            processed_data = processed_data[[
                'DayOfWeek', 'Origin', 'Dest', 'DepTime', 'CRSArrTime', 'ArrTime',
                'CRSDepTime', 'CRSDepTime_Dest', 'Cancelled', 'Marketing_Airline_Network'
            ] + [f'Departure_{col}' for col in weather_columns] + [f'Arrival_{col}' for col in weather_columns]]

            os.makedirs('Air_weather', exist_ok=True)
            final_path = os.path.join('Air_weather', f'{year}_airport_weather.csv')
            processed_data.to_csv(final_path, index=False)
            print(f"\nYear {year}: Data saved to {final_path}.")

if __name__ == "__main__":
    main()
