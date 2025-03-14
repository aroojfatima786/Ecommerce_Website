from django.contrib import admin
from .models import Product, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Display ID and Name in admin panel
    search_fields = ('name',)  # Add search functionality

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'category')  # Display fields
    list_filter = ('category',)  # Filter products by category
    search_fields = ('name', 'category__name')  # Search by name or category

# Registering models
# admin.site.register(Product, ProductAdmin)  # Now using @admin.register decorator
# admin.site.register(Category, CategoryAdmin)  # Now using @admin.register decorator
