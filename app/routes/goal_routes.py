from flask import Blueprint, request, make_response, abort
from ..db import db
from ..models.goal import Goal
from ..models.task import Task

bp = Blueprint("goals", __name__, url_prefix="/goals")

def get_goal_by_id(id):
    query = db.select(Goal).where(Goal.id == id)
    return db.session.scalar(query)

def get_task_by_id(id):
    query = db.select(Task).where(Task.id == id)
    return db.session.scalar(query)

@bp.route("", methods=["POST"])
def create_goal():
    request_body = request.get_json()
    
    new_goal = Goal.from_dict(request_body)
    
    if not new_goal:
        abort(400)
    
    db.session.add(new_goal)
    db.session.commit()
    
    return {"goal": new_goal.to_dict()}, 201

@bp.route("", methods=["GET"])
def get_all_goals():
    goals = db.session.scalars(db.select(Goal)).all()
    return [goal.to_dict() for goal in goals]

@bp.route("/<goal_id>", methods=["GET"])
def get_goal(goal_id):
    goal = get_goal_by_id(goal_id)
    
    if not goal:
        abort(404)
    
    return {"goal": goal.to_dict()}

@bp.route("/<goal_id>", methods=["PUT"])
def update_goal(goal_id):
    goal = get_goal_by_id(goal_id)
    
    if not goal:
        abort(404)
    
    request_body = request.get_json()
    
    goal.title = request_body.get("title", goal.title)
    
    db.session.commit()
    
    response = make_response("", 204)
    response.mimetype = "application/json"
    return response

@bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    goal = get_goal_by_id(goal_id)
    
    if not goal:
        abort(404)
    
    db.session.delete(goal)
    db.session.commit()
    
    response = make_response("", 204)
    response.mimetype = "application/json"
    return response

@bp.route("/<goal_id>/tasks", methods=["GET"])
def get_goal_tasks(goal_id):
    goal = get_goal_by_id(goal_id)
    
    if not goal:
        abort(404)
    
    return goal.to_dict_with_tasks()

@bp.route("/<goal_id>/tasks", methods=["POST"])
def associate_tasks_with_goal(goal_id):
    goal = get_goal_by_id(goal_id)
    
    if not goal:
        abort(404)
    
    request_body = request.get_json()
    task_ids = request_body.get("task_ids", [])
    
    valid_tasks = [task for task in 
                (get_task_by_id(task_id) for task_id in task_ids) 
                if task is not None]
    
    goal.tasks = valid_tasks
    
    db.session.commit()
    
    return {
        "id": goal.id,
        "task_ids": [task.id for task in goal.tasks]
    }