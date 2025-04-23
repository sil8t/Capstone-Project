from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # ────────────────
    # Authentication
    # ────────────────
    path('accounts/login/', auth_views.LoginView.as_view(template_name='tasks/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('accounts/signup/', views.signup, name='signup'),

    # ────────────────
    # Home / Redirect
    # ────────────────
    path('', views.root_redirect, name='root_redirect'),

    # ────────────────
    # Task Management (scoped by team)
    # ────────────────
    path('team/<int:team_id>/', views.task_list, name='task_list'),
    path('team/<int:team_id>/new/', views.create_task, name='create_task'),
    path('team/<int:team_id>/edit/<int:task_id>/', views.edit_task, name='edit_task'),
    path('team/<int:team_id>/delete/<int:task_id>/', views.delete_task, name='delete_task'),
    path('team/<int:team_id>/status/<int:task_id>/', views.update_task_status, name='update_task_status'),

    # ────────────────
    # Team Management
    # ────────────────
    path('team/new/', views.create_team, name='create_team'),
    path('teams/<int:team_id>/', views.team_detail, name='team_detail'),
    path('teams/<int:team_id>/invite/', views.invite_member, name='invite_member'),
    path('team/<int:team_id>/delete/', views.delete_team, name='delete_team'),
    path('team/<int:team_id>/leave/', views.leave_team, name='leave_team'),

    # ────────────────
    # Invite Inbox
    # ────────────────
    path('invites/', views.manage_invites, name='manage_invites'),
]
