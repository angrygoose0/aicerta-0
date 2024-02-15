from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import NceaUserDocument, Assignment
from channels.db import database_sync_to_async



class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.groups = []
        user = self.scope['user']
        self.room_name = f"user_{user.id}"
        self.groups.append(self.room_name)
        await self.channel_layer.group_add(self.room_name, self.channel_name)

        if user.student:
            documents = await self.get_student_documents(user)
            
            for document in documents:
                group_name = self.teacher_student_group(document.assignment.teacher.id, user.id, document.id)
                self.groups.append(group_name)
                await self.channel_layer.group_add(group_name, self.channel_name)
        else:  # Assuming non-students are teachers
            documents = await self.get_teacher_documents(user)
            for document in documents:
                group_name = self.teacher_student_group(user.id, document.user.id, document.id)
                self.groups.append(group_name)
                await self.channel_layer.group_add(group_name, self.channel_name)

        
        print(f"User {user.id} is in groups: {self.groups}")
        await self.accept()

    async def disconnect(self, close_code):
        for group in self.groups:
            await self.channel_layer.group_discard(group, self.channel_name)

    @database_sync_to_async
    def get_student_documents(self, user):
        return list(NceaUserDocument.objects.filter(user=user, assignment__isnull=False).select_related('assignment__teacher'))

    @database_sync_to_async
    def get_teacher_documents(self, user):
        assignments = Assignment.objects.filter(teacher=user)
        return list(NceaUserDocument.objects.filter(assignment__in=assignments).select_related('user'))

    @database_sync_to_async
    def get_teacher_id(self, doc):
        return doc.assignment.teacher.id
    
    def teacher_student_group(self, teacher_id, student_id, document_id):
        return f"doc_{document_id}_teacher_{teacher_id}_student_{student_id}"

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('message_type')
        
        if message_type == 'update_status':
            await self.handle_status_update(text_data_json)
        pass

    async def handle_status_update(self, data):
        document_id = data['document_id']
        status = data['status']
        assignment_id = data['assignment_id']
        
        # Update document status and get the updated document
        doc = await self.update_document_status(document_id, status)
        
        teacher_id = await self.get_teacher_id(doc)
        student_id = await self.get_student_id_from_doc(doc)
        
        group_name = self.teacher_student_group(teacher_id, student_id, document_id)

        # Prepare the message
        message = json.dumps({
            'message_type': 'update_status',
            'status': status,
            'document_id': document_id,
            'assignment_id' : assignment_id
        })

        # Send the message to the specific group
        await self.channel_layer.group_send(
            group_name,
            {
                'type': 'send.message',
                'message': message
            }
        )
        
    @database_sync_to_async
    def get_student_id_from_doc(self, doc):
        return doc.user.id
    
    @database_sync_to_async
    def update_document_status(self, document_id, status):
        doc = NceaUserDocument.objects.get(id=document_id)
        doc.status = status
        doc.save()
        return doc
    
    async def send_message(self, event):
        await self.send(text_data=event['message'])

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

        