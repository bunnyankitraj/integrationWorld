from django.urls import path
from . import views

urlpatterns=[
    path('',views.index),
    path('process_json/', views.process_json, name='process_json'),
    path('map_xml_component_generator', views.map_xml_component_generator, name='map_xml_component_generator'),
]
