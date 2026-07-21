from sqlalchemy import Column, String, Integer, DateTime, Boolean
from app.database import Base
from datetime import datetime, timezone

class Report(Base):
    __tablename__ = "reports"

    report_id = Column(String(36), primary_key=True, index=True)
    session_id = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    report_type = Column(String(50), nullable=False, default="session")
    report_format = Column(String(20), nullable=False, default="pdf")
    download_url = Column(String(1000), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    file_hash_sha256 = Column(String(64), nullable=True)
    status = Column(String(20), nullable=False, default="generating")
    generated_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
