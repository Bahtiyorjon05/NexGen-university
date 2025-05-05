from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import (
    UserLoginForm, UserRegistrationForm, ProfileUpdateForm,
    StudentRegistrationForm, FacultyRegistrationForm, StaffRegistrationForm
)

# Home view - landing page
def home(request):
    """Display the home page of the university system."""
    return render(request, 'accounts/home.html')

# Authentication views
def login_view(request):
    """Handle user login and authentication."""
    # If user is already authenticated, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")

                # Redirect to the appropriate dashboard based on user type
                next_page = request.GET.get('next', 'dashboard')
                return redirect(next_page)
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form, 'title': 'Login'})
 

def logout_view(request):
    """Handle user logout successfully"""
    logout(request)
    messages.info(request, "You have been logged out successfuly.")
    return redirect('login')


def register_view(request):
    """Handle new user registration"""
    # If user is logged in redirect to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')    

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Account created for {user.username}! You can now log in.")
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form, 'title': 'Register'})
            

# Profile views
@login_required
def profile_view(request):
    """Display and update the user's profile."""
    if request.method == 'POST':
        profile_form = ProfileUpdateForm(
            request.POST, request.FILES, instance = request.user.profile
        )
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')
    else:
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'profile_form': profile_form,
        'title': 'Profile',
    }
    return render(request, 'accounts/profile.html', context)

# Dashboard view
@login_required
def dashboard_view(request):
    """Display personalized dashboard based on user type."""
    user_type = request.user.profile.user_type

    context = {
        'title': 'Dashboard',
        'user_type': user_type
    }

    if user_type == 'student':
        try:
            student = request.user.profile.student
            context['student'] = student
        except:
            pass
    elif user_type == 'faculty':
        try:
            faculty = request.user.profile.faculty
            context['faculty'] = faculty
        except:
            pass
    
    return render(request, 'accounts/dashboard.html', context)