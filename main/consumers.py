from channels.generic.websocket import AsyncWebsocketConsumer
import json

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['user'].id  # assuming the user is authenticated
        self.room_name = f"user_{self.user_id}"
        print(self.room_name)
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        pass

    async def notification_message(self, event):
        task_id = event['task_id']
        user_document_name = event['user_document_name']
        exam_name = event['exam_name']
        progress = event['progress']
        doc_id = event['doc_id']
        error = event['error']
        
        await self.send(text_data=json.dumps({
            'message_type' : 'notification',
            'task_id': task_id,
            'user_document_name': user_document_name,
            'exam_name': exam_name,
            'progress': progress,
            'doc_id': doc_id,
            'error':error,
            
        }))
    
    async def alert_message(self, event):
        message = event['message']
        alert = event['alert']
        icon = event['icon']

        # Constructing the message with assignment and document names
        await self.send(text_data=json.dumps({
            'message_type': 'alert',
            'message': message,
            'alert': alert,
            'icon': icon,
        }))

        