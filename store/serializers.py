from rest_framework import serializers

from playground.views import expresson_wrapper
from decimal import Decimal
from store.models import Cart, CartItem, Product, Collection, Review

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

  

class ReviewSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Review
        fields = ['id','date','name','description']

    def create(self, validated_data):
        product_id= self.context['product_id']
        return Review.objects.create(product_id=product_id,**validated_data)

class SimpleProductSerializer(serializers.ModelSerializer):
  
    class Meta:
        model = Product
        fields = ['id','title','unit_price']




class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ['id','product','quantity','total_price']

    def get_total_price(self,cart_item: CartItem):
        return cart_item.quantity *cart_item.product.unit_price

class CartSerializer(serializers.ModelSerializer):
    id =serializers.UUIDField(read_only = True)
    items = CartItemSerializer(many=True,read_only=True)
    total_price = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id','items','total_price']

    def get_total_price(self,cart: Cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])



class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
    class Meta:
        model = CartItem
        fields = ['id', 'product_id','quantity']

    def validate_product_id(self,value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No product with the give ID was found')
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        try:
            cart_item = CartItem.objects.get(cart_id=cart_id,product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
        
        return self.instance

class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']