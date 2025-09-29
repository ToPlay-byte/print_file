import re

from pathlib import Path as SysPath

from uuid import uuid4

from typing import Optional, List

from datetime import datetime, timezone

import fitz
from redis import Redis

from fastapi import APIRouter, status, Form, HTTPException, Depends, UploadFile, File, Query, Path
from fastapi.responses import FileResponse

from .utils import save_job, load_job, list_jobs
from .dependincies import get_redis
from src.core.config import settings
from src.worker import process_job
from src.schemas import JobResponseSchema


router = APIRouter()


@router.post(
    "/jobs",
    summary="Create a new print job",
    response_model=JobResponseSchema,
    responses={
        400: {
            "description": "Missing file | File size exceeds 10MB | Invalid PDF",
            "content": {
                "application/json": {
                    "example": {"detail": "File size exceeds 10MB."}
                }
            },
        },
        415: {
            "description": "Invalid file type",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid file type, only PDF is allowed."}
                }
            },
        },
    },
)
async def create_job(
    title: Optional[str] = Form(
        default=None,
        description="Optional custom name for the job. If not provided, the file name will be used.",
    ),
    file: UploadFile = File(
        description="PDF file to be uploaded. Maximum size: 10MB.",
    ),
    redis_client: Redis = Depends(get_redis),
) -> JobResponseSchema:
    """Upload a PDF file and create a new print job."""

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Invalid file type, only PDF is allowed.",
        )

    content = await file.read()

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="File is missing.")

    max_file_size = 10 * 1024 * 1024

    if len(content) > max_file_size:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB.")

    try:
        doc = fitz.open(stream=content, filetype="pdf")
        pages = doc.page_count
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid PDF file.")

    job_id = str(uuid4())
    base_name = title if title else file.filename
    safe_name = re.sub(r"[^a-zA-Z0-9_.-]", "_", base_name.strip())
    stored_name = f"{safe_name}_{job_id}.pdf"
    file_path = settings.uploaded_files / stored_name

    with open(file_path, "wb") as f:
        f.write(content)

    created_at = datetime.now(timezone.utc)

    job = JobResponseSchema(
        job_id=job_id,
        filename=safe_name,
        pages=pages,
        status="queued",
        created_at=created_at,
    )

    save_job(redis_client, job)
    process_job.delay(job_id)

    return job


@router.get(
    "/jobs",
    summary="List all print jobs",
    response_model=List[JobResponseSchema],
)
def get_jobs(
    status_job: Optional[str] = Query(
        default=None,
        description="Filter jobs by status (queued, printing, done, canceled, error).",
    ),
    redis_client: Redis = Depends(get_redis),
) -> List[JobResponseSchema]:
    """Get all jobs from the queue."""
    jobs = list_jobs(redis_client)

    if status_job:
        jobs = [item for item in jobs if item.status == status_job]

    return jobs


@router.get(
    "/jobs/{job_id}",
    summary="Get job details",
    response_model=JobResponseSchema,
    responses={
        404: {
            "description": "Job not found",
            "content": {
                "application/json": {"example": {"detail": "Job not found."}}
            },
        },
    },
)
def get_job(
    job_id: str = Path(
        description="Unique job identifier (UUID).",
    ),
    redis_client: Redis = Depends(get_redis),
) -> JobResponseSchema:
    """Retrieve details of a single job by ID."""

    job = load_job(redis_client, job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    return job


@router.post(
    "/jobs/{job_id}/cancel",
    summary="Cancel a print job",
    response_model=JobResponseSchema,
    responses={
        404: {
            "description": "Job not found",
            "content": {
                "application/json": {"example": {"detail": "Job not found."}}
            },
        },
        409: {
            "description": "Job cannot be canceled",
            "content": {
                "application/json": {
                    "example": {"detail": "Cannot cancel job in status done."}
                }
            },
        },
    },
)
def cancel_job(
    job_id: str = Path(
        description="Unique job identifier (UUID).",
    ),
    redis_client: Redis = Depends(get_redis),
) -> JobResponseSchema:
    """Cancel a job by its ID. A job can be canceled only if status is `queued` or `printing`."""

    job = load_job(redis_client, job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    if job.status not in ("queued", "printing"):
        raise HTTPException(
            status_code=409,
            detail=f"Cannot cancel job in status {job.status}.",
        )

    job.status = "canceled"
    save_job(redis_client, job)

    return job


@router.get(
    "/jobs/{job_id}/file",
    summary="Download job file",
    responses={
        404: {
            "description": "Job or file not found",
            "content": {
                "application/json": {"example": {"detail": "File not found."}}
            },
        }
    }
)
def download_file(
    job_id: str = Path(
        description="Unique job identifier (UUID).",
    ),
    redis_client: Redis = Depends(get_redis),
) -> FileResponse:
    """Download the PDF file associated with a job."""

    job = load_job(redis_client, job_id)

    if not job or not SysPath((file_path := settings.uploaded_files / f"{job.filename}_{job_id}.pdf")).exists():
        raise HTTPException(status_code=404, detail="File not found.")

    return FileResponse(file_path, filename=job.filename, media_type="application/pdf")
