"""Service for managing email conversation threads."""

import json
from typing import List, Optional
from sqlalchemy.orm import Session
from ..db_models import EmailThread, EmailMessage


class ThreadService:
    """Service for CRUD operations with email threads."""
    
    @staticmethod
    def create_thread(
        db: Session,
        subject: str,
        company_context_id: Optional[int] = None,
        extra_directives: Optional[List[str]] = None,
        custom_prompt: Optional[str] = None
    ) -> EmailThread:
        """Create new email thread."""
        extra_directives_json = json.dumps(extra_directives) if extra_directives else None
        thread = EmailThread(
            subject=subject,
            company_context_id=company_context_id,
            extra_directives=extra_directives_json,
            custom_prompt=custom_prompt
        )
        db.add(thread)
        db.commit()
        db.refresh(thread)
        return thread
    
    @staticmethod
    def update_thread_directives(
        db: Session,
        thread_id: int,
        extra_directives: Optional[List[str]] = None,
        custom_prompt: Optional[str] = None
    ) -> Optional[EmailThread]:
        """Update thread directives."""
        print(f"[DEBUG] update_thread_directives called with thread_id={thread_id}, extra_directives={extra_directives}, custom_prompt={custom_prompt}")
        thread = db.query(EmailThread).filter(EmailThread.id == thread_id).first()
        if not thread:
            print(f"[ERROR] Thread {thread_id} not found")
            return None
        
        print(f"[DEBUG] Thread found: id={thread.id}, current extra_directives={thread.extra_directives}, custom_prompt={thread.custom_prompt}")
        
        if extra_directives is not None:
            if extra_directives:
                thread.extra_directives = json.dumps(extra_directives)
                print(f"[DEBUG] Set extra_directives to JSON: {thread.extra_directives}")
            else:
                thread.extra_directives = None
                print(f"[DEBUG] Set extra_directives to None (empty list)")
        
        if custom_prompt is not None:
            thread.custom_prompt = custom_prompt.strip() if custom_prompt and custom_prompt.strip() else None
            print(f"[DEBUG] Set custom_prompt to: {thread.custom_prompt}")
        
        try:
            print(f"[DEBUG] Committing changes to database...")
            db.commit()
            db.refresh(thread)
            print(f"[DEBUG] After commit - extra_directives={thread.extra_directives}, custom_prompt={thread.custom_prompt}")
            
            # Verify data was saved by querying again
            db.expire_all()
            verified_thread = db.query(EmailThread).filter(EmailThread.id == thread_id).first()
            if verified_thread:
                verified_extra_directives, verified_custom_prompt = ThreadService.get_thread_directives(verified_thread)
                print(f"[DEBUG] Verified from DB - extra_directives={verified_extra_directives}, custom_prompt={verified_custom_prompt}")
        except Exception as e:
            db.rollback()
            print(f"[ERROR] Error updating thread directives: {e}")
            import traceback
            traceback.print_exc()
            raise e
        
        return thread
    
    @staticmethod
    def get_thread_directives(thread: EmailThread) -> tuple[Optional[List[str]], Optional[str]]:
        """Get thread directives."""
        extra_directives = None
        if thread.extra_directives:
            try:
                extra_directives = json.loads(thread.extra_directives)
            except:
                extra_directives = None
        
        return extra_directives, thread.custom_prompt
    
    @staticmethod
    def get_thread(db: Session, thread_id: int) -> Optional[EmailThread]:
        """Get thread by ID with messages."""
        return db.query(EmailThread).filter(EmailThread.id == thread_id).first()
    
    @staticmethod
    def add_message(
        db: Session,
        thread_id: int,
        message_type: str,
        subject: str,
        body: str,
        sender_name: Optional[str] = None,
        sender_position: Optional[str] = None,
        generation_time_seconds: Optional[float] = None
    ) -> EmailMessage:
        """Add message to thread."""
        message = EmailMessage(
            thread_id=thread_id,
            message_type=message_type,
            subject=subject,
            body=body,
            sender_name=sender_name,
            sender_position=sender_position,
            generation_time_seconds=generation_time_seconds
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
    
    @staticmethod
    def get_thread_history(db: Session, thread_id: int) -> List[EmailMessage]:
        """Get all messages in thread ordered by creation time."""
        return db.query(EmailMessage).filter(
            EmailMessage.thread_id == thread_id
        ).order_by(EmailMessage.created_at.asc()).all()
    
    @staticmethod
    def format_thread_history(messages: List[EmailMessage]) -> str:
        """Format thread history as text for context."""
        if not messages:
            return ""
        
        history_lines = ["История переписки:"]
        for msg in messages:
            msg_type = "Входящее письмо" if msg.message_type == "incoming" else "Исходящее письмо"
            sender_info = ""
            if msg.sender_name:
                sender_info = f" от {msg.sender_name}"
                if msg.sender_position:
                    sender_info += f" ({msg.sender_position})"
            
            history_lines.append(f"\n{msg_type}{sender_info}:")
            history_lines.append(f"Тема: {msg.subject}")
            history_lines.append(f"Текст: {msg.body}")
            history_lines.append("---")
        
        return "\n".join(history_lines)

