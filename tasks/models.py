from django.db import models
from django.contrib.auth.models import User

class Team(models.Model):
    """
    Represents a team that can have multiple members and an owner.
    """
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='teams')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_teams')

    def __str__(self):
        return self.name


class Task(models.Model):
    """
    Represents a task assigned to a user within a team.
    """
    TODO = 'todo'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'

    STATUS_CHOICES = [
        (TODO, 'To Do'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=TODO)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class TeamInvite(models.Model):
    """
    Represents a pending or resolved invite to a team.
    """
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    invited_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_invites')
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invites')
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(null=True)  # None = pending, True = accepted, False = declined

    def __str__(self):
        return f"{self.invited_user.username} → {self.team.name}"
