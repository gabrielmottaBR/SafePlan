"""
SafePlan Backend - Repository Base Classes
Generic repository pattern for CRUD operations
"""

from typing import Generic, TypeVar, List, Optional, Type
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.src.data.models import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """
    Generic base repository for CRUD operations.
    
    Implements common patterns for all entity repositories.
    """
    
    def __init__(self, db: Session, model: Type[T]):
        """
        Initialize repository.
        
        Args:
            db: SQLAlchemy session
            model: SQLAlchemy model class
        """
        self.db = db
        self.model = model
    
    def create(self, obj_in: dict) -> T:
        """
        Create a new record.
        
        Args:
            obj_in: Dictionary with data
            
        Returns:
            Created model instance
        """
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def get_by_id(self, id: int) -> Optional[T]:
        """
        Get record by ID.
        
        Args:
            id: Primary key
            
        Returns:
            Model instance or None
        """
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """
        Get all records with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of model instances
        """
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def update(self, id: int, obj_in: dict) -> Optional[T]:
        """
        Update a record.
        
        Args:
            id: Primary key
            obj_in: Dictionary with updated data
            
        Returns:
            Updated model instance or None
        """
        db_obj = self.get_by_id(id)
        if db_obj:
            for key, value in obj_in.items():
                setattr(db_obj, key, value)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: int) -> bool:
        """
        Delete a record.
        
        Args:
            id: Primary key
            
        Returns:
            True if deleted, False if not found
        """
        db_obj = self.get_by_id(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False
    
    def count(self) -> int:
        """
        Count total records.
        
        Returns:
            Total number of records
        """
        return self.db.query(self.model).count()
