from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from routes.r import router as all_routes
from db import lifespan

# 設定 HTML 模板資料夾
templates = Jinja2Templates(directory="templates")

# 建立 FastAPI
app = FastAPI(lifespan=lifespan)

# 載入路由
app.include_router(all_routes)

# 首頁
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request}
    )