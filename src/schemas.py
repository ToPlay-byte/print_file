from datetime import datetime

from pydantic import BaseModel, Field


class JobResponseSchema(BaseModel):
    """Schema representing a print job."""

    job_id: str = Field(description="Unique job identifier (UUID)")
    filename: str = Field(description="Original or sanitized name of the uploaded PDF file")
    pages: int = Field(description="Number of pages in the PDF document")
    status: str = Field(description="Current job status (queued, printing, canceled, done, error)")
    created_at: datetime = Field(description="Job creation timestamp in UTC")
