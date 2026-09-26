from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Rocket.urls')),
    path('', include('fleet.urls')),
    path('', include('livraison.urls')),
    path('', include('accounts.urls')),
]

