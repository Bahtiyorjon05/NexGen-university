



from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator 
from dateutil.relativedelta import relativedelta
import logging

logger = logging.getLogger(__name__)



# NexGen University Accounts

class Address(models.Model):
    """
    Physical address information that can be reused across the system.
    This is a separate model to avoid duplicating address fields in multiple models.
    """
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True, null=True)    
    country = models.CharField(max_length=100, default='Uzbekistan')

    def __str__(self):
        """Return a string representation of the address"""
        return f"{self.street}, {self.city}, {self.region}, {self.country}"
    
    def get_full_address(self):
        """Returns a formatted full address with optional postal code"""
        address_parts = [self.street, self.city, self.region]
        if self.postal_code:
            address_parts.append(self.postal_code)
        address_parts.append(self.country)
        return ", ".join(address_parts)
    
    def clean(self):
        """Validate that required fields are provided"""
        if not self.street or not self.city or not self.region:
            raise ValidationError("Street, city, and region are required fields.")
    
    class Meta: 
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
        ordering = ['country', 'region', 'city', 'street']
        indexes = [
            models.Index(fields=['city']),
            models.Index(fields=['country', 'region']),
        ]


class Profile(models.Model):
    """
    Base profile information for all university users.
    This model extends Django's built-in User model with additional information.
    """
    # Link to Django's built-in User model with cascade deletion
    # If User is deleted, Profile will be deleted too
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,  # Delete profile when user is deleted
        related_name='profile'     # Allows reverse lookup: user.profile
    )
    
    # User type choices - defines the role of the user in the university
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty Member'),
        ('staff', 'Administrative Staff'),
        ('admin', 'Administrator'),
        ('other', 'Other')
    )
    user_type = models.CharField(
        max_length=20, 
        choices=USER_TYPE_CHOICES,
        default='other',
        db_index=True  # Add index for faster filtering by user type
    )
    
    # Basic personal information
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True)
    
    # Contact information
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact = models.CharField(max_length=100, blank=True, null=True)
    
    # Physical address - references the Address model
    address = models.ForeignKey(
        Address, 
        on_delete=models.SET_NULL,  # Set to NULL if address is deleted
        null=True, 
        blank=True
    )
    
    # Profile picture with upload path to media/profile_pics/
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        null=True, 
        blank=True
    )
    
    # Account status and dates
    is_active = models.BooleanField(default=True, db_index=True)  # Add index for faster queries
    date_joined = models.DateTimeField(default=timezone.now)  # Use timezone-aware datetime
    last_updated = models.DateTimeField(auto_now=True)     # Updated on each save
    
    def __str__(self):
        """String representation of profile - shows username and type"""
        return f"{self.user.username} ({self.get_user_type_display()})"
    
    def get_age(self):
        """Calculate age based on date of birth"""
        if not self.date_of_birth:
            return None
        today = timezone.now().date()
        delta = relativedelta(today, self.date_of_birth)
        return delta.years
    
    def get_full_contact_info(self):
        """Return full contact information"""
        info = {
            'email': self.user.email,
            'phone': self.phone_number or 'Not provided',
            'emergency_contact': self.emergency_contact or 'Not provided',
            'address': self.address.get_full_address() if self.address else 'No address registered'
        }
        return info
    
    def clean(self):
        """Validate profile data"""
        # Check if date of birth is in the future
        if self.date_of_birth and self.date_of_birth > timezone.now().date():
            raise ValidationError({'date_of_birth': 'Date of birth cannot be in the future.'})
        
        # Validate minimum age (16 years)
        if self.date_of_birth:
            age = self.get_age()
            if age is not None and age < 16:
                raise ValidationError({'date_of_birth': 'User must be at least 16 years old.'})
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ['user__username']
        indexes = [
            models.Index(fields=['user_type', 'is_active']),
            models.Index(fields=['date_joined']),
        ]


class Student(models.Model):
    """
    Student-specific information model.
    Contains academic information specific to students.
    """
    # Link to Profile model with cascade deletion
    profile = models.OneToOneField(
        Profile, 
        on_delete=models.CASCADE,
        related_name='student'  # Allows reverse lookup: profile.student
    )

    # Student ID - unique identifier for each student
    student_id = models.CharField(
        max_length=20, 
        unique=True,
        db_index=True,
        help_text="Unique student identification number"
    )

    # Academic information
    enrollment_date = models.DateField()
    expected_graduation = models.DateField(null=True, blank=True)
    major = models.CharField(max_length=100, blank=True, db_index=True)  # Add index for filtering by major

    # Academic status choices
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('on_leave', 'On Leave'),
        ('graduated', 'Graduated'),
        ('withdrawn', 'Withdrawn'),
        ('suspended', 'Suspended')
    )

    academic_status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='active',
        db_index=True
    )

    # Additional academic information
    gpa = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Grade Point Average (0.00 - 4.00)",
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(4.0)
        ]
    )
    credits_completed = models.PositiveIntegerField(default=0)

    def __str__(self):
        """String representation of student"""
        return f"Student: {self.profile.user.get_full_name() or self.profile.user.username}"
    
    def get_enrollment_duration(self):
        """Return the duration of enrollment in years and months"""
        if not self.enrollment_date:
            return "Unknown"
        today = timezone.now().date()
        delta = relativedelta(today, self.enrollment_date)
        return f"{delta.years} years, {delta.months} months"
    
    def get_expected_time_to_graduation(self):
        """Calculate time remaining until expected graduation"""
        if not self.expected_graduation:
            return "No graduation date set"
        
        today = timezone.now().date()
        if self.expected_graduation < today:
            return "Past expected graduation date"
        
        delta = relativedelta(self.expected_graduation, today)
        if delta.years > 0:
            return f"{delta.years} years, {delta.months} months"
        elif delta.months > 0:
            return f"{delta.months} months, {delta.days} days"
        else:
            return f"{delta.days} days"
    
    def is_graduating_soon(self, days=90):
        """Check if student is graduating within specified days"""
        if not self.expected_graduation:
            return False
        return (self.expected_graduation - timezone.now().date()).days <= days
    
    def is_on_track(self):
        """Check if student is on track based on credits completed"""
        if not self.enrollment_date or not self.expected_graduation:
            return None  # Can't determine
        
        # Calculate expected credits
        total_duration = relativedelta(self.expected_graduation, self.enrollment_date)
        total_months = total_duration.years * 12 + total_duration.months
        typical_credits_per_semester = 15  # Typically 15 credits per semester
        expected_credits = (total_months / 6) * typical_credits_per_semester
        
        # Student is on track if they have at least 90% of expected credits
        return self.credits_completed >= (expected_credits * 0.9)
    
    def clean(self):
        """Validate student data"""
        # Ensure enrollment date is not in the future
        if self.enrollment_date and self.enrollment_date > timezone.now().date():
            raise ValidationError({'enrollment_date': 'Enrollment date cannot be in the future.'})
        
        # Check that expected graduation is after enrollment
        if self.enrollment_date and self.expected_graduation and self.expected_graduation <= self.enrollment_date:
            raise ValidationError({'expected_graduation': 'Expected graduation must be after enrollment date.'})
        
        # Format validation for student_id
        if not self.student_id.startswith('S') or not self.student_id[1:].isdigit():
            raise ValidationError({'student_id': 'Student ID must start with "S" followed by numbers.'})
        
        # Ensure profile type matches
        if self.profile.user_type != 'student':
            self.profile.user_type = 'student'
            self.profile.save()
            logger.info(f"Updated profile type to 'student' for user {self.profile.user.username}")
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation and proper profile type"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        ordering = ['student_id']
        indexes = [
            models.Index(fields=['academic_status']),
            models.Index(fields=['enrollment_date']),
            models.Index(fields=['gpa']),
        ]


class FacultyMember(models.Model):
    """
    Faculty-specific information model.
    Contains information about faculty members (professors, instructors, etc.).
    """
    # Link to Profile model with cascade deletion
    profile = models.OneToOneField(
        Profile, 
        on_delete=models.CASCADE,
        related_name='faculty'  # Allows reverse lookup: profile.faculty
    )

    # Faculty ID - unique identifier for each faculty member
    faculty_id = models.CharField(
        max_length=20, 
        unique=True,
        db_index=True,
        help_text="Unique faculty identification number"
    )

    # Position/title choices
    POSITION_CHOICES = (
        ('professor', 'Professor'),
        ('assoc_professor', 'Associate Professor'),
        ('asst_professor', 'Assistant Professor'),
        ('lecturer', 'Lecturer'),
        ('instructor', 'Instructor'),
        ('adjunct', 'Adjunct Faculty'),
        ('other', 'Other')
    )
    position = models.CharField(
        max_length=20, 
        choices=POSITION_CHOICES,
        db_index=True  # Add index for filtering by position
    )

    # Employment information
    hire_date = models.DateField()
    department = models.CharField(max_length=100, db_index=True)
    
    # Academic background
    highest_degree = models.CharField(max_length=100, blank=True)
    alma_mater = models.CharField(max_length=255, blank=True, null=True)
    
    # Office and accessibility information
    office_location = models.CharField(max_length=100, blank=True)
    office_hours = models.CharField(max_length=100, blank=True)
    
    # Academic focus
    specialization = models.CharField(max_length=255, blank=True)
    research_interests = models.TextField(blank=True)

    def __str__(self):
        """String representation of faculty member"""
        name = self.profile.user.get_full_name() or self.profile.user.username
        return f"Faculty: {name} ({self.get_position_display()})"
    
    def get_employment_duration(self):
        """Calculate the duration of employment"""
        today = timezone.now().date()
        delta = relativedelta(today, self.hire_date)
        return f"{delta.years} years, {delta.months} months"
    
    def is_tenured(self):
        """Determine if faculty member is tenured based on position and duration"""
        tenured_positions = ['professor', 'assoc_professor']
        if self.position in tenured_positions:
            return True
        
        # Assume assistant professors get tenure after 7 years
        if self.position == 'asst_professor':
            delta = relativedelta(timezone.now().date(), self.hire_date)
            return delta.years >= 7
            
        return False
    
    def get_courses_taught(self):
        """
        Returns a QuerySet of courses taught by this faculty member.
        Note: Requires linking to a Course model in a separate app.
        """
        # This is a placeholder - implement when Course model is available
        return []
    
    def clean(self):
        """Validate faculty data"""
        # Ensure hire date is not in the future
        if self.hire_date and self.hire_date > timezone.now().date():
            raise ValidationError({'hire_date': 'Hire date cannot be in the future.'})
        
        # Ensure profile type matches
        if self.profile.user_type != 'faculty':
            self.profile.user_type = 'faculty'
            self.profile.save()
            logger.info(f"Updated profile type to 'faculty' for user {self.profile.user.username}")
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation and proper profile type"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Faculty Member"
        verbose_name_plural = "Faculty Members"
        ordering = ['faculty_id']
        indexes = [
            models.Index(fields=['department', 'position']),
            models.Index(fields=['hire_date']),
        ]


class StaffMember(models.Model):
    """
    Administrative staff-specific information model.
    Contains information about non-faculty staff members.
    """
    # Link to Profile model with cascade deletion
    profile = models.OneToOneField(
        Profile, 
        on_delete=models.CASCADE,
        related_name='staff'  # Allows reverse lookup: profile.staff
    )
    
    # Staff ID - unique identifier for each staff member
    staff_id = models.CharField(
        max_length=20, 
        unique=True,
        db_index=True,
        help_text="Unique staff identification number"
    )
    
    # Employment information
    department = models.CharField(max_length=100, db_index=True)
    position = models.CharField(max_length=100)
    hire_date = models.DateField()
    
    # Job details
    responsibilities = models.TextField(blank=True)
    supervisor = models.ForeignKey(
        'self',  # Self-reference to allow staff hierarchy
        on_delete=models.SET_NULL,
        null=True, 
        blank=True, 
        related_name='subordinates'
    )
    
    # Administrative access level
    ADMIN_LEVEL_CHOICES = (
        (1, 'Basic'),
        (2, 'Intermediate'),
        (3, 'Advanced'),
        (4, 'Full Access')
    )
    admin_level = models.PositiveSmallIntegerField(
        choices=ADMIN_LEVEL_CHOICES,
        default=1
    )
    
    def __str__(self):
        """String representation of staff member"""
        name = self.profile.user.get_full_name() or self.profile.user.username
        return f"Staff: {name} ({self.position})"
    
    def get_employment_duration(self):
        """Calculate the duration of employment"""
        today = timezone.now().date()
        delta = relativedelta(today, self.hire_date)
        return f"{delta.years} years, {delta.months} months"
    
    def get_admin_level_display_emoji(self):
        """Return admin level with emoji indicator"""
        level_emojis = {
            1: "🔵 Basic",
            2: "🟢 Intermediate",
            3: "🟠 Advanced",
            4: "🔴 Full Access"
        }
        return level_emojis.get(self.admin_level, str(self.admin_level))
    
    def get_subordinate_count(self):
        """Return the number of staff members reporting to this staff member"""
        return self.subordinates.count()
    
    def get_full_department_hierarchy(self):
        """Return department and position in hierarchy format"""
        if self.supervisor:
            return f"{self.department} → {self.position} (Reports to: {self.supervisor.position})"
        return f"{self.department} → {self.position}"
    
    def clean(self):
        """Validate staff data"""
        # Ensure hire date is not in the future
        if self.hire_date and self.hire_date > timezone.now().date():
            raise ValidationError({'hire_date': 'Hire date cannot be in the future.'})
        
        # Prevent circular supervisor relationships
        if self.supervisor and self.supervisor.id == self.id:
            raise ValidationError({'supervisor': 'A staff member cannot be their own supervisor.'})
        
        # Check for deeper circular dependencies
        if self.supervisor:
            supervisor = self.supervisor
            seen_supervisors = {self.id}
            while supervisor:
                if supervisor.id in seen_supervisors:
                    raise ValidationError({'supervisor': 'Circular supervision hierarchy detected.'})
                seen_supervisors.add(supervisor.id)
                supervisor = supervisor.supervisor
        
        # Ensure profile type matches
        if self.profile.user_type != 'staff':
            self.profile.user_type = 'staff'
            self.profile.save()
            logger.info(f"Updated profile type to 'staff' for user {self.profile.user.username}")
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation and proper profile type"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Staff Member"
        verbose_name_plural = "Staff Members"
        ordering = ['department', 'position']
        indexes = [
            models.Index(fields=['department']),
            models.Index(fields=['hire_date']),
            models.Index(fields=['admin_level']),
        ]


class Alumni(models.Model):
    """
    Alumni-specific information model.
    Contains information about former students of the university.
    """
    # Link to Student model (not Profile directly)
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name='alumni'  # Allows reverse lookup: student.alumni
    )

    # Graduation year and degree
    graduation_year = models.PositiveIntegerField(db_index=True)
    degree = models.CharField(max_length=100, blank=True, db_index=True)

    # Current employment information
    current_employer = models.CharField(max_length=255, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    
    # Contact information for alumni
    personal_email = models.EmailField(blank=True)
    
    # Alumni engagement
    is_donor = models.BooleanField(default=False)
    last_contact_date = models.DateField(null=True, blank=True)
    engagement_level = models.PositiveSmallIntegerField(
        choices=[(1, 'Low'), (2, 'Medium'), (3, 'High')],
        default=1
    )

    def __str__(self):
        """String representation of alumni"""
        name = self.student.profile.user.get_full_name() or self.student.profile.user.username
        return f"Alumnus: {name} ({self.graduation_year})"
    
    def years_since_graduation(self):
        """Calculate years since graduation"""
        current_year = timezone.now().year
        return current_year - self.graduation_year
    
    def update_student_status(self):
        """Ensure the linked student has 'graduated' status"""
        if self.student.academic_status != 'graduated':
            self.student.academic_status = 'graduated'
            self.student.save(update_fields=['academic_status'])
            logger.info(f"Updated student status to 'graduated' for {self.student}")
    
    def get_full_alumni_details(self):
        """Return comprehensive alumni information"""
        return {
            'name': self.student.profile.user.get_full_name() or self.student.profile.user.username,
            'graduation_year': self.graduation_year,
            'degree': self.degree,
            'years_since_graduation': self.years_since_graduation(),
            'employer': self.current_employer or 'Not provided',
            'position': self.job_title or 'Not provided',
            'contact': self.personal_email or self.student.profile.user.email,
            'engagement': dict(self._meta.get_field('engagement_level').choices).get(self.engagement_level),
            'is_donor': 'Yes' if self.is_donor else 'No'
        }
    
    def clean(self):
        """Validate alumni data"""
        # Ensure graduation year is not in the future
        current_year = timezone.now().year
        if self.graduation_year > current_year:
            raise ValidationError({'graduation_year': 'Graduation year cannot be in the future.'})
        
        # Check graduation year against university founding year
        founding_year = 1950  # Example founding year
        if self.graduation_year < founding_year:
            raise ValidationError({'graduation_year': f'Graduation year cannot be before university founding in {founding_year}.'})
        
        # Check graduation year against student enrollment
        if self.student.enrollment_date and self.graduation_year < self.student.enrollment_date.year:
            raise ValidationError({'graduation_year': 'Graduation year cannot be before enrollment year.'})
        
        # If last contact date is provided, ensure it's not in the future
        if self.last_contact_date and self.last_contact_date > timezone.now().date():
            raise ValidationError({'last_contact_date': 'Last contact date cannot be in the future.'})
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation and update student status"""
        self.full_clean()
        # Update student status to graduated
        self.update_student_status()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Alumnus"
        verbose_name_plural = "Alumni"
        ordering = ['graduation_year', 'student__profile__user__username']
        indexes = [
            models.Index(fields=['graduation_year']),
            models.Index(fields=['degree']),
            models.Index(fields=['is_donor']),
        ]


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to automatically create a Profile when a new User is created.
    This ensures every User has an associated Profile.
    """
    if created:
        Profile.objects.create(user=instance)
        logger.info(f"Created new profile for user {instance.username}")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal handler to save the Profile whenever the associated User is saved.
    Ensures Profile changes are persisted when User is updated.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()