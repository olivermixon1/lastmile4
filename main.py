from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Last-Mile Logistics API",
    description="Backend API for connecting autonomous trucking companies with local truckers.",
    version="1.0.0"
)

# -------------------------------------------------
# Allow iOS app / frontend to call your API (🔥 NEW)
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# Data Models
# -------------------------------------------------
class Job(BaseModel):
    id: int
    pickup_location: str
    dropoff_location: str
    load_description: str
    status: str = "available"  # available, assigned, completed
    driver_id: Optional[int] = None

class JobCreate(BaseModel):   # 🔥 NEW: model for creating jobs
    pickup_location: str
    dropoff_location: str
    load_description: str

class Driver(BaseModel):
    id: int
    name: str
    current_location: str


# -------------------------------------------------
# In-Memory Database
# -------------------------------------------------
drivers = [
    Driver(id=1, name="John Doe", current_location="Seattle"),
    Driver(id=2, name="Sarah Lee", current_location="Bellevue"),
]

jobs = [
    Job(id=1, pickup_location="Amazon SODO", dropoff_location="Bellevue Downtown", load_description="Pallet of boxes", status="available"),
    Job(id=2, pickup_location="Port of Seattle Terminal 18", dropoff_location="Redmond Microsoft Campus", load_description="Electronics container", status="available"),
]

next_job_id = 3  # 🔥 tracks the next job ID


# -------------------------------------------------
# Routes
# -------------------------------------------------

@app.get("/")
def home():
    return {"message": "Last-Mile Logistics API is live!"}


# Get all jobs
@app.get("/jobs", response_model=List[Job])
def get_jobs():
    return jobs


# 🔥 NEW: Add a job (from app or web admin panel)
@app.post("/jobs", response_model=Job)
def create_job(job: JobCreate):
    global next_job_id

    new_job = Job(
        id=next_job_id,
        pickup_location=job.pickup_location,
        dropoff_location=job.dropoff_location,
        load_description=job.load_description,
        status="available",
        driver_id=None
    )

    jobs.append(new_job)
    next_job_id += 1

    return new_job


# 🔥 NEW: Driver accepts a job
@app.post("/jobs/{job_id}/accept", response_model=Job)
def accept_job(job_id: int, driver_id: Optional[int] = None):
    for job in jobs:
        if job.id == job_id:
            if job.status != "available":
                raise HTTPException(status_code=400, detail="Job already assigned or completed")
            
            job.status = "assigned"
            job.driver_id = driver_id
            return job

    raise HTTPException(status_code=404, detail="Job not found")


# Assign a driver to a job (older method, still usable)
@app.post("/assign/{job_id}/{driver_id}")
def assign_driver(job_id: int, driver_id: int):
    for job in jobs:
        if job.id == job_id:
            job.status = "assigned"
            job.driver_id = driver_id
            return {"message": "Driver assigned", "job": job}
    return {"error": "Job not found"}


# Complete a job
@app.post("/complete/{job_id}")
def complete_job(job_id: int):
    for job in jobs:
        if job.id == job_id:
            job.status = "completed"
            return {"message": "Job completed", "job": job}
    return {"error": "Job not found"}


# Get all drivers
@app.get("/drivers", response_model=List[Driver])
def get_drivers():
    return drivers
