from typing import Any
from django.contrib import admin,messages
from django.db.models.query import QuerySet
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models.aggregates import Count
from django.http import HttpRequest
from django.utils.html import format_html
from django.urls import reverse
from urllib.parse import urlencode

from tags.models import TaggedItem
from . import models


class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'

    def lookups(self, request: Any, model_admin: Any) -> list[tuple[Any, str]]:
        return [
                ('<10','Low')
            ]

    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any] | None:
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)
        return 



@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    # fields = ['title','slug'] # shows only these fields in admin page form
    # exclude = ['']
    # inlines = [TagInline]
    prepopulated_fields = {
            'slug':['title']
        }
    search_fields = ['title']
    autocomplete_fields =['collection']
    actions = ['clear_inventory']
    list_display = ['title','unit_price','inventory_status','collection_title']
    list_editable = ['unit_price']
    list_per_page = 10
    list_select_related = ['collection']
    list_filter = ['collection','last_update',InventoryFilter]

    def collection_title(self,product):
        return product.collection.title

    @admin.display(ordering='inventory')
    def inventory_status(self,product):
        if product.inventory < 10:
            return 'Low'
        return 'Ok'
    @admin.action(description='Clear inventory')
    def clear_inventory(self,request,queryset):
        updated_count = queryset.update(inventory=0)
        self.message_user(request,f'{updated_count} products were successfully updated',messages.ERROR)
        

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name','last_name','membership']
    list_editable = ['membership']
    list_per_page = 10
    search_fields = ['first_name__startswith','last_name__startswith']


# admin.site.register(models.Product)

class OrderItemInline(admin.TabularInline): # can also use admin.StackedInline where it the differecne is in layout of children
    autocomplete_fields = ['product']
    model = models.OrderItem
    min_num =1
    max_num = 10

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ['id','placed_at','customer','customer_name']
    autocomplete_fields = ['customer']
    list_per_page = 10
    list_select_related = ['customer']
    

    def customer_name(self,order):
        return f"{order.customer.first_name} {order.customer.last_name}"

@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title','products_count']
    search_fields = ['title']
    @admin.display(ordering='products_count')
    def products_count(self,collection):
        url = (
            reverse('admin:store_product_changelist')   # structure 'admin:app_model_page'
            + '?'
            + urlencode({
                'collection__id':str(collection.id )
                })
            ) 
        return format_html('<a href="{}"> {} </a>',url,collection.products_count) # will redirect to particular collection when clicked
        return f"{collection.products_count}"

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(products_count=Count('product'))
