from flask import Flask, request
from .db import db, migrate
from .routes.task_routes import bp as tasks_bp
from .routes.goal_routes import bp as goals_bp
from .models import task, goal
import os

def create_app(config=None):
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
    
    if config:
        app.config.update(config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    app.register_blueprint(tasks_bp)
    app.register_blueprint(goals_bp)
    
    @app.errorhandler(404)
    def handle_not_found(e):
        if request.path.startswith('/goals'):
            return {"error": "Goal not found"}, 404
        elif request.path.startswith('/tasks'):
            return {"error": "Task not found"}, 404
        else:
            return {"error": "Not found"}, 404
    
    @app.errorhandler(400)
    def handle_bad_request(e):
        return {"details": "Invalid data"}, 400
    
    return app