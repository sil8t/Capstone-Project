from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

# Optional root redirect view
def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('task_list', team_id=request.user.teams.first().id if request.user.teams.exists() else None)
    return redirect('login')

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),

    # Main task app (includes task creation, viewing, team logic)
    path('tasks/', include('tasks.urls')),

    # Django built-in auth views (login, logout, password reset, etc.)
    path('accounts/', include('django.contrib.auth.urls')),

    # Live reload during development
    path('__reload__/', include('django_browser_reload.urls')),

    # Redirect root path to either tasks or login
    path('', root_redirect, name='root_redirect'),
]
