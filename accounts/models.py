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