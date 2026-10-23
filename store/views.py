from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.mixins import ListModelMixin,CreateModelMixin
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet

from store.models import Collection, Product
from .serializers import CollectionSerializer, ProductSerializer
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
    queryset = Product.objects.all()

    def get_serializer_context(self):
        return {"request":self.request}
    
    

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
        return super().delete(request, *args, **kwargs)

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
    

class CollectionList(ListCreateAPIView):
    queryset = Collection.objects.annotate(products_count=Count('products')).all() # products is related name from products table to collection . counts no of products for each collection
    serializer_class = CollectionSerializer

class CollectionDetail(RetrieveUpdateDestroyAPIView):
    queryset = Collection.objects.annotate(products_count=Count('products')).all() # products is related name from products table to collection . counts no of products for each collection
    serializer_class = CollectionSerializer
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
