import os
import httpx
import asyncio
from dotenv import load_dotenv
from schemas import (
    GeoCoordinates,
    CurrentWeatherResponse,
    AirPollutionResponse,
    ForecastResponse
)

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

async def get_weather_data(city: str):
    async with httpx.AsyncClient() as client:
        # 1. Получаем координаты
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
        geo_resp = await client.get(geo_url)

        if geo_resp.status_code != 200 or not geo_resp.json():
            return None

        geo_data = GeoCoordinates(**geo_resp.json()[0])

        # 2. Подготовка ссылок
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={geo_data.lat}&lon={geo_data.lon}&appid={API_KEY}&units=metric&lang=ru"
        air_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={geo_data.lat}&lon={geo_data.lon}&appid={API_KEY}"
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={geo_data.lat}&lon={geo_data.lon}&appid={API_KEY}&units=metric&lang=ru"

        # ПАРАЛЛЕЛЬНЫЕ ЗАПРОСЫ
        responses = await asyncio.gather(
            client.get(weather_url),
            client.get(air_url),
            client.get(forecast_url)
        )

        if any(r.status_code != 200 for r in responses):
            return None

        return {
            "weather": CurrentWeatherResponse(**responses[0].json()),
            "air": AirPollutionResponse(**responses[1].json()),
            "forecast": ForecastResponse(**responses[2].json())
        }

async def get_weather_by_coords(lat: float, lon: float):
    async with httpx.AsyncClient() as client:
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=ru"
        air_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=ru"

        responses = await asyncio.gather(
            client.get(weather_url),
            client.get(air_url),
            client.get(forecast_url)
        )

        if any(r.status_code != 200 for r in responses):
            return None

        weather_data = responses[0].json()
        return {
            "city": weather_data.get("name", "Неизвестно"), # Извлекаем название города из API
            "weather": CurrentWeatherResponse(**weather_data),
            "air": AirPollutionResponse(**responses[1].json()),
            "forecast": ForecastResponse(**responses[2].json())
        }