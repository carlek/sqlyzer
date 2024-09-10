from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from utils.metrics import unique_tables, subquery_tables, redundant_joins

app = FastAPI()
templates = Jinja2Templates(directory="src/templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze", response_class=HTMLResponse)
async def analyze(request: Request, query: str = Form(...)):
    metrics = {
        "subquery_tables": subquery_tables(query),
        "unique_tables": unique_tables(query),
        "redundant_joins": redundant_joins(query)
    }
    return templates.TemplateResponse("result.html", {"request": request, "metrics": metrics})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)