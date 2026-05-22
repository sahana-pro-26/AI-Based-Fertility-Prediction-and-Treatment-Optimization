from django.contrib import admin
from django.urls import path
from predictor import views

urlpatterns = [
    path('', views.home, name='home'),
    path('pcos/', views.pcos, name='pcos'),
    path('ivf/', views.ivf, name='ivf'),
    path('score/', views.score, name='score'),
    path('recommend/', views.recommend, name='recommend'),
]
