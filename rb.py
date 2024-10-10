from fastapi import FastAPI, HTTPException, Path, Body
from pydantic import BaseModel
from typing import List, Optional

# Initialize FastAPI application
app = FastAPI()

# Initial Task Database
task_db = [
    {"task_id": 1, "task_title": "Laboratory Activity", "task_desc": "Create Lab Act 2", "is_finished": False}
]

# Pydantic Model for Task
class Task(BaseModel):
    task_id: Optional[int] = None
    task_title: str
    task_desc: str
    is_finished: bool = False

# Helper function to find a task by ID
def find_task(task_id: int):
    for task in task_db:
        if task["task_id"] == task_id:
            return task
    return None

# Endpoint to get a task by ID
@app.get("/tasks/{task_id}")
def get_task(task_id: int = Path(..., description="ID of the task to retrieve", gt=0)):
    task = find_task(task_id)
    if task:
        return {"status": "ok", "data": task}
    else:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

# Endpoint to create a new task
@app.post("/tasks")
def create_task(task: Task = Body(..., description="Details of the task to create")):
    if not task.task_title or not task.task_desc:
        raise HTTPException(status_code=400, detail="Task title and description cannot be empty")

    # Set the task_id for the new task
    task_id = max(task["task_id"] for task in task_db) + 1 if task_db else 1
    new_task = task.dict()
    new_task["task_id"] = task_id
    task_db.append(new_task)
    return {"status": "ok", "data": new_task}

# Endpoint to update a task by ID
@app.patch("/tasks/{task_id}")
def update_task(
    task_id: int = Path(..., description="ID of the task to update", gt=0),
    task_update: Task = Body(..., description="Task data to update (only fields to modify)")
):
    task = find_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

    # Update only provided fields
    update_data = task_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if key == "task_id":
            continue
        task[key] = value

    return {"status": "ok", "data": task}

# Endpoint to delete a task by ID
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int = Path(..., description="ID of the task to delete", gt=0)):
    global task_db
    task = find_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

    # Remove task from the database
    task_db = [t for t in task_db if t["task_id"] != task_id]
    return {"status": "ok", "message": f"Task with id {task_id} deleted successfully"}
