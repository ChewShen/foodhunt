from django.urls import path
from . import views

urlpatterns=[
    path('',views.home,name='home'),
    path('selectionPage/',views.selectionPage,name='selectionPage'),
    # Case 1: /shops/ -> Shows ALL shops
    path('shops/', views.shop_list_view, name='all_shops'),
    
    # Case 2: /shops/kuchai_lama/ -> Shows specific area
    path('shops/<str:area>/', views.shop_list_view, name='area_shops'),

    path('api/random/', views.pick_random_shop, name='pick_random_shop'),
]