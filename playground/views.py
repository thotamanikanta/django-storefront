from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from store.models import Collection, Customer, Order, OrderItem, Product
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, F,Value,Func,ExpressionWrapper,DecimalField
from django.db.models.aggregates import Count,Max,Min,Avg,Sum
from django.db.models.functions import Concat

def orm_commands(request):
    query_set = Product.objects.all()
    product = Product.objects.filter(pk=0).first() # return None if no id found
    try:
        product = Product.objects.get(pk=0)
    except ObjectDoesNotExist as e:
        print(e)

    query_set = Product.objects.filter(collection__id__range=(1,10)) # foreign key to collection
    query_set = Product.objects.filter(title__icontains='coffee')
    query_set = OrderItem.objects.filter(product__collection__id=3)
    query_set = Product.objects.filter(Q(inventory__lt=10)| Q(unit_price = 20))
    query_set = Product.objects.filter(inventory=F('collection__id'))
    query_set = Product.objects.order_by('-title')
    query_set = Product.objects.values('id','title','collection__title')
    query_set = Product.objects.values_list('id','title','collection__title')
    query_set = OrderItem.objects.select_related('product')
    # print(query_set)
    query_set = Product.objects.filter(id__in=OrderItem.objects.values('product__id').distinct())
    query_set = Product.objects.only('id','title') # loads only id and title
    query_set = Product.objects.defer('description') # ignores description

    
    query_set = Product.objects.select_related('collection').all()
    query_set = Product.objects.prefetch_related('promotions').select_related('collection').all()

    query_set = Order.objects.select_related('customer').prefetch_related('orderitem_set__product').order_by('-placed_at')[:5]
    
    print(query_set)

    for order in query_set:
        # print(product.product.title)
        for item in order.orderitem_set.all():
            print(f"Product Title: {item.product.title}")
    
    # return render(request,'hello.html',{"name":"King Bob",'products':(query_set)})
    return render(request,'hello.html',{"name":"King Bob",'orders':(query_set)})

def aggregate_methods(request):
    
    result = Product.objects.aggregate(count=Count(id),min_price=Min('unit_price')) 
    result = OrderItem.objects.filter(product__id=1).aggregate(units_sold=Sum('quantity'))
    result = Order.objects.filter(customer__id=1).aggregate(orders_placed=Count('id'))
    result = Product.objects.filter(collection__id=3).aggregate(min_price=Min('unit_price'),max_price=Max('unit_price'))
    print(result)

    return render(request,'hello.html',{"name":"King Bob",'result':result})

def annotate_methods(request):
    
    query_set = Product.objects.annotate(is_new=Value(True)) # will add new filed called is_new and set value to 1

    query_set = Product.objects.annotate(new_id=F('id')+1) # will add new field id and set value to id Plus 1 of product table
    query_set = Customer.objects.annotate(full_name=Func(F('first_name'),Value(' '),F('last_name'),function='CONCAT'))

    query_set = Customer.objects.annotate(full_name=Concat('first_name',Value(' '),'last_name')) # Short way to concat 2 or more fields
    print(query_set)
    return render(request,'hello.html',{"name":"King Bob",'products':(query_set)})

def group_by_method(request):
    
   
    query_set = Customer.objects.annotate(order_counts=Count('order')) # Left Joins order table and gives count of orders group by customers

    return render(request,'hello.html',{"name":"King Bob",'products':(query_set)})

def expresson_wrapper(request):
    
    
    # query_set = Product.objects.annotate(discounted_price=F('unit_price')*0.8) # Throws '*' expression involving these types: DecimalField, FloatField
    discounted_price = ExpressionWrapper(F('unit_price')*0.8,output_field=DecimalField())    
    query_set = Product.objects.annotate(discounted_price=discounted_price)
    print(query_set)
    return render(request,'hello.html',{"name":"King Bob",'products':(query_set)})

from django.contrib.contenttypes.models import ContentType
from store.models import Product
from tags.models import TaggedItem

def get_tagged_items_with_content_type(request):
    query_set = TaggedItem.objects.get_tags_for(Product,1)
    # content_type = ContentType.objects.get_for_model(Product)
    # query_set = TaggedItem.objects \
    # .select_related('tag') \
    # .filter(
    #     content_type =content_type,
    #     object_id=1
    #     )
    return render(request,'hello.html',{"name":"King Bob",'products':list(query_set)})

def insert_data(request):
    collection = Collection()
    collection.title = 'Video Games'
    collection.featured_product = Product(pk=1)
    # collection.featured_product_id = 1 # other way to set feature_product
    collection.save()

    # collection = Collection.objects.create(title='d',featured_product=1) other way to insert data
    return render(request,'hello.html',{"name":"King Bob"})

def update_data(request):
    # collection = Collection(pk=11) # will have to mention all the fields otherwise it will take empty string as default value
    # collection = Collection.objects.get(pk=11)
    # # collection.title = 'Games' 
    # collection.featured_product = None
    # # collection.featured_product_id = 1 # other way to set feature_product
    # collection.save()

    collection = Collection.objects.filter(pk=11).update(featured_product=None) #other way to insert data
    return render(request,'hello.html',{"name":"King Bob"})

def delete_dt(request):
    collection = Collection(pk=11) 
    collection.delete()
    Collection.objects.filter(id__lt=5).delete()

    return render(request,'hello.html',{"name":"King Bob"})

from django.db import transaction

# @transaction.atomic
def transaction_atomic(request):
    with transaction.atomic():
  

        order = Order()
        order.customer_id = 1
        order.save()


        item = OrderItem()
        item.order = order
        item.product_id = -1
        item.quantity = 1
        item.unit_price = 10
        item.save()




    return render(request,'hello.html',{"name":"King Bob"})

# execute raw queries
from django.db import connection
def say_hello(request):
    query_set = Product.objects.raw("select * from store_product")
    # cursor = connection.cursor()
    # cursor.execute('select * from store_product')
    # cursor.close()
    with connection.cursor() as cursor:
        cursor.execute()
    print(list(query_set))
    return render(request,'hello.html',{"name":"King Bob",'result':list(query_set)})