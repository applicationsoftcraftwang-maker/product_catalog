from django.contrib import admin
from .models import Category, Tag, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "product_count", "created_at")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at",)

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "# Materials"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "product_count", "created_at")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at",)

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "# Materials"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "status", "is_prefab_item", "stock", "price", "is_active")
    list_filter = ("category", "status", "is_prefab_item", "is_active", "tags")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("tags",)
    actions = ["mark_available", "mark_backordered"]

    def mark_available(self, request, queryset):
        updated = queryset.update(status=Product.STATUS_AVAILABLE)
        self.message_user(request, f"{updated} item(s) marked as available.")
    mark_available.short_description = "Mark selected as Available"

    def mark_backordered(self, request, queryset):
        updated = queryset.update(status=Product.STATUS_BACKORDERED)
        self.message_user(request, f"{updated} item(s) marked as Backordered.")
    mark_backordered.short_description = "Mark selected as Backordered"

