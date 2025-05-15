from django.shortcuts import render

from django.http import HttpResponse
from rest_framework.decorators import api_view
from django.http import JsonResponse
import traceback
from mappingUtility.service import MappingService,ComponentService,FeildMappingExcelGenerator,BoomiComponentUploader,FileTypeChecker
from mappingUtility.strategy.JSONProcessor import JSONProcessor
from mappingUtility.strategy.XMLProcessor import XMLProcessor
from mappingUtility.strategy.FileProcessingContext import FileProcessingContext

@api_view(['POST'])
def map_xml_component_generator(request):
    try:
        print("Request received")
        source_file = request.FILES.get('source')
        destination_file = request.FILES.get('destination')
        excel_file = request.FILES.get('excel')

        if not all([source_file, destination_file, excel_file]):
            return JsonResponse({'error': 'Missing one or more files'}, status=400)

        source_file_type = FileTypeChecker.get_file_type(source_file)
        destination_file_type = FileTypeChecker.get_file_type(destination_file)
        
        source_data = source_file.read()
        destination_data = destination_file.read()
        excel_data = excel_file.read()
        
        print('Processing files...')
        processed_result = MappingService.process_mapping_files(source_data, destination_data, excel_data,source_file_type,destination_file_type)

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
        file_type = request.POST.get('type')
        data = request.POST.get('content')
        print("Request received")
        print(f"File type: {file_type}")
        print(f"Data: {data}")

        if file_type == 'json' or file_type == 'JSON':
            strategy = JSONProcessor()
        elif file_type == 'xml' or file_type == 'XML':
            strategy = XMLProcessor()
        else:
            return JsonResponse({'error': 'Unsupported type'}, status=400)

        # Initialize the context with the selected strategy
        context = FileProcessingContext(strategy)

        # Process and get result
        xml_response = context.execute(data)
        
        xml_boomi_response = BoomiComponentUploader.upload_component(xml_response)
        print("Uploaded component successfully")
        print(xml_boomi_response)
        componenetId = ComponentService.extract_component_id(xml_boomi_response)

        return JsonResponse({
            'status': "success",
            'message': 'Files processed successfully',
            'redirectUrl': 'https://platform.boomi.com/AtomSphere.html#build;accountId=dpwsubaccount1-FZOWUA;branchName=main;components='+componenetId, 
            'componentId': componenetId,
        })

    except Exception as e:
        tb = traceback.format_exc()
        return JsonResponse({
            'error': str(e),
            'traceback': tb,
            'function': 'profile_xml_generator'
        }, status=500)


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
        source_type = source_type.upper()
        destination_type = destination_type.upper()

        processed_result = FeildMappingExcelGenerator.main(source_type, source_data, destination_type, target_data)
        return processed_result

    except Exception as e:
        tb = traceback.format_exc()
        return JsonResponse({
            'error': str(e),
            'traceback': tb,
            'function': 'mapping_excel_generator'
        }, status=500)
