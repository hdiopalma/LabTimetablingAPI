from django.db.models.signals import post_save
from django.dispatch import receiver
from ..models import Solution

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# @receiver(post_save, sender=Solution)
# def notify_task_completion(sender, instance: Solution, created, **kwargs):
#     '''Send a notification when a solution has completed and is saved to the database. Called automatically when a Solution instance is saved.'''
#     if created:
#         print('Solution created')
#         channel_layer = get_channel_layer()
#         name = instance.name
#         async_to_sync(channel_layer.group_send)(
#             'notifications', # Group name
#             {
#                 'type': 'solution_notification', # Custom function to send the notification
#                 'message': f'{name} has been created' # Message to send
#             }
#         )
    
    # # if status is updated to completed
    # if instance.status == Solution.Status.COMPLETED:
    #     print('Solution completed')
    #     channel_layer = get_channel_layer()
    #     name = instance.name
    #     async_to_sync(channel_layer.group_send)(
    #         'notifications', # Group name
    #         {
    #             'type': 'solution_notification', # Custom function to send the notification
    #             'message': f'{name} has completed' # Message to send
    #         }
    #     )
        

def notify_task(solution: Solution):
    '''Send a notification after huey task has completed.'''
    print('Solution completed')
    channel_layer = get_channel_layer()
    name = solution.name
    status = 'been created' if solution.status == Solution.Status.PENDING else solution.status
    async_to_sync(channel_layer.group_send)(
        'notifications', # Group name
        {
            'type': 'solution_notification', # Custom function to send the notification
            'message': f'{name} has {status}', # Message to send
            'title': 'Solution Status Update'
        }
    )
# Path: scheduling_data/utils/signals.py