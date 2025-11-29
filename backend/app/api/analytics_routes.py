"""API routes for analytics and dashboard data."""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, case
from sqlalchemy.sql import text

from ..database import get_db
from ..db_models import EmailThread, EmailMessage, CompanyContext

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/overview")
def get_overview(
    days: int = Query(7, description="Количество дней для анализа"),
    db: Session = Depends(get_db)
) -> Dict:
    """Get overview statistics."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Total threads
    total_threads = db.query(EmailThread).filter(
        EmailThread.created_at >= start_date
    ).count()
    
    # Total messages
    total_messages = db.query(EmailMessage).filter(
        EmailMessage.created_at >= start_date
    ).count()
    
    # Incoming vs Outgoing
    incoming_count = db.query(EmailMessage).filter(
        EmailMessage.created_at >= start_date,
        EmailMessage.message_type == "incoming"
    ).count()
    
    outgoing_count = db.query(EmailMessage).filter(
        EmailMessage.created_at >= start_date,
        EmailMessage.message_type == "outgoing"
    ).count()
    
    # Threads with directives
    threads_with_directives = db.query(EmailThread).filter(
        EmailThread.created_at >= start_date,
        EmailThread.extra_directives.isnot(None)
    ).count()
    
    # Average response time in seconds
    # Calculate average generation time from outgoing messages
    avg_response_time_seconds = 0.0
    try:
        # Get all outgoing messages with generation time in the period
        outgoing_messages = db.query(EmailMessage.generation_time_seconds).filter(
            EmailMessage.created_at >= start_date,
            EmailMessage.message_type == "outgoing",
            EmailMessage.generation_time_seconds.isnot(None)
        ).all()
        
        generation_times = [msg[0] for msg in outgoing_messages if msg[0] is not None and msg[0] > 0]
        
        if generation_times:
            avg_response_time_seconds = round(sum(generation_times) / len(generation_times), 2)
            print(f"[DEBUG] Calculated avg generation time: {avg_response_time_seconds}s from {len(generation_times)} messages")
        else:
            print(f"[DEBUG] No generation times found in period")
    except Exception as e:
        print(f"Error calculating avg response time: {e}")
        import traceback
        traceback.print_exc()
    
    return {
        "period_days": days,
        "total_threads": total_threads,
        "total_messages": total_messages,
        "incoming_messages": incoming_count,
        "outgoing_messages": outgoing_count,
        "threads_with_directives": threads_with_directives,
        "avg_response_time_seconds": avg_response_time_seconds,
    }


@router.get("/messages-by-day")
def get_messages_by_day(
    days: int = Query(7, description="Количество дней для анализа"),
    db: Session = Depends(get_db)
) -> Dict:
    """Get message count grouped by day."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Group by date
    results = db.query(
        func.date(EmailMessage.created_at).label('date'),
        func.count(EmailMessage.id).label('count'),
        EmailMessage.message_type
    ).filter(
        EmailMessage.created_at >= start_date
    ).group_by(
        func.date(EmailMessage.created_at),
        EmailMessage.message_type
    ).order_by(func.date(EmailMessage.created_at)).all()
    
    # Organize by date
    by_date = {}
    for date, count, msg_type in results:
        date_str = date.isoformat() if isinstance(date, datetime) else str(date)
        if date_str not in by_date:
            by_date[date_str] = {"date": date_str, "incoming": 0, "outgoing": 0}
        by_date[date_str][msg_type] = count
    
    return {
        "data": list(by_date.values()),
        "period_days": days
    }


@router.get("/threads-by-context")
def get_threads_by_context(
    days: int = Query(30, description="Количество дней для анализа"),
    db: Session = Depends(get_db)
) -> Dict:
    """Get thread count grouped by company context."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Get threads with context
    results = db.query(
        CompanyContext.name.label('context_name'),
        func.count(EmailThread.id).label('thread_count')
    ).join(
        EmailThread, EmailThread.company_context_id == CompanyContext.id
    ).filter(
        EmailThread.created_at >= start_date
    ).group_by(
        CompanyContext.name
    ).all()
    
    # Count threads without context
    threads_without_context = db.query(EmailThread).filter(
        EmailThread.created_at >= start_date,
        EmailThread.company_context_id.is_(None)
    ).count()
    
    data = [
        {"name": name, "count": count}
        for name, count in results
    ]
    
    if threads_without_context > 0:
        data.append({"name": "Без контекста", "count": threads_without_context})
    
    return {
        "data": data,
        "period_days": days
    }


@router.get("/threads-growth")
def get_threads_growth(
    days: int = Query(30, description="Количество дней для анализа"),
    db: Session = Depends(get_db)
) -> Dict:
    """Get cumulative thread growth over time."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Get daily thread counts
    daily_counts = db.query(
        func.date(EmailThread.created_at).label('date'),
        func.count(EmailThread.id).label('count')
    ).filter(
        EmailThread.created_at >= start_date
    ).group_by(
        func.date(EmailThread.created_at)
    ).order_by(func.date(EmailThread.created_at)).all()
    
    # Calculate cumulative
    cumulative = 0
    data = []
    for date, count in daily_counts:
        cumulative += count
        date_str = date.isoformat() if isinstance(date, datetime) else str(date)
        data.append({
            "date": date_str,
            "daily": count,
            "cumulative": cumulative
        })
    
    return {
        "data": data,
        "period_days": days
    }


@router.get("/top-threads")
def get_top_threads(
    limit: int = Query(10, description="Количество топ переписок"),
    days: int = Query(30, description="Количество дней для анализа"),
    db: Session = Depends(get_db)
) -> Dict:
    """Get top threads by message count."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    results = db.query(
        EmailThread.id,
        EmailThread.subject,
        func.count(EmailMessage.id).label('message_count'),
        EmailThread.created_at,
        EmailThread.updated_at
    ).join(
        EmailMessage, EmailMessage.thread_id == EmailThread.id
    ).filter(
        EmailThread.created_at >= start_date
    ).group_by(
        EmailThread.id,
        EmailThread.subject,
        EmailThread.created_at,
        EmailThread.updated_at
    ).order_by(
        func.count(EmailMessage.id).desc()
    ).limit(limit).all()
    
    data = []
    for thread_id, subject, msg_count, created_at, updated_at in results:
        data.append({
            "id": thread_id,
            "subject": subject,
            "message_count": msg_count,
            "created_at": created_at.isoformat() if created_at else None,
            "updated_at": updated_at.isoformat() if updated_at else None,
        })
    
    return {
        "data": data,
        "limit": limit,
        "period_days": days
    }


@router.get("/directives-usage")
def get_directives_usage(
    days: int = Query(30, description="Количество дней для анализа"),
    db: Session = Depends(get_db)
) -> Dict:
    """Get statistics about directives usage."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    total_threads = db.query(EmailThread).filter(
        EmailThread.created_at >= start_date
    ).count()
    
    threads_with_directives = db.query(EmailThread).filter(
        EmailThread.created_at >= start_date,
        EmailThread.extra_directives.isnot(None)
    ).count()
    
    threads_with_custom_prompt = db.query(EmailThread).filter(
        EmailThread.created_at >= start_date,
        EmailThread.custom_prompt.isnot(None)
    ).count()
    
    usage_percentage = round((threads_with_directives / total_threads * 100) if total_threads > 0 else 0, 2)
    
    return {
        "total_threads": total_threads,
        "threads_with_directives": threads_with_directives,
        "threads_with_custom_prompt": threads_with_custom_prompt,
        "directives_usage_percentage": usage_percentage,
        "period_days": days
    }

