from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class OrderItemData(BaseModel):
    label_name: str
    quantity: int
    size: str
    size_unit: str
    po_number: str
    file_url: str

class ItemInsert(BaseModel):
    po_number: str
    quantity: int
    label_name: str
    size: str

class ItemResponse(BaseModel):
    status: str
    order_id: str

class LabelSearch(BaseModel):
    input: str
    company: str

class LabelResponse(BaseModel):
    labels: list[str]

class StatusUpdateRequest(BaseModel):
    order_id: str
    status: str