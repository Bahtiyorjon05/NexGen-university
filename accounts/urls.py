from django.urls import path
from . import views

app_name = 'accounts'

url_patterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    
    # Profile management URLs
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.profile_update_view, name='profile_update'),
    
    # Role-specific registration URLs
    path('student/register/', views.student_registration_view, name='student_register'),
    path('faculty/register/', views.faculty_registration_view, name='faculty_register'),
    path('staff/register/', views.staff_registration_view, name='staff_register'),
    
    # Dashboard URL
    path('dashboard/', views.dashboard_view, name='dashboard'),
]