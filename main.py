from typing import List

from fastapi import FastAPI,HTTPException
from fastapi.params import Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db_connect import SessionLocal, engine
from models import Base, Task

app = FastAPI()

class TaskSchema(BaseModel):
    title : str
    description : str
    status : str


Base.metadata.create_all(bind=engine)

def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Welcome to Task Manager API"}

@app.post("/tasks")
def add_task(task :  TaskSchema, db : Session = Depends(get_db)):

    new_task = Task(title = task.title , description = task.description)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@app.get("/tasks",response_model=List[TaskSchema])
def get_tasks(db : Session = Depends(get_db)):
    tasks = db.query(Task).all()
    if not tasks:
        raise HTTPException(status_code = 404 , detail="There are not tasks in the list")
    return tasks

@app.get("/tasks/{task_id}",response_model = TaskSchema)
def get_specific_task(task_id : int, db : Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        return task
    else:
        raise HTTPException(status_code=404,detail=f"Item {task_id} not found!" )

@app.put("/tasks/{task_id}", response_model=TaskSchema)
def update_task(task_id : int , updated_task : TaskSchema, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.title = updated_task.title
        task.description = updated_task.description
        task.status = updated_task.status
        db.commit()
        return task

    else:
        raise HTTPException(status_code=404, detail=f"Item {task_id} not found!")

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
        return {"message": f"Task {task_id} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found!")



