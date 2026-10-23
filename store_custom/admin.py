from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from store.admin import ProductAdmin
from store.models import Product
from tags.models import TaggedItem
# Register your models here.

class TagInline(GenericTabularInline):
    model =TaggedItem

class CUstomPrductAdmin(ProductAdmin):
    inlines = [TagInline]

admin.site.unregister(Product)
admin.site.register(Product,CUstomPrductAdmin)