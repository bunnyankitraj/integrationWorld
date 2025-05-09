from django.urls import path
from . import views

urlpatterns=[
    path('',views.index),
    path('process_json/', views.process_json, name='process_json'),
    path('startFileMove', views.start_file_move, name='start_file_move'),
]
