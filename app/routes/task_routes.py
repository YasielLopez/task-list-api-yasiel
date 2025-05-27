from flask import Blueprint, request, make_response, abort
from ..db import db
from ..models.task import Task
from datetime import datetime
from ..services.slack_service import send_slack_notification

bp = Blueprint("tasks", __name__, url_prefix="/tasks")

def get_task_by_id(id):
    query = db.select(Task).where(Task.id == id)
    return db.session.scalar(query)

@bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()
    
    new_task = Task.from_dict(request_body)
    
    if not new_task:
        abort(400)
    
    db.session.add(new_task)
    db.session.commit()
    
    return {"task": new_task.to_dict()}, 201

@bp.route("", methods=["GET"])
def get_all_tasks():
    sort_param = request.args.get("sort")
    
    query = db.select(Task)
    
    if sort_param == "asc":
        query = query.order_by(Task.title.asc())
    elif sort_param == "desc":
        query = query.order_by(Task.title.desc())
    
    tasks = db.session.scalars(query).all()
    
    return [task.to_dict() for task in tasks]

@bp.route("/<task_id>", methods=["GET"])
def get_task(task_id):
    task = get_task_by_id(task_id)
    
    if not task:
        abort(404)
    
    return {"task": task.to_dict(include_goal_id=True)}

@bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):
    task = get_task_by_id(task_id)
    
    if not task:
        abort(404)
    
    request_body = request.get_json()
    
    task.title = request_body.get("title", task.title)
    task.description = request_body.get("description", task.description)
    
    db.session.commit()
    
    response = make_response("", 204)
    response.mimetype = "application/json"
    return response

@bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = get_task_by_id(task_id)
    
    if not task:
        abort(404)
    
    db.session.delete(task)
    db.session.commit()
    
    response = make_response("", 204)
    response.mimetype = "application/json"
    return response

@bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_task_complete(task_id):
    task = get_task_by_id(task_id)
    
    if not task:
        abort(404)
    
    task.completed_at = datetime.now()
    db.session.commit()
    
    send_slack_notification(f"Someone just completed the task {task.title}")
    
    response = make_response("", 204)
    response.mimetype = "application/json"
    return response

@bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_task_incomplete(task_id):
    task = get_task_by_id(task_id)
    
    if not task:
        abort(404)
    
    task.completed_at = None
    db.session.commit()
    
    response = make_response("", 204)
    response.mimetype = "application/json"
    return response