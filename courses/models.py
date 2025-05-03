from django.db import models

# NexGen University Courses

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        ordering = ['name']