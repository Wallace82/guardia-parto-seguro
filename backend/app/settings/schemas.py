from pydantic import BaseModel

class SystemSettingsSchema(BaseModel):
    email_alerts: bool
    push_notifications: bool
    strict_mode: bool
    auto_process_audio: bool
    retention_days: int
    timeout_minutes: int

    class Config:
        from_attributes = True
