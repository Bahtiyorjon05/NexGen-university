from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile, Address, Student, FacultyMember, StaffMember, Alumni
import datetime


# User Login Form
class UserLoginForm(AuthenticationForm):
    """Enhanced login form with better styling"""
    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username or Email'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password'}))
    
    class Meta:
        model = User
        fields = ['username', 'password']

# User Registration Form
class UserRegistrationForm(UserCreationForm):
    """Registration form for new users with validation"""
    first_name = forms.CharField(max_length=30, required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(max_length=254, required=True, 
        widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap styling to all fields
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})
    
    def clean_email(self):
        """Ensure email is unique"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use! 📧")
        return email


# Address Form
class AddressForm(forms.ModelForm):
    """Form for creating and updating addresses"""
    class Meta:
        model = Address
        fields = ['street', 'city', 'region', 'postal_code', 'country']
        widgets = {
            'street': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
        }


# Profile Form
class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile information"""
    class Meta:
        model = Profile
        fields = ['phone_number', 'date_of_birth', 'bio', 'profile_picture', 
                  'emergency_contact']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3
            }),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
        }


# Student Registration Form
class StudentRegistrationForm(forms.ModelForm):
    """Form for student-specific information"""
    class Meta:
        model = Student
        fields = ['student_id', 'enrollment_date', 'expected_graduation', 'major']
        widgets = {
            'student_id': forms.TextInput(attrs={'class': 'form-control'}),
            'enrollment_date': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
            'expected_graduation': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
            'major': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_student_id(self):
        """Validate student ID format and uniqueness"""
        student_id = self.cleaned_data.get('student_id')
        
        # Check format (S followed by numbers)
        if not (student_id.startswith('S') and student_id[1:].isdigit()):
            raise forms.ValidationError("Student ID must start with 'S' followed by numbers.")
        
        # Skip uniqueness check if updating existing record
        if self.instance and self.instance.pk and self.instance.student_id == student_id:
            return student_id
            
        # Check uniqueness
        if Student.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError("This Student ID is already in use! 🔄")
            
        return student_id
    

# Faculty Member Registration Form
class FacultyRegistrationForm(forms.ModelForm):
    """Form for faculty-specific information"""
    class Meta:
        model = FacultyMember
        fields = ['faculty_id', 'position', 'department', 'hire_date', 
                 'highest_degree', 'alma_mater', 'office_location', 
                 'office_hours', 'specialization', 'research_interests']
        widgets = {
            'faculty_id': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'hire_date': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
            'highest_degree': forms.TextInput(attrs={'class': 'form-control'}),
            'alma_mater': forms.TextInput(attrs={'class': 'form-control'}),
            'office_location': forms.TextInput(attrs={'class': 'form-control'}),
            'office_hours': forms.TextInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'research_interests': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3
            }),
        }


# Staff Member Registration Form
class StaffRegistrationForm(forms.ModelForm):
    """Form for administrative staff information"""
    class Meta:
        model = StaffMember
        fields = ['staff_id', 'department', 'position', 'hire_date', 
                 'responsibilities', 'supervisor', 'admin_level']
        widgets = {
            'staff_id': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'hire_date': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
            'responsibilities': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3
            }),
            'supervisor': forms.Select(attrs={'class': 'form-control'}),
            'admin_level': forms.Select(attrs={'class': 'form-control'}),
        }


# Alumni Form
class AlumniUpdateForm(forms.ModelForm):
    """Form for tracking graduates and their careers"""
    class Meta:
        model = Alumni
        fields = ['graduation_year', 'degree', 'current_employer', 
                 'job_title', 'personal_email']
        widgets = {
            'graduation_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'degree': forms.TextInput(attrs={'class': 'form-control'}),
            'current_employer': forms.TextInput(attrs={'class': 'form-control'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control'}),
            'personal_email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def clean_graduation_year(self):
        """Ensure graduation year isn't in the future"""
        year = self.cleaned_data.get('graduation_year')
        current_year = datetime.date.today().year
        
        if year > current_year:
            raise forms.ValidationError("Time travel not invented yet! 🕰️ Graduation year can't be in the future.")
            
        return year

