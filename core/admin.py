from django.contrib import admin
from core import models

# Register your models here.
@admin.register(models.Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "area",
    )
    list_filter = (
        "category",
        "area",
    )
    search_fields = (
        "name",
        "description",
    )
    prepopulated_fields = {"slug": ("name",)}


@admin.register(models.Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "business",
        "is_active",
    )
    list_filter = (
        "is_active",
        "business__category",
        "business__area",
    )
    search_fields = (
        "title",
        "business__name",
    )


@admin.register(models.Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}