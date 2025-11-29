"""Service for managing company context in database."""

from typing import List, Optional
from sqlalchemy.orm import Session
from ..db_models import CompanyContext


class ContextService:
    """Service for CRUD operations with company context."""
    
    @staticmethod
    def get_context(db: Session, context_id: int) -> Optional[CompanyContext]:
        """Get context by ID."""
        return db.query(CompanyContext).filter(CompanyContext.id == context_id).first()
    
    @staticmethod
    def get_all_contexts(db: Session, skip: int = 0, limit: int = 100) -> List[CompanyContext]:
        """Get all contexts with pagination."""
        return db.query(CompanyContext).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_context(
        db: Session,
        name: str,
        context_text: str,
        description: Optional[str] = None
    ) -> CompanyContext:
        """Create new context."""
        context = CompanyContext(
            name=name,
            context_text=context_text,
            description=description
        )
        db.add(context)
        db.commit()
        db.refresh(context)
        return context
    
    @staticmethod
    def update_context(
        db: Session,
        context_id: int,
        name: Optional[str] = None,
        context_text: Optional[str] = None,
        description: Optional[str] = None
    ) -> Optional[CompanyContext]:
        """Update existing context."""
        context = db.query(CompanyContext).filter(CompanyContext.id == context_id).first()
        if not context:
            return None
        
        if name is not None:
            context.name = name
        if context_text is not None:
            context.context_text = context_text
        if description is not None:
            context.description = description
        
        db.commit()
        db.refresh(context)
        return context
    
    @staticmethod
    def delete_context(db: Session, context_id: int) -> bool:
        """Delete context by ID."""
        context = db.query(CompanyContext).filter(CompanyContext.id == context_id).first()
        if not context:
            return False
        
        db.delete(context)
        db.commit()
        return True
    
    @staticmethod
    def get_context_text(db: Session, context_id: int) -> Optional[str]:
        """Get context text by ID. Returns None if not found."""
        context = ContextService.get_context(db, context_id)
        return context.context_text if context else None

