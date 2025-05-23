from django.test import TestCase
from scheduling_data.models import Group
from scheduling_algorithm.data_parser.group_data import GroupData

class GroupDataTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Setup data test
        # cls.group = Group.objects.create(name="Test Group")
        cls.group = Group.objects.create(
            name="Test Group",
            module_id=1,  # Ganti dengan ID modul yang sesuai
        )
    
    def test_get_group_cache(self):
        # Panggil pertama kali (harus query database)
        group = GroupData.get_group(self.group.id)
        self.assertEqual(group.name, "Test Group")
        
        # Panggil kedua kali (harus dari cache)
        with self.assertNumQueries(0):
            cached_group = GroupData.get_group(self.group.id)