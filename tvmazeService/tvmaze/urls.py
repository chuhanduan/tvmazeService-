from django.urls import path

from . import views

# 正在部署的应用的名称
app_name = 'tvmaze'

urlpatterns = [
    path('', views.index, name='index'),
    path('shows/', views.shows, name='shows'),
    path('visualiza/', views.visualiza, name='visualiza'),
    path('actor/', views.actor, name='actor'),
]