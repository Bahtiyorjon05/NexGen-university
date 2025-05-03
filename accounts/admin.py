from django.contrib import admin
from .models import Address, Profile, Student, FacultyMember, StaffMember, Alumni
from django.utils.html import format_html
from django.urls import reverse

# Address Admin
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('street', 'city', 'region', 'country')
    search_fields = ('street', 'city', 'region', 'country')
    list_filter = ('country', 'region', 'city')
    ordering = ('country', 'region', 'city', 'street')


# Profile Admin
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'phone_number', 'display_address', 'is_active')
    list_filter = ('user_type', 'is_active')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'phone_number')
    raw_id_fields = ('user', 'address')
    readonly_fields = ('date_joined', 'last_updated')
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'user_type', 'is_active')
        }),
        ('Personal Details', {
            'fields': ('date_of_birth', 'bio', 'profile_picture')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'emergency_contact', 'address')
        }),
        ('System Fields', {
            'classes': ('collapse',),
            'fields': ('date_joined', 'last_updated')
        }),
    )

    def display_address(self, obj):
        if obj.address:
            url = reverse('admin:accounts_address_change', args=[obj.address.id])
            return format_html('<a href="{}">{}</a>', url, obj.address)
        return "-"
    display_address.short_description = 'Address'


# Student Admin
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'get_full_name', 'major', 'academic_status', 'enrollment_date', 'gpa')
    list_filter = ('academic_status', 'enrollment_date')
    search_fields = ('student_id', 'profile__user__username', 'profile__user__first_name', 'profile__user__last_name', 'major')
    raw_id_fields = ('profile',)
    date_hierarchy = 'enrollment_date'

    def get_full_name(self, obj):
        return obj.profile.user.get_full_name() or obj.profile.user.username
    get_full_name.short_description = 'Name'
    get_full_name.admin_order_field = 'profile__user__last_name'


# Faculty Member Admin
@admin.register(FacultyMember)
class FacultyMemberAdmin(admin.ModelAdmin):
    list_display = ('faculty_id', 'get_full_name', 'department', 'position', 'hire_date')
    list_filter = ('department', 'position', 'hire_date')
    search_fields = ('faculty_id', 'profile__user__username', 'profile__user__first_name', 'profile__user__last_name', 'department')
    raw_id_fields = ('profile',)
    date_hierarchy = 'hire_date'
    
    def get_full_name(self, obj):
        return obj.profile.user.get_full_name() or obj.profile.user.username
    get_full_name.short_description = 'Name'
    get_full_name.admin_order_field = 'profile__user__last_name'


# Staff Member Admin
@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ('staff_id', 'get_full_name', 'department', 'position', 'admin_level', 'hire_date')
    list_filter = ('department', 'admin_level', 'hire_date')
    search_fields = ('staff_id', 'profile__user__username', 'profile__user__first_name', 'profile__user__last_name', 'department', 'position')
    raw_id_fields = ('profile', 'supervisor')
    date_hierarchy = 'hire_date'
    
    def get_full_name(self, obj):
        return obj.profile.user.get_full_name() or obj.profile.user.username
    get_full_name.short_description = 'Name'
    get_full_name.admin_order_field = 'profile__user__last_name'


# Alumni Admin
@admin.register(Alumni)
class AlumniAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'graduation_year', 'degree', 'current_employer', 'job_title')
    list_filter = ('graduation_year', 'degree')
    search_fields = ('student__profile__user__first_name', 'student__profile__user__last_name', 'degree', 'current_employer', 'job_title')
    raw_id_fields = ('student',)
    
    def get_full_name(self, obj):
        return obj.student.profile.user.get_full_name() or obj.student.profile.user.username
    get_full_name.short_description = 'Name'
    get_full_name.admin_order_field = 'student__profile__user__last_name'