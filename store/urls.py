from django.urls import path
# from .views import product_list,product_details,collection_details,collection_list
from .views import ProductList,ProductDetail,CollectionList,CollectionDetail
urlpatterns=[
        # path('products/',product_list),
        # path('products/<int:id>',product_details),
        # path('collections/',collection_list),
        # path('collections/<int:pk>',collection_details,name='collection-details')
         path('products/',ProductList.as_view()),
        path('products/<int:pk>',ProductDetail.as_view()),
        path('collections/',CollectionList.as_view()),
        path('collections/<int:pk>',CollectionDetail.as_view()),
        # path('collections/<int:pk>',collection_details,name='collection-details')
    ]