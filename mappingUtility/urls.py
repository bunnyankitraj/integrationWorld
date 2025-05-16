from django.urls import path
from . import views

urlpatterns=[
    path('',views.index),
    path('requirment/profile-xml-generator', views.profile_xml_generator),
    path('requirment/map-xml-component-generator', views.map_xml_component_generator),
    path('requirment/mapping-excel-generator', views.mapping_excel_generator),
    path('test/sample-api', views.sample_api),

]
