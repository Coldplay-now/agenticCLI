"""
API 路由定义
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter()


# 数据模型示例
class Item(BaseModel):
    """项目模型"""
    id: int = None
    name: str
    description: str = None


class ItemCreate(BaseModel):
    """创建项目模型"""
    name: str
    description: str = None


# 模拟数据库
items_db = []


@router.get("/items", response_model=List[Item])
async def get_items():
    """获取所有项目"""
    return items_db


@router.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    """获取单个项目"""
    for item in items_db:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")


@router.post("/items", response_model=Item, status_code=201)
async def create_item(item: ItemCreate):
    """创建项目"""
    item_id = len(items_db) + 1
    new_item = {
        "id": item_id,
        "name": item.name,
        "description": item.description
    }
    items_db.append(new_item)
    return new_item


@router.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemCreate):
    """更新项目"""
    for idx, existing_item in enumerate(items_db):
        if existing_item["id"] == item_id:
            updated_item = {
                "id": item_id,
                "name": item.name,
                "description": item.description
            }
            items_db[idx] = updated_item
            return updated_item
    raise HTTPException(status_code=404, detail="Item not found")


@router.delete("/items/{item_id}")
async def delete_item(item_id: int):
    """删除项目"""
    for idx, item in enumerate(items_db):
        if item["id"] == item_id:
            items_db.pop(idx)
            return {"message": "Item deleted"}
    raise HTTPException(status_code=404, detail="Item not found")

