from django_filters.rest_framework import FilterSet

from store.models import Product

class ProductFilter(FilterSet):
    class Meta:
        model = Product
        fields = {
                'collection_id':['exact'],
                'title':['icontains'],
                'unit_price':['gt','lt']
            }