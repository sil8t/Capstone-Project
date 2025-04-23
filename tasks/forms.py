from django import forms
from django.contrib.auth.models import User
from .models import Task, Team

class TaskForm(forms.ModelForm):
    """
    Form for creating and editing tasks.
    Restricts 'assigned_to' and 'team' fields to relevant context (user/team).
    """
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'team']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        team = kwargs.pop('team', None)
        super().__init__(*args, **kwargs)

        if team:
            # Limit assignment to members of the selected team
            self.fields['assigned_to'].queryset = User.objects.filter(teams=team).distinct()

            # Lock the team field to the current team
            self.fields['team'].queryset = Team.objects.filter(id=team.id)
            self.fields['team'].initial = team
            self.fields['team'].disabled = True
        elif user:
            # Fall back to all user teams
            self.fields['assigned_to'].queryset = User.objects.filter(teams__in=user.teams.all()).distinct()
            self.fields['team'].queryset = user.teams.all()

class TeamForm(forms.ModelForm):
    """
    Form for creating a new team.
    """
    class Meta:
        model = Team
        fields = ['name']

class TeamInviteForm(forms.Form):
    """
    Simple form to invite users to a team by username.
    """
    username = forms.CharField(label="Invite User by Username")

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError("No user with that username exists.")
        return user
