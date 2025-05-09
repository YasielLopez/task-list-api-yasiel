from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey
from datetime import datetime
from typing import Optional
from ..db import db

class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    
    # Relationship with Goal
    goal_id: Mapped[Optional[int]] = mapped_column(ForeignKey("goal.id"), nullable=True)
    goal = relationship("Goal", back_populates="tasks")
    
    @classmethod
    def from_dict(cls, task_data):
        """
        Creates a new Task instance from a dictionary
        """
        if not task_data.get("title") or not task_data.get("description"):
            return None
            
        return cls(
            title=task_data.get("title"),
            description=task_data.get("description"),
            completed_at=task_data.get("completed_at")
        )
    
    def to_dict(self, include_goal_id=False):
        """
        Converts the Task model to a dictionary for API responses
        """
        task_dict = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "is_complete": self.completed_at is not None
        }
        
        if include_goal_id and self.goal_id is not None:
            task_dict["goal_id"] = self.goal_id
        
        return task_dict