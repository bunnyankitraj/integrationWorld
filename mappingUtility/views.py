from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from rest_framework.decorators import api_view
from django.http import JsonResponse
from mappingUtility.service.addition_service import AdditionService
from mappingUtility.service.profileCreator import generate_xml
import os
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import uuid
from tempfile import NamedTemporaryFile
import uuid
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework.decorators import api_view

def index(request):
    return HttpResponse("Hello Geeks")


@api_view(['POST'])
def add_numbers(request):
    try:
        a = float(request.GET.get('a', 0))
        b = float(request.GET.get('b', 0))
        result = AdditionService(a, b).compute()
        return JsonResponse({'result': result})
    except (ValueError, TypeError) as e:
        return JsonResponse({'error': str(e)}, status=400)
    

@api_view(['POST'])
def process_json(request):
    try:
        data = request.data

        data['processed'] = True
        data['message'] = 'Your data has been processed.'

        xml_response = generate_xml(data)

        return HttpResponse(xml_response, content_type="application/xml")

    except Exception as e:
        # In case of an error, return a JSON response with error message
        return JsonResponse({'error': str(e)}, status=400)


# A sample random function that processes all three files
def process_files(source_data, destination_data, excel_data):
    # Just a dummy implementation of file processing
    # In reality, this can involve data manipulation, file conversion, etc.
    print("Processing files...")
    
    # Example of something you might do with the files (e.g., combining them, extracting data)
    processed_data = {
        'source_size': len(source_data),
        'destination_size': len(destination_data),
        'excel_size': len(excel_data),
    }
    # You can also return some other result based on the file processing logic
    return processed_data

@api_view(['POST'])
def start_file_move(request):
    try:
        source_file = request.FILES.get('source')
        destination_file = request.FILES.get('destination')
        excel_file = request.FILES.get('excel')

        if not all([source_file, destination_file, excel_file]):
            return JsonResponse({'error': 'Missing one or more files'}, status=400)

        # Read the files directly from the request and process them
        source_data = source_file.read()
        destination_data = destination_file.read()
        excel_data = excel_file.read()

        # Call the random function to process all three files
        processed_result = process_files(source_data, destination_data, excel_data)

        # Return the processed result
        return JsonResponse({
            'message': 'Files processed successfully',
            'processed_result': processed_result
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
