from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search,name="search"),
    path('searchByDistrict/', views.searchByDistrict,name="searchByDistrict"),
    path('searchByPinCode/', views.searchByPinCode,name="searchByPinCode"),
    path('searchByDistrictResults/', views.searchByDistrictResults,name="searchByDistrictResults"),
    path('searchByPinCodeResults/', views.searchByPinCodeResults,name="searchByPinCodeResults"),
    path('results/', views.results, name='results'),
    path('error/', views.error, name="error"),
    path('load_districts/',views.load_districts, name="load_districts"),

]
