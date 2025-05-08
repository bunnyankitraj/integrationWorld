from django.urls import path
from . import views
from .views import add_numbers

urlpatterns=[
    path('',views.index),
    path('add/', add_numbers),
    path('process_json/', views.process_json, name='process_json')
]
