from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from ..db import db

class Goal(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100))
    
    tasks = relationship("Task", back_populates="goal", cascade="all, delete-orphan")
    
    @classmethod
    def from_dict(cls, goal_data):
        if not goal_data.get("title"):
            return None
            
        return cls(
            title=goal_data.get("title")
        )
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title
        }
        
    def to_dict_with_tasks(self):
        goal_dict = self.to_dict()
        goal_dict["tasks"] = [task.to_dict(include_goal_id=True) for task in self.tasks]
        return goal_dict
    
    #finished, i think