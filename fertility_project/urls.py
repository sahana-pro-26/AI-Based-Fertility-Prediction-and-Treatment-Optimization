from django.contrib import admin
from django.urls import path
from predictor.views import home, pcos

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    path('pcos/', pcos),
]
