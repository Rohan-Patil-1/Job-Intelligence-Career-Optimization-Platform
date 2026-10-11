from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import  JSON, UniqueConstraint, func
from sqlalchemy import Column, ForeignKey
    
class Base(DeclarativeBase):
    pass


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    source: Mapped[str] = mapped_column(String(100), nullable=False)
    source_job_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)

    location: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    remote_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    employment_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    salary_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    salary_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    salary_currency: Mapped[Optional[str]] = mapped_column(
        String(10), nullable=True
    )

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    responsibilities: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    skills: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    job_url: Mapped[str] = mapped_column(String(1000), nullable=False)

    posted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    collected_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

class JobEnrichment(Base):
    __tablename__ = "job_enrichments"

    id = Column(Integer, primary_key=True, index=True)

    job_id = Column(
        Integer,
        ForeignKey("jobs.id"),
        nullable=False,
        index=True,
    )

    source_url = Column(
        Text,
        nullable=False,
    )

    source_type = Column(
        String(30),
        nullable=False,
    )

    validation_status = Column(
        String(30),
        nullable=False,
    )

    external_identifier = Column(
        String(255),
        nullable=True,
    )

    title = Column(
        Text,
        nullable=True,
    )

    company = Column(
        Text,
        nullable=True,
    )

    description = Column(
        Text,
        nullable=True,
    )

    requirements = Column(
        JSON,
        nullable=False,
        default=list,
    )

    responsibilities = Column(
        JSON,
        nullable=False,
        default=list,
    )

    skills = Column(
        JSON,
        nullable=False,
        default=list,
    )

    extraction_method = Column(
        String(50),
        nullable=False,
        default="json_ld",
    )

    extracted_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint(
            "job_id",
            "source_url",
            name="uq_job_enrichment_source",
        ),
    )