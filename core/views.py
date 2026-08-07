from django.shortcuts import render
from django.http import request
from core.models import Category, Area, Offer, Business
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
today = timezone.now().date()
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import JsonResponse

# Create your views here.
def home(self):
	categories = Category.objects.order_by("name")[:6]
	offer_types = Offer.OFFER_TYPES
	areas = Area.objects.order_by("name")
	top_offers = Offer.objects.filter(is_active=True, expires_at__gte=timezone.now().date()).select_related("business").order_by("-id")[:3]
	featured_businesses = Business.objects.filter(featured=True).select_related("area")
	context = {
		"categories": categories,
		"offer_types": offer_types,
		"areas": areas,
		"top_offers": top_offers,
		"featured_businesses": featured_businesses
	}
	return render(request, 'core/home.html', context)



def business_list(request):
	businesses = Business.objects.select_related("category", "area").prefetch_related("offers")

	keyword = request.GET.get("q")
	category = request.GET.get("category")
	area = request.GET.get("area")
	offer = request.GET.get("offer")
	featured = request.GET.get("featured")

	if keyword:
	    businesses = businesses.filter(Q(name__icontains=keyword) | Q(description__icontains=keyword) | Q(search_keywords__icontains=keyword))

	if category:
	    businesses = businesses.filter(category__slug=category)

	if area:
	    businesses = businesses.filter(area__slug=area)

	if featured:
		businesses = businesses.filter(featured=True)

	if offer:

	    if offer == "ending_soon":

	        today = timezone.now().date()

	        businesses = businesses.filter(
	            offers__expires_at__gte=today,
	            offers__expires_at__lte=today + timedelta(days=7),
	            offers__is_active=True,
	        )

	    else:

	        businesses = businesses.filter(
	            offers__offer_type=offer,
	            offers__is_active=True,
	        )

	businesses = businesses.distinct()

	context = {
	    "businesses": businesses,
	    "page_title": "Businesses",

	    "categories": Category.objects.order_by("name"),
	    "areas": Area.objects.order_by("name"),
	    "offer_types": Offer.OFFER_TYPES,

	    # preserve selected values
	    "keyword": keyword,
	    "selected_category": category,
	    "selected_area": area,
	    "selected_offer": offer,
	}

	return render(request, "core/businesses_list.html", context)



def business_modal(request, pk):
    business = get_object_or_404(Business, pk=pk)
    latest_offers = business.offers.filter(is_active=True, expires_at__gte=timezone.now().date()).order_by("-id")[:3]

    html = render_to_string(
        "includes/business_modal.html",
        {"business": business, "latest_offers": latest_offers},
        request=request
    )

    return JsonResponse({"html": html})