from django.contrib import admin
from django.urls import path
from . import views

app_name = "users_app"

urlpatterns = [
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('update/', views.UpdatePassword.as_view(), name='update'),
    path('plantilla/', views.PlantillaView.as_view(), name='plantilla'),
    path('perfil/<int:pk>/', views.Perfil.as_view(), name='perfil'),
    path('directorio/', views.Directorio.as_view(), name='directorio'),
    path('batch-users/', views.Batch_Users.as_view(), name='batch-users'),
]
