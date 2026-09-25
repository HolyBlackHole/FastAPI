# main.py
from fastapi import FastAPI, Query
from api import taobao_api
import json

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello from Vercel!"}


@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}


@app.get("/taobao_api/items")
def fetch_taobao_items(
    page_num: int = Query(default=1, ge=1, description="页码，从1开始"),
    page_size: int = Query(default=25, ge=1, le=25, description="每页数量，最大25")
):
    # 此时 page_num 和 page_size 已经是 int 类型，且经过校验
    data = taobao_api.get_data(page_num, page_size)
    return data