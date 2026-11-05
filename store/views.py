from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.decorators import api_view,action
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.mixins import ListModelMixin,CreateModelMixin,RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet



from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from store.filters import ProductFilter
from store.models import Cart, CartItem, Collection, Customer, OrderItem, Product,Review
from store.pagination import DefaultPagination
from .serializers import AddCartItemSerializer, CartItemSerializer, CartSerializer, CollectionSerializer, CustomerSerializer, ProductSerializer,ReviewSerializer, UpdateCartItemSerializer
from django.db.models.aggregates import Count
# Create your views here.

class ProductList(ListCreateAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    # to overwrite query_set, serializer_class or serializer context
    # def get_queryset(self):
    #     return Product.objects.select_related('collection').all()
    # def get_serializer_class(self):
    #     return ProductSerializer
    def get_serializer_context(self):
        return {"request":self.request}
    
class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields = ['unit_price']
    search_fields = ['title','description']
    # filterset_fields = ['collection_id'] #without filter class
    filterset_class =ProductFilter
    queryset = Product.objects.all()
    pagination_class = DefaultPagination
    """
    Overwrite get_queryset method to filter manually with collection id.
    If using DJnagoFIlterBackend that will automatically takes care of filter
    """
    # def get_queryset(self):
    #     queryset = Product.objects.all()
    #     print("))))))))))))))")
    #     collection_id = self.request.query_params.get('collection_id')
    #     print(collection_id,"????????????????????//")
    #     if collection_id is not None:
    #         queryset = queryset.filter(collection__id=collection_id)
    #     return queryset

    def get_serializer_context(self):
        return {"request":self.request}

    def destroy(self, request, *args, **kwargs):

        if OrderItem.objects.filter(product_id=kwargs['pk']).count() >0: # orderitems is reverse relation related name from product to orderitems table(Default orderitem_set)
            return Response({"error":"Product cannot be deleted as associsated Orderitem exists"},status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)
    
    

# class ProductList(APIView):
#     def get(self,request):
#         queryset = Product.objects.select_related('collection').all() # to avoid n+1 queries to get collection data
#         serializer = ProductSerializer(queryset,many =True,context={'request': request})
#         return Response("serializer.data")
#     def post(self,request):
#         serializer = ProductSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True) # automatcy returns 400 bad request if data is not validated
#         serializer.save()
#         return Response(serializer.data,status=status.HTTP_201_CREATED)

class ProductDetail(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # lookup_field = 'id' # use this if url has pk as different name

    def delete(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        product = get_object_or_404(Product,pk=id)
        if product.orderitems.count()>0: # orderitems is reverse relation related name from product to orderitems table(Default orderitem_set)
            return Response({"error":"Product cannot be deleted as associsated Orderitem exists"},status=status.HTTP_403_FORBIDDEN)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# class ProductDetail(APIView):
    
#     def get(self,request,id):
#         product = get_object_or_404(Product,pk=id)
#         serializer = ProductSerializer(product)
#         return Response(serializer.data)
#     def put(self,request,id):
#         product = get_object_or_404(Product,pk=id)
#         serializer = ProductSerializer(product,data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data,status=status.HTTP_201_CREATED)
#     def delete(self,request,pk):
#         product = get_object_or_404(Product,pk=id)
#         if product.orderitems.count()>0: # orderitems is reverse relation related name from product to orderitems table(Default orderitem_set)
#             return Response({"error":"Product cannot be deleted as associsated Orderitem exists"},status=status.HTTP_403_FORBIDDEN)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count('products')).all() # products is related name from products table to collection . counts no of products for each collection
    serializer_class = CollectionSerializer

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']).count() >0:
            return Response({"error":"Collection cannot be deleted as associsated Product exists"},status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
    
class CollectionList(ListCreateAPIView):
    queryset = Collection.objects.annotate(products_count=Count('products')).all() # products is related name from products table to collection . counts no of products for each collection
    serializer_class = CollectionSerializer

class CollectionDetail(RetrieveUpdateDestroyAPIView):
    queryset = Collection.objects.annotate(products_count=Count('products')).all() # products is related name from products table to collection . counts no of products for each collection
    serializer_class = CollectionSerializer

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    def delete(self, request, pk):
        collection = get_object_or_404(
        Collection.objects.annotate(products_count=Count('products')),
        pk=pk
        )
        if collection.products.count()>0: # orderitems is reverse relation related name from product to orderitems table(Default orderitem_set)
            return Response({"error":"Collection cannot be deleted as associsated Product exists"},status=status.HTTP_403_FORBIDDEN)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

# @api_view(['GET','POST'])
# def collection_list(request):
#     # products = Product.objects.all()
#     if request.method == 'GET':
#         queryset = Collection.objects.annotate(products_count=Count('products')).all() # products is related name from products table to collection . counts no of products for each collection
#         serializer = CollectionSerializer(queryset,many =True,context={'request': request})
#         return Response(serializer.data)
#     elif request.method == 'POST':
#         serializer = CollectionSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True) # automatcy returns 400 bad request if data is not validated
#         serializer.save()
#         return Response(serializer.data,status=status.HTTP_201_CREATED)

# @api_view(["GET","PUT","DELETE"])
# def collection_details(request,pk):
#     # try:
#     #     product = Product.objects.get(pk=id)
#     #     serializer = ProductSerializer(product)
#     #     return Response(serializer.data)
#     # except Product.DoesNotExist:
#     #     return Response(status=404)
#     collection = get_object_or_404(
#         Collection.objects.annotate(products_count=Count('products')),
#         pk=pk
#         )
#     if request.method == 'GET':
#         serializer = CollectionSerializer(collection)
#         return Response(serializer.data)
#     elif request.method == 'PUT':
#             serializer = CollectionSerializer(collection,data=request.data)
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#             return Response(serializer.data,status=status.HTTP_201_CREATED)
#     elif request.method == 'DELETE':
#         if collection.products.count()>0: # orderitems is reverse relation related name from product to orderitems table(Default orderitem_set)
#             return Response({"error":"Collection cannot be deleted as associsated Product exists"},status=status.HTTP_403_FORBIDDEN)
#         collection.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):

        return {'product_id': self.kwargs['product_pk']}


from django.db.models import Prefetch

class CartViewSet(CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    # serializer_class = CartSerializer
    

    # def get_queryset(self):
    #     return Cart.objects.prefetch_related(
    #         Prefetch(
    #             'items',
    #             queryset=CartItem.objects.select_related('product')
    #         )
    #     )

class CartItemViewSet(ModelViewSet):
    http_method_names = ['get','post','patch','delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        if self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {'cart_id':self.kwargs['cart_pk']}

    def get(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product')

class CustomerViewSet(CreateModelMixin,RetrieveModelMixin,UpdateModelMixin,GenericViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    @action(detail=False)
    def me(self,request): # custom endpoint works customers/me
        # user = request.user

        customer = Customer.objects.get(user_id=request.user.id)
        serializer = CustomerSerializer(customer)
  
        return Response(serializer.data)