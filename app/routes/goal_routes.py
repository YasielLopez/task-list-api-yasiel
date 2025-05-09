from flask import Blueprint, request, jsonify, make_response
from ..db import db
from ..models.goal import Goal
from ..models.task import Task

goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

def get_goal_by_id(id):
    """Helper function to get a goal by ID"""
    query = db.select(Goal).where(Goal.id == id)
    return db.session.scalar(query)

@goals_bp.route("", methods=["POST"])
def create_goal():
    request_body = request.get_json()
    
    if not request_body.get("title"):
        return make_response(jsonify({"details": "Invalid data"}), 400)
    
    new_goal = Goal(title=request_body.get("title"))
    
    db.session.add(new_goal)
    db.session.commit()
    
    return make_response(jsonify({"goal": new_goal.to_dict()}), 201)

@goals_bp.route("", methods=["GET"])
def get_all_goals():
    goals = db.session.scalars(db.select(Goal)).all()
    return jsonify([goal.to_dict() for goal in goals])

@goals_bp.route("/<goal_id>", methods=["GET"])
def get_goal(goal_id):
    goal = get_goal_by_id(goal_id)
    
    if not goal:
        return make_response(jsonify({"error": "Goal not found"}), 404)
    
    return jsonify({"goal": goal.to_dict()})

@goals_bp.route("/<goal_id>", methods=["PUT"])
def update_goal(goal_id):
    goal = get_goal_by_id(goal_id)
    
    if not goal:
        return make_response(jsonify({"error": "Goal not found"}), 404)
    
    request_body = request.get_json()
    
    goal.title = request_body.get("title", goal.title)
    
    db.session.commit()
    
    return make_response("", 204, {"Content-Type": "application/json"})

@goals_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    goal = get_goal_by_id(goal_id)
    
    if not goal:
        return make_response(jsonify({"error": "Goal not found"}), 404)
    
    db.session.delete(goal)
    db.session.commit()
    
    return make_response("", 204, {"Content-Type": "application/json"})


@goals_bp.route("/<goal_id>/tasks", methods=["GET"])
def get_goal_tasks(goal_id):
    """Get all tasks for a specific goal"""
    goal = get_goal_by_id(goal_id)
    
    if not goal:
        return make_response(jsonify({"error": "Goal not found"}), 404)
    
    return jsonify(goal.to_dict_with_tasks())

@goals_bp.route("/<goal_id>/tasks", methods=["POST"])
def associate_tasks_with_goal(goal_id):
    """Associate multiple tasks with a goal by IDs"""
    goal = get_goal_by_id(goal_id)
    
    if not goal:
        return make_response(jsonify({"error": "Goal not found"}), 404)
    
    request_body = request.get_json()
    task_ids = request_body.get("task_ids", [])
    
    goal.tasks = []
    
    for task_id in task_ids:
        task = db.session.scalar(db.select(Task).where(Task.id == task_id))
        if task:
            goal.tasks.append(task)
    
    db.session.commit()
    
    return jsonify({
        "id": goal.id,
        "task_ids": [task.id for task in goal.tasks]
    })