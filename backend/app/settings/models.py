from sqlalchemy import Column, Integer, Boolean
from app.database import Base

class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True, default=1)
    email_alerts = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=False)
    strict_mode = Column(Boolean, default=True)
    auto_process_audio = Column(Boolean, default=True)
    retention_days = Column(Integer, default=180)
    timeout_minutes = Column(Integer, default=30)
