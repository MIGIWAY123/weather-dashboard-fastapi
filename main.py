import plotly.express as px
import plotly.io as pio
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from services import get_weather_data, get_weather_by_coords
from database import init_db, add_to_history, get_recent_history

init_db()
app = FastAPI()
templates = Jinja2Templates(directory="templates")

AQI_DESCRIPTION = {
    1: ("Отлично", "text-success"),
    2: ("Приемлемо", "text-info"),
    3: ("Средне", "text-warning"),
    4: ("Вредно", "text-danger"),
    5: ("Опасно", "text-dark font-weight-bold")
}

# Вспомогательная функция для рендеринга страницы (убирает NameError)
async def render_weather_page(request: Request, city: str, data: dict):
    weather = data["weather"]
    air = data["air"]
    forecast = data["forecast"]

    temp = round(weather.main.temp)
    # Добавляем в историю (из database.py)
    add_to_history(city, temp)

    # Определяем цвет фона
    if temp <= 0:
        bg_class = "bg-cold"
    elif 0 < temp <= 20:
        bg_class = "bg-mild"
    elif 20 < temp <= 30:
        bg_class = "bg-warm"
    else:
        bg_class = "bg-hot"

    # Качество воздуха
    raw_aqi = air.list[0].main.aqi
    aqi_text, aqi_class = AQI_DESCRIPTION.get(raw_aqi, ("Нет данных", "text-muted"))

    # Создание графика через Plotly
    forecast_list = forecast.list[:8]
    times = [item.dt_txt for item in forecast_list]
    temps = [item.main.temp for item in forecast_list]

    fig = px.line(
        x=times,
        y=temps,
        title=f"Прогноз: {city.capitalize()}",
        labels={'x': 'Время', 'y': 'Температура (°C)'}
    )
    graph_html = pio.to_html(fig, full_html=False, include_plotlyjs='cdn')

    return templates.TemplateResponse("index.html", {
        "request": request,
        "city": city,
        "temp": temp,
        "bg_class": bg_class,
        "desc": weather.weather[0].description,
        "icon": weather.weather[0].icon,
        "humidity": weather.main.humidity,
        "aqi_text": aqi_text,
        "aqi_class": aqi_class,
        "history": get_recent_history(),
        "graph_html": graph_html
    })

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    history = get_recent_history()
    return templates.TemplateResponse("index.html", {"request": request, "history": history})

@app.post("/weather", response_class=HTMLResponse)
async def weather_report(request: Request, city: str = Form(...)):
    data = await get_weather_data(city)
    if not data:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "Город не найден или API ошибка",
            "history": get_recent_history()
        })
    return await render_weather_page(request, city, data)

@app.get("/weather_by_coords", response_class=HTMLResponse)
async def weather_by_coords(request: Request, lat: float, lon: float):
    data = await get_weather_by_coords(lat, lon)
    if not data:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "Ошибка получения данных по GPS",
            "history": get_recent_history()
        })
    return await render_weather_page(request, data["city"], data)