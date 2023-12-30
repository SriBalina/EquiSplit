from multiprocessing.sharedctypes import Value
import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

API_KEY = "4a39c4159c2baebee624d9f03d854bbd"

def find_current_weather(city):
    base_url  = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    weather_data = requests.get(base_url).json()
    try:
        general = weather_data['weather'][0]['main']
        icon_id = weather_data['weather'][0]['icon']
        temperature = round(weather_data['main']['temp'])
        icon = f"http://openweathermap.org/img/wn/{icon_id}@2x.png"
        wind_speed = weather_data['wind']["speed"]
        hmdt = weather_data['main']['humidity']
        max_temp = weather_data['main']['temp_max']
    except KeyError:
        st.error("City Not Found")
        st.stop()
    return general, temperature, icon, wind_speed, hmdt, max_temp

def get_weather_forecast(city, days=3):
    base_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    weather_data = requests.get(base_url).json()
    
    forecast = []
    for i in range(days):
        date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
        daily_data = [x for x in weather_data["list"] if date in x["dt_txt"]]
        if daily_data:
            forecast.append({
                'date': date,
                'temperature': round(daily_data[0]['main']['temp']),
                'icon': f"http://openweathermap.org/img/wn/{daily_data[0]['weather'][0]['icon']}@2x.png",
                'general': daily_data[0]['weather'][0]['main'],
                'wind_speed': daily_data[0]['wind']['speed'],
                'humidity': daily_data[0]['main']['humidity'],
                'max_temp': daily_data[0]['main']['temp_max']
            })
    return forecast

def visualize_forecast(forecast_data):
    df = pd.DataFrame(forecast_data)
    
    # Line chart for temperature
    fig_temp = px.line(df, x='date', y='temperature', title='Temperature Forecast')
    fig_temp.update_layout(xaxis_title='Date', yaxis_title='Temperature (°C)')

    # Bar chart for humidity
    fig_humidity = px.bar(df, x='date', y='humidity', title='Humidity Forecast')
    fig_humidity.update_layout(xaxis_title='Date', yaxis_title='Humidity (%)')

    st.plotly_chart(fig_temp)
    st.plotly_chart(fig_humidity)

def main():
    st.header("Find the Weather")
    default_city = "India"
    city = st.text_input("Enter the place", default_city).lower()
    days_to_forecast = st.slider("Select number of days to forecast", 1, 5, 3)

    if st.button("Find"):
        general, temperature, icon, wind_speed, hmdt, max_temp = find_current_weather(city)

        date = datetime.now().strftime("%d %b %Y | %I:%M:%S %p")

        st.write("#### Current Weather stats for : {},  {}".format(city.upper(), date))
        col_1, col_2, col_3 = st.columns(3)
        with col_1:
            st.metric(label="Temperature", value=f"{temperature}°C")
            st.metric(label="Humidity", value=f"{hmdt}%")
        with col_2:
            st.metric(label="Weather description", value=f"{general}")
            st.image(icon)
        with col_3:
            st.metric(label="Wind Speed", value=f"{wind_speed}kmph")
            st.metric(label="Max Temperature", value=f"{max_temp}")

        # Future forecast
        forecast_data = get_weather_forecast(city, days=days_to_forecast)
        st.subheader(f"Weather Forecast for the next {days_to_forecast} days:")
        visualize_forecast(forecast_data)
        for forecast in forecast_data:
            st.write(f"### {forecast['date']}")
            st.image(forecast['icon'])
            st.write(f"**Temperature:** {forecast['temperature']}°C")
            st.write(f"**Weather description:** {forecast['general']}")
            st.write(f"**Wind Speed:** {forecast['wind_speed']} kmph")
            st.write(f"**Humidity:** {forecast['humidity']}%")
            st.write(f"**Max Temperature:** {forecast['max_temp']}°C")
            st.write("---")


if __name__ == '__main__':
    main()
