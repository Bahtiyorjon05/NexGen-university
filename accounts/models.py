from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# NexGen University Accounts

class Address(models.Model):
    """
    Physical address information that can be reused accross the system.
    This is a separate model to avoic duplicating address fields in multiple models.
    """
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True, null=True)    
    country = models.CharField(max_length=100, default='Uzbekistan')

    def __str__(self):
        return f"{self.street}, {self.city}, {self.region}, {self.country}"
    
    class Meta: 
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
        ordering = ['city', 'street']

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
        default='other'
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
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)  # Set once on creation
    last_updated = models.DateTimeField(auto_now=True)     # Updated on each save
    
    def __str__(self):
        """String representation of profile - shows username and type"""
        return f"{self.user.username} ({self.get_user_type_display()})"
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ['user__username']  # Order profiles by username

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
    major = models.CharField(max_length=100, blank=True)

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
        help_text="Grade Point Average (0.00 - 4.00)"
    )
    credits_completed = models.PositiveIntegerField(default=0)

    def __str__(self):
        """String representation of student"""
        return f"Student: {self.profile.user.get_full_name() or self.profile.user.username}"
    
    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        ordering = ['student_id']  # Order students by student ID

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
        choices=POSITION_CHOICES
    )

    # Employment information
    hire_date = models.DateField()
    department = models.CharField(max_length=100)
    
    # Academic qualifications
    highest_degree = models.CharField(max_length=100, blank=True)
    alma_mater = models.CharField(max_length=255, blank=True, null=True)

    # Office information
    office_location = models.CharField(max_length=100, blank=True)
    office_hours = models.CharField(max_length=100, blank=True)

    # Areas of expertise and research
    specialization = models.CharField(max_length=255, blank=True)
    research_interests = models.TextField(blank=True)

    def __str__(self):
        """String representation of faculty member"""
        name = self.profile.user.get_full_name() or self.profile.user.username
        return f"{self.get_position_display()}: {name}"
    
    class Meta:
        verbose_name = "Faculty Member"
        verbose_name_plural = "Faculty Members"
        ordering = ['faculty_id']  # Order faculty members by faculty ID

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
        help_text="Unique staff identification number"
    )
    
    # Employment information
    department = models.CharField(max_length=100)
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
    
    class Meta:
        verbose_name = "Staff Member"
        verbose_name_plural = "Staff Members"
        ordering = ['department', 'position']

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
    graduation_year = models.PositiveIntegerField()
    degree = models.CharField(max_length=100, blank=True)

    # Current employment information
    current_employer = models.CharField(max_length=255, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    
    # Contact information for alumni
    personal_email = models.EmailField(blank=True)

    def __str__(self):
        """
        String representation of alumni.
        Accesses the user's full name via the related student and profile.
        """
        name = self.student.profile.user.get_full_name() or self.student.profile.user.username
        return f"Alumnus: {name} ({self.graduation_year})"

    class Meta:
        verbose_name = "Alumnus"
        verbose_name_plural = "Alumni"
        ordering = ['graduation_year', 'student__profile__user__username']

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to automatically create a Profile when a new User is created.
    This ensures every User has an associated Profile.
    """
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal handler to save the Profile whenever the associated User is saved.
    Ensures Profile changes are persisted when User is updated.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
    
