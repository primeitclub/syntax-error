from django.db import models
from django.utils import timezone
from Accounts.models import Student  

class ConnectionRequest(models.Model):
    sender = models.ForeignKey(Student, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(Student, related_name='received_requests', on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_REJECTED, 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"Request from {self.sender.user_name} to {self.receiver.user_name} - {self.status}"


class Connection(models.Model):
    student1 = models.ForeignKey(Student, related_name='connections1', on_delete=models.CASCADE)
    student2 = models.ForeignKey(Student, related_name='connections2', on_delete=models.CASCADE)
    connected_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('student1', 'student2')

    def __str__(self):
        return f"{self.student1.user_name} <-> {self.student2.user_name}"
