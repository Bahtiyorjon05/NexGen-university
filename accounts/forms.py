


from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import Profile, Address, Student, FacultyMember, StaffMember, Alumni
import datetime
import re


class BootstrapFormMixin:
    """
    Mixin that applies Bootstrap styling to form fields.
    
    This mixin automatically adds the 'form-control' class to all form widgets 
    except for those that don't work well with it (like file inputs).
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Skip file fields which don't work well with form-control
            if not isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({'class': 'form-control'})


def get_bootstrap_widget(field_type='text', **attrs):
    """
    Factory function that returns properly configured form widgets with Bootstrap styling.
    
    Args:
        field_type: The type of field/widget to create 
                   ('text', 'textarea', 'date', 'select', 'email', 'number', 'password')
        attrs: Additional attributes to add to the widget
        
    Returns:
        A configured form widget with Bootstrap styling
    """
    base_attrs = {'class': 'form-control'}
    base_attrs.update(attrs)
    
    widget_map = {
        'text': forms.TextInput(attrs=base_attrs),
        'textarea': forms.Textarea(attrs={**base_attrs, 'rows': attrs.get('rows', 3)}),
        'date': forms.DateInput(attrs={**base_attrs, 'type': 'date'}),
        'select': forms.Select(attrs=base_attrs),
        'email': forms.EmailInput(attrs=base_attrs),
        'number': forms.NumberInput(attrs=base_attrs),
        'password': forms.PasswordInput(attrs=base_attrs),
        'file': forms.FileInput(attrs={**base_attrs, 'class': 'form-control-file'}),
        'checkbox': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    }
    
    return widget_map.get(field_type, forms.TextInput(attrs=base_attrs))


# Authentication Forms
class UserLoginForm(BootstrapFormMixin, AuthenticationForm):
    """
    Enhanced login form with improved styling and user experience.
    
    Extends Django's built-in AuthenticationForm with Bootstrap styling and 
    user-friendly placeholders.
    """
    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username or Email'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password'}))
    
    class Meta:
        model = User
        fields = ['username', 'password']


class UserRegistrationForm(BootstrapFormMixin, UserCreationForm):
    """
    Registration form for new users with comprehensive validation.
    
    Collects all required user information and performs validation to ensure 
    data integrity and uniqueness.
    """
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        help_text="Your first name"
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        help_text="Your last name"
    )
    email = forms.EmailField(
        max_length=254, 
        required=True,
        help_text="Required. Enter a valid email address."
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        help_texts = {
            'username': 'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        }
    
    def clean_email(self):
        """
        Validate that the email is unique in the system.
        
        Emails must be unique to prevent duplicate accounts and ensure
        password recovery works correctly.
        
        Returns:
            str: The validated email address
            
        Raises:
            ValidationError: If the email is already registered
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use! 📧")
        return email


# Profile-Related Forms
class AddressForm(BootstrapFormMixin, forms.ModelForm):
    """
    Form for creating and updating physical addresses.
    
    Handles all address components with appropriate validation.
    """
    class Meta:
        model = Address
        fields = ['street', 'city', 'region', 'postal_code', 'country']
        help_texts = {
            'street': 'Street address including house/apartment number',
            'postal_code': 'ZIP or postal code for your area',
        }
    
    def clean_postal_code(self):
        """
        Validate postal code format if country is Uzbekistan.
        
        Uzbekistan postal codes are 6 digits.
        """
        postal_code = self.cleaned_data.get('postal_code')
        country = self.cleaned_data.get('country')
        
        if postal_code and country and country.lower() == 'uzbekistan':
            if not re.match(r'^\d{6}$', postal_code):
                raise forms.ValidationError("Uzbekistan postal codes must be 6 digits.")
        
        return postal_code


class ProfileUpdateForm(BootstrapFormMixin, forms.ModelForm):
    """
    Form for updating common user profile information.
    
    Used by all user types to update their profile details.
    """
    # Add custom validation for phone numbers
    phone_number = forms.CharField(
        required=False,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    
    class Meta:
        model = Profile
        fields = ['phone_number', 'date_of_birth', 'bio', 'profile_picture', 
                  'emergency_contact']
        help_texts = {
            'profile_picture': 'Upload a professional photo (JPG, PNG)',
            'emergency_contact': 'Name and phone number of emergency contact',
            'bio': 'Brief description about yourself',
        }
        widgets = {
            'date_of_birth': get_bootstrap_widget('date'),
            'bio': get_bootstrap_widget('textarea', rows=4),
        }
    
    def clean_date_of_birth(self):
        """
        Validate that date of birth is in the past and user is at least 16.
        
        Returns:
            date: The validated date of birth
            
        Raises:
            ValidationError: If the date is invalid
        """
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = datetime.date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            
            if dob > today:
                raise forms.ValidationError("Date of birth cannot be in the future.")
                
            if age < 16:
                raise forms.ValidationError("You must be at least 16 years old.")
                
        return dob


# Role-Specific Forms
class StudentRegistrationForm(BootstrapFormMixin, forms.ModelForm):
    """
    Form for creating and updating student-specific information.
    
    Handles academic information with validation for student records.
    """
    class Meta:
        model = Student
        fields = ['student_id', 'enrollment_date', 'expected_graduation', 'major']
        help_texts = {
            'student_id': 'Must start with S followed by numbers (e.g., S12345)',
            'enrollment_date': 'Date when you started your program',
            'expected_graduation': 'Anticipated graduation date',
            'major': 'Your primary field of study',
        }
        widgets = {
            'enrollment_date': get_bootstrap_widget('date'),
            'expected_graduation': get_bootstrap_widget('date'),
        }
    
    def clean_student_id(self):
        """
        Validate student ID format and uniqueness.
        
        Student IDs must start with 'S' followed by numbers and be unique in the system.
        
        Returns:
            str: The validated student ID
            
        Raises:
            ValidationError: If the ID format is invalid or already exists
        """
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
    
    def clean(self):
        """
        Validate enrollment and graduation dates are logical.
        
        Ensures enrollment date is before graduation date and within reasonable timeframe.
        
        Returns:
            dict: The cleaned data
            
        Raises:
            ValidationError: If dates don't make logical sense
        """
        cleaned_data = super().clean()
        enrollment_date = cleaned_data.get('enrollment_date')
        expected_graduation = cleaned_data.get('expected_graduation')
        
        if enrollment_date and expected_graduation:
            # Typical degree duration range
            min_years = 2
            max_years = 8
            
            if expected_graduation < enrollment_date:
                self.add_error('expected_graduation', 
                               "Graduation date cannot be before enrollment date.")
                
            # Check for reasonable timeframe
            duration_days = (expected_graduation - enrollment_date).days
            duration_years = duration_days / 365.25
            
            if duration_years < min_years:
                self.add_error('expected_graduation', 
                    f"Graduation date should be at least {min_years} years after enrollment.")
            
            if duration_years > max_years:
                self.add_error('expected_graduation',
                    f"Graduation date should be within {max_years} years of enrollment.")
                
        return cleaned_data


class FacultyRegistrationForm(BootstrapFormMixin, forms.ModelForm):
    """
    Form for creating and updating faculty-specific information.
    
    Handles academic and professional information for faculty members.
    """
    class Meta:
        model = FacultyMember
        fields = ['faculty_id', 'position', 'department', 'hire_date', 
                 'highest_degree', 'alma_mater', 'office_location', 
                 'office_hours', 'specialization', 'research_interests']
        help_texts = {
            'faculty_id': 'Unique faculty identification number',
            'position': 'Academic rank or position',
            'highest_degree': 'Highest academic qualification (e.g., Ph.D., M.Sc.)',
            'research_interests': 'Areas of research or academic focus',
        }
        widgets = {
            'hire_date': get_bootstrap_widget('date'),
            'research_interests': get_bootstrap_widget('textarea', rows=4),
        }
    
    def clean_faculty_id(self):
        """
        Validate faculty ID format and uniqueness.
        
        Returns:
            str: The validated faculty ID
            
        Raises:
            ValidationError: If the ID is invalid or already exists
        """
        faculty_id = self.cleaned_data.get('faculty_id')
        
        # Check format (F followed by numbers)
        if not (faculty_id.startswith('F') and faculty_id[1:].isdigit()):
            raise forms.ValidationError("Faculty ID must start with 'F' followed by numbers.")
        
        # Skip uniqueness check if updating existing record
        if self.instance and self.instance.pk and self.instance.faculty_id == faculty_id:
            return faculty_id
            
        # Check uniqueness
        if FacultyMember.objects.filter(faculty_id=faculty_id).exists():
            raise forms.ValidationError("This Faculty ID is already in use!")
            
        return faculty_id
    
    def clean_hire_date(self):
        """
        Validate that hire date is not in the future.
        
        Returns:
            date: The validated hire date
            
        Raises:
            ValidationError: If the date is invalid
        """
        hire_date = self.cleaned_data.get('hire_date')
        if hire_date and hire_date > datetime.date.today():
            raise forms.ValidationError("Hire date cannot be in the future.")
        return hire_date


class StaffRegistrationForm(BootstrapFormMixin, forms.ModelForm):
    """
    Form for creating and updating staff-specific information.
    
    Handles administrative staff details and role information.
    """
    class Meta:
        model = StaffMember
        fields = ['staff_id', 'department', 'position', 'hire_date', 
                 'responsibilities', 'supervisor', 'admin_level']
        help_texts = {
            'staff_id': 'Unique staff identification number',
            'position': 'Job title or role',
            'responsibilities': 'Key duties and responsibilities',
            'admin_level': 'System access permission level',
        }
        widgets = {
            'hire_date': get_bootstrap_widget('date'),
            'responsibilities': get_bootstrap_widget('textarea', rows=4),
        }
    
    def clean_staff_id(self):
        """
        Validate staff ID format and uniqueness.
        
        Returns:
            str: The validated staff ID
            
        Raises:
            ValidationError: If the ID is invalid or already exists
        """
        staff_id = self.cleaned_data.get('staff_id')
        
        # Check format (A followed by numbers for administrative staff)
        if not (staff_id.startswith('A') and staff_id[1:].isdigit()):
            raise forms.ValidationError("Staff ID must start with 'A' followed by numbers.")
        
        # Skip uniqueness check if updating existing record
        if self.instance and self.instance.pk and self.instance.staff_id == staff_id:
            return staff_id
            
        # Check uniqueness
        if StaffMember.objects.filter(staff_id=staff_id).exists():
            raise forms.ValidationError("This Staff ID is already in use!")
            
        return staff_id
    
    def clean(self):
        """
        Perform cross-field validation for staff information.
        
        Validates supervisor relationships and other staff-specific constraints.
        
        Returns:
            dict: The cleaned data
            
        Raises:
            ValidationError: If validation fails
        """
        cleaned_data = super().clean()
        supervisor = cleaned_data.get('supervisor')
        admin_level = cleaned_data.get('admin_level')
        
        # Ensure supervisor has higher or equal admin level
        if supervisor and admin_level:
            if supervisor.admin_level < admin_level:
                self.add_error('supervisor', 
                              "Supervisor must have an equal or higher access level than subordinate.")
        
        return cleaned_data


class AlumniUpdateForm(BootstrapFormMixin, forms.ModelForm):
    """
    Form for tracking graduates and their post-graduation careers.
    
    Handles alumni information including employment and contact details.
    """
    class Meta:
        model = Alumni
        fields = ['graduation_year', 'degree', 'current_employer', 
                 'job_title', 'personal_email']
        help_texts = {
            'graduation_year': 'Year when you completed your degree',
            'degree': 'Qualification obtained (e.g., B.Sc. Computer Science)',
            'personal_email': 'Email address other than your university account',
        }
    
    def clean_graduation_year(self):
        """
        Validate that graduation year is historically accurate.
        
        Ensures the year is not in the future and is within the university's
        operational timeline.
        
        Returns:
            int: The validated graduation year
            
        Raises:
            ValidationError: If the year is invalid
        """
        year = self.cleaned_data.get('graduation_year')
        current_year = datetime.date.today().year
        founding_year = 1950  # Assuming the university was founded in 1950
        
        if year > current_year:
            raise forms.ValidationError("Time travel not invented yet! 🕰️ Graduation year can't be in the future.")
        
        if year < founding_year:
            raise forms.ValidationError(f"The university wasn't established until {founding_year}.")
            
        return year
    
    def clean_personal_email(self):
        """
        Validate personal email format and uniqueness.
        
        Returns:
            str: The validated email
            
        Raises:
            ValidationError: If the email is invalid
        """
        email = self.cleaned_data.get('personal_email')
        
        # Skip if email is not provided (it's optional)
        if not email:
            return email
            
        # Check that personal email is different from university email
        if self.instance and self.instance.student and self.instance.student.profile.user.email == email:
            raise forms.ValidationError("Personal email should be different from your university email.")
            
        return email