from django.shortcuts import render
from django.http import request
from core.models import Category, Area, Offer, Business, SearchLog
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q, Count
today = timezone.now().date()
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.core.paginator import Paginator

# Create your views here.
def home(self):
	categories = Category.objects.order_by("name")[:6]
	offer_types = Offer.OFFER_TYPES
	areas = Area.objects.order_by("name")
	top_offers = Offer.objects.filter(is_active=True, expires_at__gte=timezone.now().date()).select_related("business").order_by("-id")[:3]
	featured_businesses = Business.objects.filter(featured=True).select_related("area")
	business_areas = Area.objects.annotate(business_count=Count("businesses")).filter(business_count__gt=1).order_by("-business_count")[:5]
	context = {
		"categories": categories,
		"offer_types": offer_types,
		"areas": areas,
		"top_offers": top_offers,
		"featured_businesses": featured_businesses,
		"business_areas": business_areas
	}
	return render(request, 'core/home.html', context)



def business_list(request):

    businesses = (
        Business.objects
        .select_related("category", "area")
        .prefetch_related("offers")
    )

    keyword = request.GET.get("q")
    search_submit = request.GET.get("search_submit")
    category = request.GET.get("category")
    area = request.GET.get("area")
    offer = request.GET.get("offer")
    featured = request.GET.get("featured")
    sort = request.GET.get("sort", "popular")

    # Sort
    if sort == "name":
    	businesses = businesses.order_by("name")
    else:
    	businesses = businesses.order_by("-featured", "-id")


    # --------------------------------
    # AREA
    # --------------------------------

    selected_area = None

    if area:
        selected_area = get_object_or_404(
            Area,
            slug=area
        )

        businesses = businesses.filter(
            area=selected_area
        )


    selected_category = None

    if category:
        selected_category = get_object_or_404(
            Category,
            slug=category
        )

    # --------------------------------
    # KEYWORD
    # --------------------------------

    if keyword:
        businesses = businesses.filter(Q(name__icontains=keyword) | Q(description__icontains=keyword) | Q(search_keywords__icontains=keyword))



    # --------------------------------
    # SEARCH LOG
    # --------------------------------

    if search_submit and keyword and keyword.strip():
        # print("CREATING SEARCH LOG:", keyword)

        SearchLog.objects.create(
            query=keyword.strip().lower(),
            area=selected_area,
            category=selected_category,
            ip_address=request.META.get("REMOTE_ADDR"),
        )
    # --------------------------------
    # FEATURED
    # --------------------------------

    if featured:
        businesses = businesses.filter(
            featured=True
        )


    # --------------------------------
    # OFFER
    # --------------------------------

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


    # Remove duplicates
    businesses = businesses.distinct()


    # --------------------------------
    # COUNT BEFORE CATEGORY
    # --------------------------------

    # This represents:
    #
    # Area + Keyword + Featured + Offer
    #
    # but NOT Category

    all_business_count = businesses.count()


    # --------------------------------
    # CATEGORY COUNTS
    # --------------------------------

    categories = Category.objects.annotate(
        business_count=Count(
            "businesses",
            filter=Q(
                businesses__in=businesses
            ),
            distinct=True
        )
    ).order_by("name")[:5]


    # --------------------------------
    # APPLY SELECTED CATEGORY
    # --------------------------------

    if category:

        businesses = businesses.filter(
            category__slug=category
        ).distinct()


    # --------------------------------
    # PAGINATION
    # --------------------------------

    paginator = Paginator(businesses, 5)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)


    # --------------------------------
    # DISPLAY KEYWORDS
    # --------------------------------

    for business in page_obj:

        if business.search_keywords:

            business.display_keywords = [
                keyword.strip()
                for keyword in business.search_keywords.split(",")
                if keyword.strip()
            ][:3]

        else:

            business.display_keywords = []

    # --------------------------------
    # ACTIVE OFFER
    # --------------------------------

    for business in page_obj:

        today = timezone.now().date()

        business.active_offer = next(
            (
                offer
                for offer in business.offers.all()
                if offer.is_active
                and (
                    not offer.expires_at
                    or offer.expires_at >= today
                )
            ),
            None
        )


    # --------------------------------
    # FINAL COUNT
    # --------------------------------

    business_count = businesses.count()

    # --------------------------------
    # TOP OFFERS
    # --------------------------------
    today = timezone.now().date()
    top_offers = (
        Offer.objects
        .filter(
            is_active=True,
            expires_at__gte=today,
        )
        .select_related(
            "business",
            "business__area",
        )
    )

    if selected_area:

        top_offers = top_offers.filter(
            business__area=selected_area
        )

    top_offers = top_offers[:3]


    # --------------------------------
    # PAGE TITLE
    # --------------------------------

    if selected_area:

        page_title = f"Businesses in {selected_area.name}"

    else:

        page_title = "All Businesses"


    # --------------------------------
    # PAGINATION QUERY STRING
    # --------------------------------

    query_params = request.GET.copy()

    query_params.pop("page", None)
    query_params.pop("search_submit", None)

    pagination_query = query_params.urlencode()


    # --------------------------------
    # CONTEXT
    # --------------------------------

    context = {

        "businesses": page_obj,

        "page_obj": page_obj,

        "categories": categories,

        "business_count": business_count,

        "all_business_count": all_business_count,

        "areas": Area.objects.order_by("name"),

        "offer_types": Offer.OFFER_TYPES,

        "top_offers": top_offers,

        # Selected filters

        "keyword": keyword,

        "selected_category": category,

        "selected_area": selected_area,

        "selected_offer": offer,

        "featured": featured,

        "page_title": page_title,

        "selected_sort": sort,

        "pagination_query": pagination_query,

        # List page needs counts
        "show_category_counts": True,
    }


    return render(
        request,
        "core/businesses_list.html",
        context
    )



def business_modal(request, pk):
    business = get_object_or_404(Business, pk=pk)
    latest_offers = business.offers.filter(is_active=True, expires_at__gte=timezone.now().date()).order_by("-id")[:3]

    html = render_to_string(
        "includes/business_modal.html",
        {"business": business, "latest_offers": latest_offers},
        request=request
    )

    return JsonResponse({"html": html})