from django.test import TestCase
from courses.models import Department
from django.utils import timezone

class DepartmentModelTest(TestCase):
    def test_department_creation(self):
        department = Department.objects.create(
            name="Computer Science",
            description="Department of Computer Science",
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
        self.assertEqual(department.name, "Computer Science")
        self.assertEqual(department.description, "Department of Computer Science")
        self.assertIsInstance(department.created_at, timezone.datetime)
        self.assertIsInstance(department.updated_at, timezone.datetime)
        self.assertTrue(department.created_at <= department.updated_at)
        self.assertEqual(str(department), "Computer Science")

    def test_unique_name(self):
        Department.objects.create(
            name="Physics",
            description="Department of Physics",
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
        with self.assertRaises(Exception):
            Department.objects.create(
                name="Physics",
                description="Duplicate Department",
                created_at=timezone.now(),
                updated_at=timezone.now()
            )

    def test_string_representation(self):
        department = Department(name="Mathematics")
        self.assertEqual(str(department), "Mathematics")
        department.name = "Chemistry"
        self.assertEqual(str(department), "Chemistry")
        department.save()
        self.assertEqual(str(department), "Chemistry")
        department.delete()
        with self.assertRaises(Department.DoesNotExist):
            Department.objects.get(name="Chemistry")
