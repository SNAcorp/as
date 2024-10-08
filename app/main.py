import httpx
import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import redis
from starlette.responses import JSONResponse

app = FastAPI()

# Настройка Jinja2 шаблонов
templates = Jinja2Templates(directory="app/templates")
# Static files
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Подключение к Redis
r = redis.Redis(host='redis-creators-app', port=6379, db=0)

# Главная страница
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Увеличиваем глобальное количество посещений в Redis
    r.incr('global_visits')

    # Получаем глобальное количество посещений
    global_visits = r.get('global_visits').decode('utf-8')

    # Возвращаем шаблон с глобальными посещениями
    return templates.TemplateResponse("index.html", {"request": request, "global_visits": global_visits})

# Обработка формы для подачи заявки в команду
@app.post("/submit_application")
async def submit_application(
    telegram_link: str = Form(...),
    full_name: str = Form(...),
    desired_role: str = Form(...),
    skills: str = Form(...),
    phone: str = Form(...),
):
    # Логика обработки данных формы
    application_data = {
        "telegram_link": telegram_link,
        "full_name": full_name,
        "desired_role": desired_role,
        "skills": skills,
        "phone": phone,
    }

    r.set(telegram_link, f"{application_data}")

    # Здесь можно сохранить данные в базу данных или отправить уведомление
    data = {"phone_number": 79642245443, "message": f"{application_data}"}

    async with httpx.AsyncClient() as client:
        response = await client.post("http://51.250.37.160:8012/send_message", json=data)
        print(response.status_code)

    return JSONResponse(content={"message": "Заявка успешно отправлена"}, status_code=200)


