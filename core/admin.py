from django.contrib import admin
from core import models
from django.db.models import Count
from django.shortcuts import render
from django.urls import path

# Register your models here.
@admin.register(models.Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "area",
        "featured"
    )
    list_filter = (
        "featured",
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







@admin.register(models.SearchLog)
class SearchLogAdmin(admin.ModelAdmin):

    change_list_template = "admin/searchlog/change_list.html"

    list_display = (
        "query",
        "search_count",
        "area",
        "category",
        "searched_at",
        "ip_address",
    )

    list_filter = (
        "area",
        "category",
        "searched_at",
    )

    search_fields = (
        "query",
        "ip_address",
    )

    ordering = (
        "-searched_at",
    )

    def get_queryset(self, request):

        queryset = super().get_queryset(request)

        return queryset.annotate(
            total_searches=Count("query")
        )

    @admin.display(
        ordering="total_searches",
        description="Searches"
    )

    def search_count(self, obj):
        return obj.total_searches


    def get_urls(self):

        urls = super().get_urls()

        custom_urls = [
            path(
                "analytics/",
                self.admin_site.admin_view(self.analytics_view),
                name="searchlog-analytics",
            ),
        ]

        return custom_urls + urls


    def analytics_view(self, request):

        searches = models.SearchLog.objects.all()

        area = request.GET.get("area")
        category = request.GET.get("category")

        if area:
            searches = searches.filter(
                area_id=area
            )

        if category:
            searches = searches.filter(
                category_id=category
            )

        searches = (
            searches
            .values(
                "query",
                "area__name",
                "category__name",
            )
            .annotate(
                total_searches=Count("id")
            )
            .order_by("-total_searches")
        )

        context = {
            **self.admin_site.each_context(request),

            "title": "Search Analytics",

            "searches": searches,

            "areas": models.Area.objects.order_by("name"),

            "categories": models.Category.objects.order_by("name"),

            "selected_area": area,

            "selected_category": category,
        }

        return render(
            request,
            "admin/search_analytics.html",
            context
        )