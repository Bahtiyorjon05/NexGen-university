from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Address, Profile, Student, FacultyMember, StaffMember, Alumni


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['date_joined']


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for the Address model."""

    class Meta:
        model = Address
        fields = ['id', 'street', 'city', 'region','postal_code', 'country']


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profiles with nested user information"""

    # Nested serializer for related objects
    user = UserSerializer(read_only=True)
    address = AddressSerializer(read_only=True)

    # Computed field
    age = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'id', 'user', 'user_type', 'date_of_birth', 'age',
            'bio', 'phone_number', 'emergency_contact',
            'address', 'profile_picture', 'is_active',
            'date_joined', 'last_updated'
        ]
        read_only_fields = ['date_joined', 'last_updated']

    def get_age(self, obj):
        """Get user's age based on date of birth."""
        return obj.get_age() if hasattr(obj, 'get_age') else None


class StudentSerializer(serializers.ModelSerializer):
    """Serializer for the Student model."""

    # Nested profile data
    profile = ProfileSerializer(read_only=True)

    # Computed fields
    enrollment_duration = serializers.SerializerMethodField()
    time_to_graduation = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id', 'profile', 'student_id', 'enrollment_date',
            'expected_graduation', 'major', 'academic_status',
            'gpa', 'credits_completed', 'enrollment_duration', 
            'time_to_graduation'
        ]

    def get_enrollment_duration(self, obj):
        """Calculate the duration of enrollment in years."""
        return obj.get_enrollment_duration() if hasattr(obj, 'get_enrollment_duration') else None

    def get_time_to_graduation(self, obj):
        """Calculate the time remaining until graduation in years."""
        return obj.get_expected_time_to_graduation() if hasattr(obj, 'get_expected_time_to_graduation') else None


class FacultyMemberSerializer(serializers.ModelSerializer):
    """Serializer for faculty member information."""

    # Nested profile data
    profile = ProfileSerializer(read_only=True)

    # Computed fields
    tenured = serializers.SerializerMethodField()
    employment_duration = serializers.SerializerMethodField()

    class Meta:
        model = FacultyMember
        fields = [
            'id', 'profile', 'faculty_id', 'position', 'department',
            'hire_date', 'highest_degree', 'alma_mater',
            'office_location', 'office_hours', 'specialization',
            'research_interests', 'employment_duration', 'tenured'
        ]

    def get_employment_duration(self, obj):
        """Get the duration of employment."""
        return obj.get_employment_duration() if hasattr(obj, 'get_employment_duration') else None
    
    def get_tenured(self, obj):
        """Check if faculty member is tenured."""
        return obj.is_tenured() if hasattr(obj, 'is_tenured') else None


class StaffMemberSerializer(serializers.ModelSerializer):
    """Serializer for admistrative staff member information."""

    # Nested profile data
    profile = ProfileSerializer(read_only=True)

    # Supervisor name
    supervisor_name = serializers.SerializerMethodField()

    # Computed fields
    employment_duration = serializers.SerializerMethodField()
    department_hierarchy = serializers.SerializerMethodField()
    admin_level_display = serializers.SerializerMethodField()

    class Meta:
        model = StaffMember
        fields = [
            'id', 'profile', 'staff_id', 'department', 'position',
            'hire_date', 'responsibilities', 'supervisor', 'supervisor_name',
            'admin_level', 'admin_level_display', 'employment_duration',
            'department_hierarchy'
        ]

    def get_supervisor_name(self, obj):
        """Get the name of the supervisor."""
        if obj.supervisor and obj.supervisor.profile and obj.supervisor.profile.user:
            user = obj.supervisor.profile.user
            return f"{user.first_name} {user.last_name}" if user.first_name else user.username
        return None
     
    def get_employment_duration(self, obj):
        """Get the duration of employment."""
        return obj.get_employment_duration() if hasattr(obj, 'get_employment_duration') else None
    
    def get_department_hierarchy(self, obj):
        """Get the department hierarchy information."""
        return obj.get_full_department_hierarchy() if hasattr(obj, 'get_full_department_hierarchy') else None
    
    def get_admin_level_display(self, obj):
        """Get the formatted admin level with emoji."""
        return obj.get_admin_level_display_emoji() if hasattr(obj, 'get_admin_level_display_emoji') else obj.get_admin_level_display()
    

class AlumniSerializer(serializers.ModelSerializer):
    """Serializer for alumni information."""

    # Nested student data
    student = StudentSerializer(read_only=True)

    # Computed fields
    years_since_graduation = serializers.SerializerMethodField()
    full_details = serializers.SerializerMethodField()

    class Meta:
        model = Alumni
        fields = [
            'id', 'student', 'graduation_year', 'degree',
            'current_employer', 'job_title', 'personal_email',
            'is_donor', 'last_contact_date', 'engagement_level',
            'years_since_graduation', 'full_details'
        ]

    def get_years_since_graduation(self, obj):
        """Get the number of years since graduation."""
        return obj.years_since_graduation() if hasattr(obj, 'years_since_graduation') else None
    
    def get_full_details(self, obj):
        """Get comprehensive alumni information."""
        return obj.get_full_alumni_details() if hasattr(obj, 'get_full_alumni_details') else None


# Simplified serializers for creating/updating records without nested data
class ProfileCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating profiles without nested objects."""
    
    class Meta:
        model = Profile
        fields = [
            'user_type', 'date_of_birth', 'bio', 'phone_number',
            'emergency_contact', 'profile_picture', 'is_active'
        ]


class StudentCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating student records without nested objects."""

    class Meta:
        model = Student
        fields = [
            'profile', 'student_id', 'enrollment_date',
            'expected_graduation', 'major', 'academic_status',
            'gpa', 'credits_completed'
        ]
        read_only_fields = ['profile']  # Only allow setting profile during creation


class FacultyMemberCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating faculty member records without nested objects."""

    class Meta:
        model = FacultyMember
        fields = [
            'profile', 'faculty_id', 'position', 'department',
            'hire_date', 'highest_degree', 'alma_mater',
            'office_location', 'office_hours', 'specialization',
            'research_interests'
        ]
        read_only_fields = ['profile']  # Only set via the API view, not directly


class StaffMemberCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating staff member records without nested objects."""

    class Meta:
        model = StaffMember
        fields = [
            'profile', 'staff_id', 'department', 'position',
            'hire_date', 'responsibilities', 'supervisor', 'admin_level'
        ]
        read_only_fields = ['profile']


class AlumniCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating alumni records without nested objects."""

    class Meta:
        model = Alumni
        fields = [
            'student', 'graduation_year', 'degree',
            'current_employer', 'job_title', 'personal_email',
            'is_donor', 'last_contact_date', 'engagement_level'
        ]
        read_only_fields = ['student'] # Only set via the API view, not directly


