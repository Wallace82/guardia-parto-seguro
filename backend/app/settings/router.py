from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_user
from app.auth.models import User
from app.settings.schemas import SystemSettingsSchema
from app.settings.service import SettingsService
from app.audit.service import AuditService

router = APIRouter()

@router.get("", response_model=SystemSettingsSchema)
async def get_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve global system settings"""
    settings = await SettingsService.get_settings(db)
    return settings

@router.put("", response_model=SystemSettingsSchema)
async def update_settings(
    payload: SystemSettingsSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update global system settings (requires admin)"""
    # For now checking simple role, or rely on auth dependency (can add role check if needed)
    if current_user.role != "admin" and current_user.role != "gestor":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Not enough permissions")

    settings = await SettingsService.update_settings(db, payload)
    
    await AuditService.log_action(
        db, action="UPDATE_CONFIG", resource="system_settings", user_id=current_user.id
    )
    
    return settings
