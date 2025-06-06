import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from app.models.task import Task
from app.db import db
import pytest

def test_mark_complete_on_incomplete_task(client, one_task):
    # Arrange
    with patch("requests.post") as mock_get:
        mock_get.return_value.status_code = 200

        # Act
        response = client.patch("/tasks/1/mark_complete")

    # Assert
    assert response.status_code == 204
    
    query = db.select(Task).where(Task.id == 1)
    assert db.session.scalar(query).completed_at

def test_mark_incomplete_on_complete_task(client, completed_task):
    # Act
    response = client.patch("/tasks/1/mark_incomplete")
    
    # Assert
    assert response.status_code == 204
    query = db.select(Task).where(Task.id == 1)
    assert db.session.scalar(query).completed_at == None

def test_mark_complete_on_completed_task(client, completed_task):
    # Arrange
    with patch("requests.post") as mock_get:
        mock_get.return_value.status_code = 200

        # Act
        response = client.patch("/tasks/1/mark_complete")
    
    # Assert
    assert response.status_code == 204

    query = db.select(Task).where(Task.id == 1)
    assert db.session.scalar(query).completed_at

def test_mark_incomplete_on_incomplete_task(client, one_task):
    # Act
    response = client.patch("/tasks/1/mark_incomplete")

    # Assert
    assert response.status_code == 204

    query = db.select(Task).where(Task.id == 1)
    assert db.session.scalar(query).completed_at == None

def test_mark_complete_missing_task(client):
    # Act
    response = client.patch("/tasks/1/mark_complete")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 404
    assert "error" in response_body
    assert response_body["error"] == "Task not found"

def test_mark_incomplete_missing_task(client):
    # Act
    response = client.patch("/tasks/1/mark_incomplete")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 404
    assert "error" in response_body
    assert response_body["error"] == "Task not found"