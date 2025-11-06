"""
数据模型定义
"""

from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from .db.database import Base


class Item(Base):
    """项目模型示例"""
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Item(id={self.id}, name={self.name})>"


# 更多模型定义...

