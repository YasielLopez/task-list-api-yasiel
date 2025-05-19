import os
import requests
from flask import current_app

def send_slack_notification(message):
    """
    Send a notification message to Slack
    Returns True if successful, False otherwise
    """
    slack_token = os.environ.get('SLACK_BOT_TOKEN')
    
    if not slack_token:
        return False
        
    slack_data = {
        'channel': 'task-notifications',
        'text': message
    }
    
    headers = {
        'Authorization': f'Bearer {slack_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        slack_response = requests.post(
            'https://slack.com/api/chat.postMessage',
            json=slack_data,
            headers=headers
        )
        
        if current_app and current_app.debug:
            current_app.logger.debug(f"Slack API Response: {slack_response.status_code}")
            
        return slack_response.status_code == 200
        
    except Exception as e:
        if current_app:
            current_app.logger.error(f"Error sending Slack notification: {str(e)}")
        return False