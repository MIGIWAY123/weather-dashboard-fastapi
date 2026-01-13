from pydantic import BaseModel
from typing import List

# Вложенная модель для температуры
class MainWeatherData(BaseModel):
    temp: float
    humidity: int

# Вложенная модель для описания (пасмурно и т.д.)
class WeatherDescription(BaseModel):
    description: str
    icon: str

# Модель для текущей погоды
class CurrentWeatherResponse(BaseModel):
    main: MainWeatherData
    weather: List[WeatherDescription]

# Модель для координат (Geocoding)
class GeoCoordinates(BaseModel):
    lat: float
    lon: float

# Модель для качества воздуха
class AirPollutionMain(BaseModel):
    aqi: int

class AirPollutionItem(BaseModel):
    main: AirPollutionMain

class AirPollutionResponse(BaseModel):
    list: List[AirPollutionItem]

# Модель для прогноза
class ForecastItem(BaseModel):
    dt_txt: str
    main: MainWeatherData

class ForecastResponse(BaseModel):
    list: List[ForecastItem]