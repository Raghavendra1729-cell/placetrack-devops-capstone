from fastapi import Depends, FastAPI, HTTPException, Response
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from . import models, schemas
from .db import get_db

app = FastAPI(title="PlaceTrack API")
Instrumentator().instrument(app).expose(app, include_in_schema=False)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready(response: Response, db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        response.status_code = 503
        return {"status": "database unavailable"}
    return {"status": "ready"}


@app.get("/api/jobs", response_model=list[schemas.JobOut])
def list_jobs(status: schemas.Status | None = None, db: Session = Depends(get_db)):
    query = select(models.Job).order_by(models.Job.id.desc())
    if status:
        query = query.where(models.Job.status == status)
    return db.scalars(query).all()


@app.get("/api/jobs/stats", response_model=schemas.Stats)
def stats(db: Session = Depends(get_db)):
    rows = dict(db.execute(select(models.Job.status, func.count()).group_by(models.Job.status)).all())
    counts = {s: rows.get(s, 0) for s in schemas.STATUSES}
    return {"total": sum(counts.values()), **counts}


def get_or_404(db: Session, job_id: int) -> models.Job:
    job = db.get(models.Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/api/jobs/{job_id}", response_model=schemas.JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, job_id)


@app.post("/api/jobs", response_model=schemas.JobOut, status_code=201)
def create_job(payload: schemas.JobIn, db: Session = Depends(get_db)):
    job = models.Job(**payload.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@app.put("/api/jobs/{job_id}", response_model=schemas.JobOut)
def update_job(job_id: int, payload: schemas.JobIn, db: Session = Depends(get_db)):
    job = get_or_404(db, job_id)
    for field, value in payload.model_dump().items():
        setattr(job, field, value)
    db.commit()
    db.refresh(job)
    return job


@app.delete("/api/jobs/{job_id}", status_code=204)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, job_id))
    db.commit()
