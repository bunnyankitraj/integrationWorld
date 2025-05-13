from django.shortcuts import render

from django.http import HttpResponse
from rest_framework.decorators import api_view
from django.http import JsonResponse
import traceback
from mappingUtility.service import MappingService, ComponentService,ProfileCreator,FeildMappingExcelGenerator;

@api_view(['POST'])
def map_xml_component_generator(request):
    try:
        print("Request received")
        source_file = request.FILES.get('source')
        destination_file = request.FILES.get('destination')
        excel_file = request.FILES.get('excel')

        if not all([source_file, destination_file, excel_file]):
            return JsonResponse({'error': 'Missing one or more files'}, status=400)

        source_data = source_file.read()
        destination_data = destination_file.read()
        excel_data = excel_file.read()

        print('Files received')
        
        print('Processing files...')
        processed_result = MappingService.process_mapping_files(source_data, destination_data, excel_data)

        print('Files processed')
        componenetId = ComponentService.extract_component_id(processed_result)

        # Return the processed result and componentId
        return JsonResponse({
            'status': "success",
            'message': 'Files processed successfully',
            'redirectUrl': 'https://platform.boomi.com/AtomSphere.html#build;accountId=dpwsubaccount1-FZOWUA;branchName=main;components='+componenetId, 
            'componentId': componenetId,
            # 'response': processed_result
        })

    except Exception as e:
        tb = traceback.format_exc()
        return JsonResponse({
            'error': str(e),
            'traceback': tb,
            'function': 'map_xml_component_generator'
        }, status=500)


def index(request):
    return HttpResponse("Hello World")


@api_view(['POST'])
def profile_xml_generator(request):
    try:
        data = request.data

        data['processed'] = True
        data['message'] = 'Your data has been processed.'

        xml_response = ProfileCreator.generate_profile_xml(data)

        return HttpResponse(xml_response, content_type="application/xml")

    except Exception as e:
        # In case of an error, return a JSON response with error message
        return JsonResponse({'error': str(e)}, status=400)


@api_view(['POST'])
def mapping_excel_generator(request):
    try:
        source_type = request.POST.get('source_type')
        destination_type = request.POST.get('destination_type')
        source_file = request.FILES.get('source')
        destination_file = request.FILES.get('destination')

        if not all([source_type, destination_type, source_file, destination_file]):
            return JsonResponse({'error': 'Missing one or more required fields or files'}, status=400)

        source_data = source_file.read()
        target_data = destination_file.read()

        processed_result = FeildMappingExcelGenerator.main(source_type, source_data, destination_type, target_data)
        return processed_result

    except Exception as e:
        tb = traceback.format_exc()
        return JsonResponse({
            'error': str(e),
            'traceback': tb,
            'function': 'mapping_excel_generator'
        }, status=500)
