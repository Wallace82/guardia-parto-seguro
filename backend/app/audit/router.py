from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.dependencies import get_current_user
from app.auth.models import User
from app.audit.models import AuditLog

router = APIRouter()

from sqlalchemy import func

@router.get("/logs")
async def get_audit_logs(
    skip: int = 0,
    limit: int = 50,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve audit logs with pagination and search"""
    if current_user.role != "admin" and current_user.role != "gestor":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Base query
    base_query = select(AuditLog, User).outerjoin(User, AuditLog.user_id == User.id)

    if search:
        search_term = f"%{search}%"
        base_query = base_query.where(
            (AuditLog.action.ilike(search_term)) |
            (AuditLog.resource.ilike(search_term)) |
            (User.full_name.ilike(search_term))
        )

    # Count total
    count_stmt = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    # Perform a join to get user information
    stmt = (
        base_query
        .order_by(AuditLog.timestamp.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    
    logs = []
    for row in result.all():
        audit_log, user = row
        logs.append({
            "id": str(audit_log.id),
            "action": audit_log.action,
            "resource": audit_log.resource,
            "user": user.full_name if user else "Sistema",
            "role": user.role if user else "system",
            "created_at": audit_log.timestamp.strftime("%d/%m/%Y %H:%M:%S")
        })
    
    return {"total": total, "items": logs}
