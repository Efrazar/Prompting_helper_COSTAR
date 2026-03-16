# src/models/prompt.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class PromptTemplate(Base):
    """
    Single table to store all prompts and templates.
    This is your starting point - simple and functional.
    """
    __tablename__ = "prompts"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # COSTAR fields - using Text for unlimited length
    role = Column(Text, nullable=True)
    context = Column(Text, nullable=True)
    objective = Column(Text, nullable=True)
    style = Column(Text, nullable=True)
    tone = Column(Text, nullable=True)
    audience = Column(Text, nullable=True)
    response_format = Column(Text, nullable=True)
    start_analysis = Column(Text, nullable=True)
    
    # Metadata fields
    title = Column(String(200), nullable=True)  # Optional name for the prompt
    is_template = Column(Boolean, default=False)  # True if pre-filled template
    is_favorite = Column(Boolean, default=False)  # Star/favorite status
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    usage_count = Column(Integer, default=0)  # How many times copied
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    last_used_at = Column(DateTime, nullable=True)
    
    def to_dict(self):
        """Convert database object to dictionary for easy JSON serialization"""
        return {
            "id": self.id,
            "title": self.title,
            "role": self.role,
            "context": self.context,
            "objective": self.objective,
            "style": self.style,
            "tone": self.tone,
            "audience": self.audience,
            "response_format": self.response_format,
            "start_analysis": self.start_analysis,
            "is_template": self.is_template,
            "is_favorite": self.is_favorite,
            "tags": self.tags.split(",") if self.tags else [],
            "usage_count": self.usage_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None
        }
    
    def __repr__(self):
        """String representation for debugging"""
        return f"<PromptTemplate(id={self.id}, title='{self.title}', created={self.created_at})>"

