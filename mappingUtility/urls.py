from django.urls import path
from . import views

urlpatterns=[
    
    path('', views.index),

    # Profile XML Generator
    path('api/generate/profile-xml', views.generate_profile_xml),

    # Mapping Excel Generator
    path('api/generate/mapping-excel', views.generate_mapping_excel),
    path('api/generate/mapping-excel-with-source-target', views.generate_mapping_excel_with_sources),

    # Map XML Component Generator
    path('api/generate/map-xml', views.generate_map_xml),
    path('api/generate/map-xml-from-excel', views.generate_map_xml_from_excel),

    # Test API
    path('test/sample', views.sample_api)

]
