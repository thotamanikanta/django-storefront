from django.urls import path
from rest_framework.routers import SimpleRouter,DefaultRouter
# from .views import product_list,product_details,collection_details,collection_list
from .views import (ProductList,ProductDetail,CollectionList,CollectionDetail,
                    ProductViewSet,CollectionViewSet,ReviewViewSet,CartViewSet,CartItemViewSet)
from rest_framework_nested import routers

# router = DefaultRouter()
router = routers.DefaultRouter()
router.register('products',ProductViewSet,basename='products')
router.register('collections',CollectionViewSet)
router.register('cart',CartViewSet,basename='cart')

products_router = routers.NestedDefaultRouter(router,'products',lookup='product')
products_router.register('reviews',ReviewViewSet,basename='product-reviews')

cart_router = routers.NestedDefaultRouter(router,'cart',lookup='cart')
cart_router.register('items',CartItemViewSet ,basename='cart-items')



urlpatterns=[
        # path('products/',product_list),
        # # path('products/<int:id>',product_details),
        # # path('collections/',collection_list),
        # # path('collections/<int:pk>',collection_details,name='collection-details')
        #  path('products/',ProductList.as_view()),
        # path('products/<int:pk>',ProductDetail.as_view()),
        # path('collections/',CollectionList.as_view()),
        # path('collections/<int:pk>',CollectionDetail.as_view()),
        # path('collections/<int:pk>',collection_details,name='collection-details')
    ] + router.urls + products_router.urls + cart_router.urls