from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db_connect import SessionLocal, engine
from models import Base, Task

app = FastAPI()

# ✅ Ensure DB tables are created on startup
Base.metadata.create_all(bind=engine)


# ✅ Pydantic Schemas
class TaskCreateSchema(BaseModel):
    title: str
    description: str
    status: Optional[str] = None  # Optional, uses default in DB


class TaskUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class TaskResponseSchema(BaseModel):
    id: int
    title: str
    description: str
    status: str

    model_config = {
        "from_attributes": True }



# ✅ Dependency for Database Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ Root Endpoint
@app.get("/")
def root():
    return {"message": "Welcome to Task Manager API"}


# ✅ Create a Task
@app.post("/tasks", response_model=TaskResponseSchema)
def add_task(task: TaskCreateSchema, db: Session = Depends(get_db)):
    new_task = Task(
        title=task.title,
        description=task.description,
        status=task.status if task.status is not None else "pending"  # ✅ Always set status
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task  # ✅ No need to manually format `created_at` due to `json_encoders`


# ✅ Get All Tasks
@app.get("/tasks", response_model=List[TaskResponseSchema])
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    if not tasks:
        raise HTTPException(status_code=404, detail="There are no tasks in the list")

    return tasks  # ✅ FastAPI will auto-convert using `model_validate`


# ✅ Get a Specific Task
@app.get("/tasks/{task_id}", response_model=TaskResponseSchema)
def get_specific_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found!")

    return task  # ✅ Will automatically format `created_at`


# ✅ Update a Task
@app.put("/tasks/{task_id}", response_model=TaskResponseSchema)
def update_task(task_id: int, updated_task: TaskUpdateSchema, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found!")

    # ✅ Update fields only if provided
    update_data = updated_task.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return task


# ✅ Delete a Task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found!")

    db.delete(task)
    db.commit()
    return {"message": f"Task {task_id} deleted successfully"}
