from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.settings.models import SystemSettings
from app.settings.schemas import SystemSettingsSchema

class SettingsService:
    @staticmethod
    async def get_settings(db: AsyncSession) -> SystemSettings:
        result = await db.execute(select(SystemSettings).where(SystemSettings.id == 1))
        settings = result.scalars().first()
        
        if not settings:
            settings = SystemSettings(id=1)
            db.add(settings)
            await db.commit()
            await db.refresh(settings)
            
        return settings

    @staticmethod
    async def update_settings(db: AsyncSession, payload: SystemSettingsSchema) -> SystemSettings:
        settings = await SettingsService.get_settings(db)
        
        settings.email_alerts = payload.email_alerts
        settings.push_notifications = payload.push_notifications
        settings.strict_mode = payload.strict_mode
        settings.auto_process_audio = payload.auto_process_audio
        settings.retention_days = payload.retention_days
        settings.timeout_minutes = payload.timeout_minutes
        
        await db.commit()
        await db.refresh(settings)
        return settings
