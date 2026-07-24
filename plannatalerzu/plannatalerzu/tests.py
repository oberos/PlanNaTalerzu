from django.test import TestCase
from django.urls import reverse


class NavigationLayoutTests(TestCase):
    def test_homepage_contains_main_navigation(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Planowanie")
        self.assertContains(response, "Przepisy")
        self.assertContains(response, "Lista zakupów")
