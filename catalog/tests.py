"""
Tests for the Trade Material Catalog app.
Run with: python manage.py test catalog
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.db.models.deletion import ProtectedError

from .models import Category, Tag, Product


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_category(name="Electrical"):
    return Category.objects.create(name=name)

def make_tag(name="jobsite-ready"):
    return Tag.objects.create(name=name)

def make_product(name="MC Cable", category=None, status=Product.STATUS_AVAILABLE,
                 is_active=True, description="Standard cable"):
    if category is None:
        category, _ = Category.objects.get_or_create(name="Default")
    return Product.objects.create(
        name=name, category=category, status=status,
        is_active=is_active, description=description, price="9.99",
    )


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class ModelTests(TestCase):

    def test_slug_auto_generated(self):
        self.assertEqual(make_category("Electrical Supplies").slug, "electrical-supplies")

    def test_slug_not_overwritten_on_resave(self):
        cat = make_category("Fasteners")
        cat.description = "Updated"
        cat.save()
        self.assertEqual(cat.slug, "fasteners")

    def test_cannot_delete_category_with_products(self):
        cat = make_category()
        make_product(category=cat)
        with self.assertRaises(ProtectedError):
            cat.delete()

    def test_product_defaults(self):
        p = make_product()
        self.assertEqual(p.status, Product.STATUS_AVAILABLE)
        self.assertTrue(p.is_active)
        self.assertFalse(p.is_prefab_item)


# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------

class FilterTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse("catalog:product_list")
        self.cat = make_category()

    def get(self, params=None):
        return self.client.get(self.url, params or {})

    def test_inactive_products_hidden(self):
        make_product("Hidden", category=self.cat, is_active=False)
        self.assertNotContains(self.get(), "Hidden")

    def test_search_matches_name_and_description(self):
        make_product("MC Cable", category=self.cat, description="armored")
        make_product("EMT Conduit", category=self.cat, description="steel tube")
        r = self.get({"query": "armored"})
        self.assertContains(r, "MC Cable")
        self.assertNotContains(r, "EMT Conduit")

    def test_category_filter(self):
        other = make_category("Fasteners")
        make_product("MC Cable", category=self.cat)
        make_product("Hex Bolt", category=other)
        r = self.get({"category": self.cat.pk})
        self.assertContains(r, "MC Cable")
        self.assertNotContains(r, "Hex Bolt")

    def test_status_filter(self):
        make_product("Available Item", category=self.cat, status=Product.STATUS_AVAILABLE)
        make_product("Backordered Item", category=self.cat, status=Product.STATUS_BACKORDERED)
        r = self.get({"status": "available"})
        self.assertContains(r, "Available Item")
        self.assertNotContains(r, "Backordered Item")

    def test_tag_filter_and_semantics(self):
        """Products must carry ALL selected tags — not just any one of them."""
        tag_a = make_tag("jobsite-ready")
        tag_b = make_tag("reorder-needed")
        both = make_product("Wire Nuts", category=self.cat)
        both.tags.add(tag_a, tag_b)
        one_only = make_product("EMT Conduit", category=self.cat)
        one_only.tags.add(tag_a)

        r = self.get({"tags": [tag_a.pk, tag_b.pk]})
        self.assertContains(r, "Wire Nuts")
        self.assertNotContains(r, "EMT Conduit")

    def test_combined_filters(self):
        other_cat = make_category("Fasteners")
        make_product("MC Cable", category=self.cat, status=Product.STATUS_AVAILABLE)
        make_product("Hex Bolt", category=other_cat, status=Product.STATUS_AVAILABLE)
        r = self.get({"category": self.cat.pk, "status": "available"})
        self.assertContains(r, "MC Cable")
        self.assertNotContains(r, "Hex Bolt")


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------

class PaginationTests(TestCase):

    def setUp(self):
        cat = make_category()
        for i in range(12):
            make_product(f"Product {i:02d}", category=cat)
        self.url = reverse("catalog:product_list")

    def test_first_page_has_nine_results(self):
        self.assertEqual(len(self.client.get(self.url).context["products"]), 9)

    def test_second_page_has_remainder(self):
        self.assertEqual(len(self.client.get(self.url, {"page": 2}).context["products"]), 3)

    def test_invalid_page_returns_404(self):
        self.assertEqual(self.client.get(self.url, {"page": 999}).status_code, 404)
