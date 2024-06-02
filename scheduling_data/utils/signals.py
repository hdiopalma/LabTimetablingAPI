from django.db.models.signals import post_save
from django.dispatch import receiver
from ..models import Solution

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import requests

def telegram_notification(message):
        TOKEN = "7457808512:AAG76voBl0muxo5bDLLQjIf8kMj-8tkyIL0"
        chat_id = "-1002213633588"
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
        response = requests.get(url)
        return response.json()        

def notify_task(solution: Solution):
    '''Send a notification after huey task has completed.'''
    print('Solution completed')
    channel_layer = get_channel_layer()
    name = solution.name
    status = 'been created' if solution.status == Solution.Status.PENDING else solution.status
    message = f'{name} has {status}'
    async_to_sync(channel_layer.group_send)(
        'notifications', # Group name
        {
            'type': 'solution_notification', # Custom function to send the notification
            'message': message,
            'title': 'Solution Status Update'
        }
    )
    telegram_notification(message)
    
# Path: scheduling_data/utils/signals.py