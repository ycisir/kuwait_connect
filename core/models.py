from django.db import models
from django.utils import choices
from django.utils.text import slugify
from urllib.parse import quote

class Area(models.Model):
	name = models.CharField(max_length=255)
	slug = models.SlugField(unique=True, blank=True)
	image = models.ImageField(upload_to="areas/")

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)

		super().save(*args, **kwargs)

	def __str__(self):
		return self.name



class Category(models.Model):
	name = models.CharField(max_length=255)
	slug = models.SlugField(unique=True, blank=True)
	icon = models.ImageField(upload_to="categories/", blank=True, null=True)

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)

		super().save(*args, **kwargs)

	def __str__(self):
		return self.name



class Business(models.Model):
	# a area and category has many businesses
	area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name="businesses")
	category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="businesses")
	name = models.CharField(max_length=255)
	slug = models.SlugField(unique=True, blank=True)
	description = models.TextField(blank=True)
	whatsapp = models.CharField(max_length=20, help_text="Include country code, e.g. 91987654321")
	featured = models.BooleanField(default=False)
	website = models.URLField(blank=True)
	instagram_url = models.URLField(blank=True)
	facebook_url = models.URLField(blank=True)
	tiktok_url = models.URLField(blank=True)
	google_maps_url = models.URLField()
	phone = models.CharField(max_length=20, help_text="Include country code (e.g. +91512345678)")
	search_keywords = models.TextField(blank=True, help_text="Comma separated keywords")
	cover_image = models.ImageField(upload_to="businesses/covers/")
	logo = models.ImageField(upload_to="businesses/logos/")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	@property
	def whatsapp_url(self):
		message = quote(f"Hi, I found your business on Kuwait Connect and I'd like to know more.")
		return f"https://wa.me/{self.whatsapp}?text={message}"

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)

		super().save(*args, **kwargs)

	def __str__(self):
		return self.name



class Offer(models.Model):
	# a offer has many businesses
	business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="offers")

	DISCOUNT = "discount"
	BOGO = "bogo"
	FREE = "free"

	OFFER_TYPES = [
        (DISCOUNT, "Discount"),
        (BOGO, "Buy 1 Get 1"),
        (FREE, "Free Offer")
    ]
	title = models.CharField(max_length=255)
	offer_type = models.CharField(max_length=20, choices=OFFER_TYPES, default=DISCOUNT)
	expires_at = models.DateField(null=True, blank=True, help_text="Leave blank if the offer has no expiry date.")
	image = models.ImageField(upload_to="offers/", blank=True, null=True)
	is_active = models.BooleanField(default=True)

	def __str__(self):
		return self.title


class SearchLog(models.Model):

    query = models.CharField(max_length=255)

    # a area and category has many searchlogs
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True, related_name="search_logs")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="search_logs")

    ip_address = models.GenericIPAddressField(null=True, blank=True)

    searched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.query