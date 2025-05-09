from flask import Blueprint, request, jsonify, make_response
from ..db import db
from ..models.task import Task
from datetime import datetime
import os
import requests

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

def get_task_by_id(id):
    query = db.select(Task).where(Task.id == id)
    return db.session.scalar(query)

@tasks_bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()
    
    new_task = Task.from_dict(request_body)
    
    if not new_task:
        return make_response(jsonify({"details": "Invalid data"}), 400)
    
    db.session.add(new_task)
    db.session.commit()
    
    return make_response(jsonify({"task": new_task.to_dict()}), 201)

@tasks_bp.route("", methods=["GET"])
def get_all_tasks():
    sort_param = request.args.get("sort")
    
    query = db.select(Task)
    
    if sort_param == "asc":
        query = query.order_by(Task.title.asc())
    elif sort_param == "desc":
        query = query.order_by(Task.title.desc())
    
    tasks = db.session.scalars(query).all()
    
    return jsonify([task.to_dict() for task in tasks])

@tasks_bp.route("/<task_id>", methods=["GET"])
def get_task(task_id):
    task = get_task_by_id(task_id)
    
    if not task:
        return make_response(jsonify({"error": "Task not found"}), 404)
    
    return jsonify({"task": task.to_dict(include_goal_id=True)})

@tasks_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):
    task = get_task_by_id(task_id)
    
    if not task:
        return make_response(jsonify({"error": "Task not found"}), 404)
    
    request_body = request.get_json()
    
    task.title = request_body.get("title", task.title)
    task.description = request_body.get("description", task.description)
    
    db.session.commit()
    
    return make_response("", 204, {"Content-Type": "application/json"})

@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = get_task_by_id(task_id)
    
    if not task:
        return make_response(jsonify({"error": "Task not found"}), 404)
    
    db.session.delete(task)
    db.session.commit()
    
    return make_response("", 204, {"Content-Type": "application/json"})

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_task_complete(task_id):
    task = get_task_by_id(task_id)
    
    if not task:
        return make_response(jsonify({"error": "Task not found"}), 404)
    
    task.completed_at = datetime.now()
    db.session.commit()
    
    # Send a notification to Slack
    slack_token = os.environ.get('SLACK_BOT_TOKEN')
    if slack_token:
        slack_data = {
            'channel': 'task-notifications',
            'text': f"Someone just completed the task {task.title}"
        }
        headers = {
            'Authorization': f'Bearer {slack_token}',
            'Content-Type': 'application/json'
        }
        
        # Make the POST request to Slack API
        slack_response = requests.post(
            'https://slack.com/api/chat.postMessage',
            json=slack_data,
            headers=headers
        )
        
        # Optional: Log the Slack API response for debugging
        print(f"Slack API Response: {slack_response.status_code}, {slack_response.text}")
    
    return make_response("", 204, {"Content-Type": "application/json"})

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_task_incomplete(task_id):
    task = get_task_by_id(task_id)
    
    if not task:
        return make_response(jsonify({"error": "Task not found"}), 404)
    
    task.completed_at = None
    db.session.commit()
    
    return make_response("", 204, {"Content-Type": "application/json"})