from django.urls import path
from . import views

urlpatterns=[
    path('',views.index),
    path('requirment/process_json/', views.process_json, name='process_json'),
    path('requirment/map-xml-component-generator', views.map_xml_component_generator),
    path('requirment/mapping-excel-generator', views.mapping_excel_generator),

]
