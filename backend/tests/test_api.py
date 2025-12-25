import pytest
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client

def test_get_empty_tasks(client):
    response = client.get('/api/tasks')
    assert response.status_code == 200
    assert json.loads(response.data) == []

def test_create_task(client):
    task_data = {'title': 'Test Task', 'description': 'Test Description'}
    response = client.post('/api/tasks', 
                         data=json.dumps(task_data),
                         content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['title'] == 'Test Task'
    assert data['description'] == 'Test Description'
    assert data['completed'] == False

def test_get_tasks(client):
    # Create a task first
    task_data = {'title': 'Test Task'}
    client.post('/api/tasks', data=json.dumps(task_data), content_type='application/json')
    
    response = client.get('/api/tasks')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['title'] == 'Test Task'

def test_update_task(client):
    # Create a task first
    task_data = {'title': 'Original Task'}
    create_response = client.post('/api/tasks', data=json.dumps(task_data), content_type='application/json')
    task_id = json.loads(create_response.data)['id']
    
    # Update the task
    update_data = {'title': 'Updated Task', 'completed': True}
    response = client.put(f'/api/tasks/{task_id}', 
                        data=json.dumps(update_data), 
                        content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == 'Updated Task'
    assert data['completed'] == True

def test_delete_task(client):
    # Create a task first
    task_data = {'title': 'Task to Delete'}
    create_response = client.post('/api/tasks', data=json.dumps(task_data), content_type='application/json')
    task_id = json.loads(create_response.data)['id']
    
    # Delete the task
    response = client.delete(f'/api/tasks/{task_id}')
    assert response.status_code == 200
    
    # Verify task is deleted
    get_response = client.get(f'/api/tasks/{task_id}')
    assert get_response.status_code == 404