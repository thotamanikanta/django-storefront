from rest_framework import serializers

from playground.views import expresson_wrapper
from decimal import Decimal
from store.models import Product, Collection

class CollectionSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Collection
        fields = ['id','title','products_count']

class ProductSerializer1(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    # unit_price = serializers.DecimalField(max_digits=6,decimal_places=2)
    price = serializers.DecimalField(max_digits=6,decimal_places=2,source='unit_price') # to use different field name from model we have to use source from model 
    price_with_tax = serializers.SerializerMethodField(method_name="calculate_tax") 

    # collection = serializers.PrimaryKeyRelatedField(queryset=Collection.objects.all()) # returns id of collection
    # collection = serializers.StringRelatedField() # return string representaion of collection 
    # collection = CollectionSerializer() # return id and title form collection 
    collection = serializers.HyperlinkedRelatedField(queryset=Collection.objects.all(),view_name='collection-details') # provides hyper link to navigate to selected collection

    def calculate_tax(self,product:Product):
        
        return product.unit_price * Decimal(1.1)

class ProductSerializer(serializers.ModelSerializer):
    # collection = CollectionSerializer() if need to modify collection
    price_with_tax = serializers.SerializerMethodField(method_name="calculate_tax") 

    class Meta:
        model = Product
        fields = ['id','title','slug','inventory','description','unit_price','collection','price_with_tax']

    def calculate_tax(self,product:Product):
        
        return product.unit_price * Decimal(1.1)
# overwrite default create and update to customize the save metho
    # def create(self, validated_data):
    #     product = Product(**validated_data)
    #     product.save()
    #     return product

    # def update(self, instance, validated_data):
    #     instance.unit_price = validated_data.get('unit_price')
    #     instance.save()
    #     return instance

  

