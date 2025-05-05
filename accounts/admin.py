


from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Avg, Q, F
from .models import Address, Profile, Student, FacultyMember, StaffMember, Alumni
import logging

logger = logging.getLogger(__name__)

# Common admin functionality
class NexGenBaseAdmin(admin.ModelAdmin):
    """
    Base admin class with common functionality for all NexGen admin interfaces.
    Provides consistent save handling and logging.
    """
    save_on_top = True  # Add save buttons at the top of admin pages
    
    def save_model(self, request, obj, form, change):
        """Log and track model changes"""
        action = 'Updated' if change else 'Created'
        logger.info(f"{action} {obj._meta.verbose_name}: {obj} by {request.user}")
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """Override to add select_related for better performance"""
        qs = super().get_queryset(request)
        if hasattr(self.model, 'profile'):
            qs = qs.select_related('profile', 'profile__user')
        return qs


# Address Admin
@admin.register(Address)
class AddressAdmin(NexGenBaseAdmin):
    list_display = ('street', 'city', 'region', 'country', 'profile_count')
    search_fields = ('street', 'city', 'region', 'country')
    list_filter = ('country', 'region', 'city')
    ordering = ('country', 'region', 'city', 'street')
    
    def get_queryset(self, request):
        """Optimize query with annotations"""
        return super().get_queryset(request).annotate(
            profile_count=Count('profile', distinct=True)
        )
    
    def profile_count(self, obj):
        """Display number of profiles using this address"""
        url = reverse('admin:accounts_profile_changelist') + f'?address__id__exact={obj.id}'
        return format_html('<a href="{}">{} profiles</a>', url, obj.profile_count)
    profile_count.admin_order_field = 'profile_count'
    profile_count.short_description = _('Profiles')


# Dynamic Inlines for Profile Admin
class StudentInline(admin.StackedInline):
    model = Student
    can_delete = False
    verbose_name_plural = _('Student Information')
    classes = ('collapse',)
    
class FacultyMemberInline(admin.StackedInline):
    model = FacultyMember
    can_delete = False
    verbose_name_plural = _('Faculty Information')
    classes = ('collapse',)
    
class StaffMemberInline(admin.StackedInline):
    model = StaffMember
    can_delete = False
    verbose_name_plural = _('Staff Information')
    classes = ('collapse',)


# Profile Admin
@admin.register(Profile)
class ProfileAdmin(NexGenBaseAdmin):
    list_display = ('user', 'user_type', 'phone_number', 'display_address', 'is_active', 'get_age', 'date_joined')
    list_filter = ('user_type', 'is_active', 'date_joined')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'phone_number')
    raw_id_fields = ('user', 'address')
    readonly_fields = ('date_joined', 'last_updated', 'get_age')
    list_per_page = 20  # Control pagination for better performance
    
    fieldsets = (
        (_('User Information'), {
            'fields': ('user', 'user_type', 'is_active')
        }),
        (_('Personal Details'), {
            'fields': ('date_of_birth', 'get_age', 'bio', 'profile_picture')
        }),
        (_('Contact Information'), {
            'fields': ('phone_number', 'emergency_contact', 'address')
        }),
        (_('System Fields'), {
            'classes': ('collapse',),
            'fields': ('date_joined', 'last_updated')
        }),
    )
    
    actions = ['mark_as_active', 'mark_as_inactive']
    
    def get_inlines(self, request, obj=None):
        """Dynamically add role-specific inlines based on user_type"""
        if not obj:
            return []
        
        inlines = []
        if obj.user_type == 'student':
            inlines.append(StudentInline)
        elif obj.user_type == 'faculty':
            inlines.append(FacultyMemberInline)
        elif obj.user_type == 'staff':
            inlines.append(StaffMemberInline)
        return inlines

    def display_address(self, obj):
        """Create a clickable link to the address detail view"""
        if obj.address:
            url = reverse('admin:accounts_address_change', args=[obj.address.id])
            return format_html('<a href="{}">{}</a>', url, obj.address)
        return "-"
    display_address.short_description = _('Address')
    
    def get_age(self, obj):
        """Display user age based on date of birth"""
        age = obj.get_age() if hasattr(obj, 'get_age') else None
        return age if age is not None else '-'
    get_age.short_description = _('Age')
    
    def mark_as_active(self, request, queryset):
        """Admin action to activate selected profiles"""
        updated = queryset.update(is_active=True)
        self.message_user(request, _(f"{updated} profiles marked as active."))
    mark_as_active.short_description = _("Mark selected profiles as active")
    
    def mark_as_inactive(self, request, queryset):
        """Admin action to deactivate selected profiles"""
        updated = queryset.update(is_active=False)
        self.message_user(request, _(f"{updated} profiles marked as inactive."))
    mark_as_inactive.short_description = _("Mark selected profiles as inactive")


# Student Admin
@admin.register(Student)
class StudentAdmin(NexGenBaseAdmin):
    list_display = ('student_id', 'get_full_name', 'major', 'academic_status', 'enrollment_date', 'gpa', 'get_enrollment_duration')
    list_filter = ('academic_status', 'enrollment_date', 'major')
    search_fields = ('student_id', 'profile__user__username', 'profile__user__first_name', 'profile__user__last_name', 'major')
    raw_id_fields = ('profile',)
    date_hierarchy = 'enrollment_date'
    readonly_fields = ('get_enrollment_duration', 'get_expected_time_to_graduation', 'is_on_track')
    
    fieldsets = (
        (_('Student Information'), {
            'fields': ('profile', 'student_id', 'major')
        }),
        (_('Academic Status'), {
            'fields': ('academic_status', 'gpa', 'credits_completed')
        }),
        (_('Enrollment'), {
            'fields': ('enrollment_date', 'expected_graduation', 'get_enrollment_duration', 'get_expected_time_to_graduation')
        }),
        (_('Performance'), {
            'fields': ('is_on_track',),
            'classes': ('collapse',),
        }),
    )
    
    actions = ['mark_as_graduated', 'mark_as_on_leave', 'mark_as_active']
    
    def get_full_name(self, obj):
        """Display the student's full name, falling back to username"""
        return obj.profile.user.get_full_name() or obj.profile.user.username
    get_full_name.short_description = _('Name')
    get_full_name.admin_order_field = 'profile__user__last_name'
    
    def get_enrollment_duration(self, obj):
        """Display how long the student has been enrolled"""
        if hasattr(obj, 'get_enrollment_duration'):
            return obj.get_enrollment_duration()
        return "-"
    get_enrollment_duration.short_description = _('Enrollment Duration')
    
    def get_expected_time_to_graduation(self, obj):
        """Display time remaining until expected graduation"""
        if hasattr(obj, 'get_expected_time_to_graduation'):
            return obj.get_expected_time_to_graduation()
        return "-"
    get_expected_time_to_graduation.short_description = _('Time to Graduation')
    
    def mark_as_graduated(self, request, queryset):
        """Admin action to mark selected students as graduated"""
        updated = queryset.update(academic_status='graduated')
        self.message_user(request, _(f"{updated} student(s) marked as graduated."))
    mark_as_graduated.short_description = _("Mark selected students as graduated")
    
    def mark_as_on_leave(self, request, queryset):
        """Admin action to mark selected students as on leave"""
        updated = queryset.update(academic_status='on_leave')
        self.message_user(request, _(f"{updated} student(s) marked as on leave."))
    mark_as_on_leave.short_description = _("Mark selected students as on leave")
    
    def mark_as_active(self, request, queryset):
        """Admin action to mark selected students as active"""
        updated = queryset.update(academic_status='active')
        self.message_user(request, _(f"{updated} student(s) marked as active."))
    mark_as_active.short_description = _("Mark selected students as active")


# Faculty Member Admin
@admin.register(FacultyMember)
class FacultyMemberAdmin(NexGenBaseAdmin):
    list_display = ('faculty_id', 'get_full_name', 'department', 'position', 'hire_date', 'get_employment_duration', 'is_tenured')
    list_filter = ('department', 'position', 'hire_date')
    search_fields = ('faculty_id', 'profile__user__username', 'profile__user__first_name', 'profile__user__last_name', 'department')
    raw_id_fields = ('profile',)
    date_hierarchy = 'hire_date'
    readonly_fields = ('get_employment_duration', 'is_tenured')
    
    fieldsets = (
        (_('Faculty Information'), {
            'fields': ('profile', 'faculty_id', 'position', 'department')
        }),
        (_('Employment'), {
            'fields': ('hire_date', 'get_employment_duration', 'is_tenured')
        }),
        (_('Academic Background'), {
            'fields': ('highest_degree', 'alma_mater', 'specialization', 'research_interests')
        }),
        (_('Office Information'), {
            'fields': ('office_location', 'office_hours')
        }),
    )
    
    def get_full_name(self, obj):
        """Display the faculty member's full name, falling back to username"""
        return obj.profile.user.get_full_name() or obj.profile.user.username
    get_full_name.short_description = _('Name')
    get_full_name.admin_order_field = 'profile__user__last_name'
    
    def get_employment_duration(self, obj):
        """Display how long the faculty member has been employed"""
        if hasattr(obj, 'get_employment_duration'):
            return obj.get_employment_duration()
        return "-"
    get_employment_duration.short_description = _('Employment Duration')
    
    def is_tenured(self, obj):
        """Display whether the faculty member is tenured"""
        if hasattr(obj, 'is_tenured') and callable(obj.is_tenured):
            return "✓" if obj.is_tenured() else "✗"
        return "-"
    is_tenured.short_description = _('Tenured')
    is_tenured.boolean = True


# Staff Member Admin
@admin.register(StaffMember)
class StaffMemberAdmin(NexGenBaseAdmin):
    list_display = ('staff_id', 'get_full_name', 'department', 'position', 'get_admin_level', 'hire_date', 'get_employment_duration', 'subordinate_count')
    list_filter = ('department', 'admin_level', 'hire_date')
    search_fields = ('staff_id', 'profile__user__username', 'profile__user__first_name', 'profile__user__last_name', 'department', 'position')
    raw_id_fields = ('profile', 'supervisor')
    date_hierarchy = 'hire_date'
    readonly_fields = ('get_employment_duration', 'subordinate_count', 'get_full_department_hierarchy')
    
    fieldsets = (
        (_('Staff Information'), {
            'fields': ('profile', 'staff_id', 'department', 'position')
        }),
        (_('Employment'), {
            'fields': ('hire_date', 'get_employment_duration')
        }),
        (_('Organizational Structure'), {
            'fields': ('supervisor', 'get_full_department_hierarchy', 'subordinate_count')
        }),
        (_('Responsibilities & Access'), {
            'fields': ('responsibilities', 'admin_level')
        }),
    )
    
    def get_queryset(self, request):
        """Optimize query with annotations"""
        return super().get_queryset(request).select_related(
            'supervisor'
        ).annotate(
            subordinate_count=Count('subordinates', distinct=True)
        )
    
    def get_full_name(self, obj):
        """Display the staff member's full name, falling back to username"""
        return obj.profile.user.get_full_name() or obj.profile.user.username
    get_full_name.short_description = _('Name')
    get_full_name.admin_order_field = 'profile__user__last_name'
    
    def get_employment_duration(self, obj):
        """Display how long the staff member has been employed"""
        if hasattr(obj, 'get_employment_duration'):
            return obj.get_employment_duration()
        return "-"
    get_employment_duration.short_description = _('Employment Duration')
    
    def get_admin_level(self, obj):
        """Format admin level with visual indicator"""
        if hasattr(obj, 'get_admin_level_display_emoji'):
            return format_html('{}', obj.get_admin_level_display_emoji())
        return obj.get_admin_level_display()
    get_admin_level.short_description = _('Access Level')
    get_admin_level.admin_order_field = 'admin_level'
    
    def subordinate_count(self, obj):
        """Display number of subordinates with link to filtered view"""
        if obj.subordinate_count > 0:
            url = reverse('admin:accounts_staffmember_changelist') + f'?supervisor__id__exact={obj.id}'
            return format_html('<a href="{}">{} staff</a>', url, obj.subordinate_count)
        return "0"
    subordinate_count.short_description = _('Subordinates')
    subordinate_count.admin_order_field = 'subordinate_count'


# Alumni Admin
@admin.register(Alumni)
class AlumniAdmin(NexGenBaseAdmin):
    list_display = ('get_full_name', 'graduation_year', 'degree', 'current_employer', 'job_title', 'years_since_graduation', 'engagement_indicator')
    list_filter = ('graduation_year', 'degree', 'is_donor', 'engagement_level')
    search_fields = ('student__profile__user__first_name', 'student__profile__user__last_name', 'degree', 'current_employer', 'job_title')
    raw_id_fields = ('student',)
    date_hierarchy = 'last_contact_date'
    
    fieldsets = (
        (_('Alumni Information'), {
            'fields': ('student', 'graduation_year', 'degree')
        }),
        (_('Employment Information'), {
            'fields': ('current_employer', 'job_title')
        }),
        (_('Contact Information'), {
            'fields': ('personal_email', 'last_contact_date')
        }),
        (_('Engagement'), {
            'fields': ('engagement_level', 'is_donor')
        }),
    )
    
    actions = ['mark_as_donor', 'update_engagement_level']
    
    def get_queryset(self, request):
        """Optimize query with select_related"""
        return super().get_queryset(request).select_related(
            'student', 
            'student__profile', 
            'student__profile__user'
        )
    
    def get_full_name(self, obj):
        """Display the alumnus's full name, falling back to username"""
        return obj.student.profile.user.get_full_name() or obj.student.profile.user.username
    get_full_name.short_description = _('Name')
    get_full_name.admin_order_field = 'student__profile__user__last_name'
    
    def years_since_graduation(self, obj):
        """Display years since graduation"""
        if hasattr(obj, 'years_since_graduation'):
            years = obj.years_since_graduation()
            return f"{years} year{'s' if years != 1 else ''}"
        return "-"
    years_since_graduation.short_description = _('Years Since Graduation')
    
    def engagement_indicator(self, obj):
        """Visual indicator of engagement level"""
        engagement_icons = {
            1: '⚪ Low',
            2: '🔵 Medium',
            3: '🟢 High'
        }
        donor_indicator = " 💰" if obj.is_donor else ""
        return format_html('{} {}', 
                          engagement_icons.get(obj.engagement_level, str(obj.engagement_level)),
                          donor_indicator)
    engagement_indicator.short_description = _('Engagement')
    
    def mark_as_donor(self, request, queryset):
        """Admin action to mark selected alumni as donors"""
        updated = queryset.update(is_donor=True)
        self.message_user(request, _(f"{updated} alumni marked as donors."))
    mark_as_donor.short_description = _("Mark selected alumni as donors")
    
    def update_engagement_level(self, request, queryset):
        """Admin action to increase engagement level of selected alumni"""
        # Only update records that aren't already at max level
        updated = queryset.filter(engagement_level__lt=3).update(engagement_level=F('engagement_level') + 1)
        self.message_user(request, _(f"Increased engagement level for {updated} alumni."))
    update_engagement_level.short_description = _("Increase engagement level")