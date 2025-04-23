from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Task, Team, TeamInvite
from .forms import TaskForm, TeamForm, TeamInviteForm


# ───────────────
# AUTHENTICATION
# ───────────────

def signup(request):
    """Handles user sign-up and login upon successful registration."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('root_redirect')
    else:
        form = UserCreationForm()
    return render(request, 'tasks/signup.html', {'form': form})


# ─────────
# TASKS
# ─────────

@login_required
def task_list(request, team_id):
    """Displays tasks for a selected team, separated into 'your' tasks and 'team' tasks."""
    team = get_object_or_404(Team, id=team_id)

    if request.user not in team.members.all():
        return redirect('root_redirect')

    all_tasks = Task.objects.filter(team=team)
    your_tasks = all_tasks.filter(assigned_to=request.user)
    team_tasks = all_tasks.exclude(assigned_to=request.user)

    return render(request, 'tasks/task_list.html', {
        'your_tasks': your_tasks,
        'team_tasks': team_tasks,
        'Task': Task,
        'team': team,
    })


@login_required
def redirect_to_team_tasks(request):
    """Redirects user to their first team’s task list or team creation page."""
    team = request.user.teams.first()
    return redirect('task_list', team_id=team.id) if team else redirect('create_team')


@login_required
def create_task(request, team_id):
    """Creates a new task within a specific team and broadcasts it via WebSocket."""
    team = get_object_or_404(Team, id=team_id)

    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user, team=team)
        if form.is_valid():
            task = form.save(commit=False)
            task.team = team
            task.created_by = request.user
            task.save()

            # Broadcast task creation to team via WebSocket
            html = render_to_string('tasks/partials/task_item.html', {'task': task, 'Task': Task}, request=request)
            async_to_sync(get_channel_layer().group_send)(
                f'team_{team_id}', {
                    'type': 'task_event',
                    'action': 'create',
                    'task_id': task.id,
                    'task_html': html,
                }
            )

            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    form = TaskForm(user=request.user, team=team)
    return render(request, 'tasks/create_task.html', {'form': form, 'team': team})


@login_required
def edit_task(request, team_id, task_id):
    """Allows editing of a task and updates it via WebSocket."""
    team = get_object_or_404(Team, id=team_id)
    task = get_object_or_404(Task, id=task_id, team=team)

    if request.user not in team.members.all():
        return redirect('task_list', team_id=team.id)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user, team=team)
        if form.is_valid():
            form.save()

            html = render_to_string('tasks/partials/task_item.html', {'task': task, 'Task': Task}, request=request)
            async_to_sync(get_channel_layer().group_send)(
                f'team_{team.id}', {
                    'type': 'task_event',
                    'action': 'update',
                    'task_id': task.id,
                    'task_html': html,
                }
            )
            return HttpResponse("")

    else:
        form = TaskForm(instance=task, user=request.user, team=team)

    return render(request, 'tasks/edit_task.html', {'form': form, 'task': task, 'team': team})


@login_required
def delete_task(request, team_id, task_id):
    """Deletes a task and broadcasts the deletion via WebSocket."""
    team = get_object_or_404(Team, id=team_id)
    task = get_object_or_404(Task, id=task_id, team=team)

    if request.user in team.members.all():
        task.delete()
        async_to_sync(get_channel_layer().group_send)(
            f'team_{team_id}', {
                'type': 'task_event',
                'action': 'delete',
                'task_id': task_id,
            }
        )

    return HttpResponse("")


@login_required
def update_task_status(request, team_id, task_id):
    """Updates the task status and notifies other team members via WebSocket."""
    task = get_object_or_404(Task, id=task_id, team__id=team_id)

    if request.user not in task.team.members.all():
        return redirect('task_list', team_id=team_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Task.STATUS_CHOICES):
            task.status = new_status
            task.save()

            html = render_to_string('tasks/partials/task_item.html', {'task': task, 'Task': Task}, request=request)
            async_to_sync(get_channel_layer().group_send)(
                f'team_{task.team.id}', {
                    'type': 'task_event',
                    'action': 'update',
                    'task_id': task.id,
                    'task_html': html,
                }
            )
            return HttpResponse("")

    return redirect('task_list', team_id=team_id)


# ─────────
# TEAMS
# ─────────

@login_required
def create_team(request):
    """Handles creation of a new team and automatically adds the creator as a member."""
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.owner = request.user
            team.save()
            team.members.add(request.user)
            return redirect('task_list', team_id=team.id)
    else:
        form = TeamForm()

    return render(request, 'tasks/create_team.html', {'form': form})


@login_required
def team_detail(request, team_id):
    """Displays team settings, pending invites, and allows inviting members."""
    team = get_object_or_404(Team, id=team_id)

    if request.user not in team.members.all():
        return redirect('task_list', team_id=request.user.teams.first().id)

    message = None
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            invited_user = User.objects.get(username=username)
            if team.members.filter(id=invited_user.id).exists():
                message = f"{username} is already a team member."
            elif TeamInvite.objects.filter(team=team, invited_user=invited_user, accepted__isnull=True).exists():
                message = f"{username} has already been invited."
            else:
                TeamInvite.objects.create(team=team, invited_user=invited_user, invited_by=request.user)
                message = f"Invite sent to {username}!"
                return redirect('team_detail', team_id=team.id)
        except User.DoesNotExist:
            message = f"No user found with username '{username}'"

    invites = TeamInvite.objects.filter(team=team, accepted__isnull=True)
    return render(request, 'tasks/team_detail.html', {
        'team': team,
        'invites': invites,
        'message': message
    })


# ─────────
# INVITES
# ─────────

@login_required
def invite_member(request, team_id):
    """Sends a new invite and notifies the invited user via WebSocket."""
    team = get_object_or_404(Team, id=team_id)

    if request.user not in team.members.all():
        return redirect('task_list', team_id=request.user.teams.first().id)

    message = None
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            invited_user = User.objects.get(username=username)
            if team.members.filter(id=invited_user.id).exists():
                message = f"{username} is already a team member."
            elif TeamInvite.objects.filter(team=team, invited_user=invited_user, accepted__isnull=True).exists():
                message = f"{username} has already been invited."
            else:
                invite = TeamInvite.objects.create(
                    team=team,
                    invited_user=invited_user,
                    invited_by=request.user
                )
                message = f"Invite sent to {username}!"

                # Notify invitee via WebSocket
                async_to_sync(get_channel_layer().group_send)(
                    f"user_{invited_user.id}", {
                        "type": "invite_event",
                        "action": "new_invite",
                        "invite_id": invite.id,
                        "team_name": team.name,
                        "team_id": team.id,
                        "invited_by": request.user.username
                    }
                )
                return redirect('team_detail', team_id=team.id)

        except User.DoesNotExist:
            message = f"No user found with username '{username}'"

    form = TeamInviteForm()
    return render(request, 'tasks/invite_member.html', {
        'form': form,
        'team': team,
        'message': message
    })


@login_required
def manage_invites(request):
    """Lists all pending invites for the logged-in user and handles accept/decline."""
    invites = request.user.team_invites.filter(accepted__isnull=True)

    if request.method == 'POST':
        invite_id = request.POST.get('invite_id')
        action = request.POST.get('action')
        invite = get_object_or_404(TeamInvite, id=invite_id, invited_user=request.user)

        if action == 'accept':
            invite.accepted = True
            invite.team.members.add(request.user)
        elif action == 'decline':
            invite.accepted = False

        invite.save()
        return redirect('manage_invites')

    return render(request, 'tasks/manage_invites.html', {'invites': invites})


@login_required
def delete_team(request, team_id):
    """Allows team owners to delete their team."""
    team = get_object_or_404(Team, id=team_id)

    if team.owner != request.user:
        return redirect('root_redirect')

    if request.method == 'POST':
        team.delete()
        return redirect('root_redirect')


@login_required
def leave_team(request, team_id):
    """Allows members to leave a team (owner cannot leave)."""
    team = get_object_or_404(Team, id=team_id)

    if request.method == 'POST' and request.user in team.members.all():
        if team.owner == request.user:
            return redirect('team_detail', team_id=team.id)
        team.members.remove(request.user)
        return redirect('root_redirect')


@login_required
def root_redirect(request):
    """Redirects authenticated users to their team or to team creation."""
    team = request.user.teams.first()
    return redirect('task_list', team_id=team.id) if team else redirect('create_team')
