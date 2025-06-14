from django.db import models
from django.contrib.auth.models import User

class ConnectionRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(null=True, blank=True)  # None = pending, True = accepted, False = rejected

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        status = "Pending" if self.accepted is None else "Accepted" if self.accepted else "Rejected"
        return f"{self.from_user.username} -> {self.to_user.username} [{status}]"
