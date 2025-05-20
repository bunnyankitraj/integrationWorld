from django.http import HttpResponse
from rest_framework.decorators import api_view
from django.http import JsonResponse
import traceback
from mappingUtility.Utility import ComponentUtilsService,LogUtils
from mappingUtility.service import BoomiApiService, ExcelMappingGenerator, MappingService,FileTypeChecker

import logging

logger = logging.getLogger(__name__)

def sample_api(request):
    LogUtils.log_api_request(logger, request, "Sample API called")
    logger.info("Info called")
    logger.debug("Debugging information")
    logger.error("Error occurred")
    logger.warning("Warning message")
    logger.critical("Critical error")
    return JsonResponse({'message': 'Success'})

@api_view(['POST'])
def map_xml_component_generator(request):
    LogUtils.log_api_request(logger, request, "map_xml_component_generator")
    try:
        logger.info("Request received for map_xml_component_generator")
        source_file = request.FILES.get('source')
        destination_file = request.FILES.get('destination')
        excel_file = request.FILES.get('excel')

        if not all([source_file, destination_file, excel_file]):
            return JsonResponse({'error': 'Missing one or more files'}, status=400)

        source_file_type = FileTypeChecker.get_file_type(source_file)
        logger.info(f"Source file type detected: {source_file_type}")
        
        destination_file_type = FileTypeChecker.get_file_type(destination_file)
        logger.info(f"Destination file type detected: {destination_file_type}")
        
        source_data = source_file.read()
        destination_data = destination_file.read()
        excel_data = excel_file.read()
        
        logger.info('Processing files...')
        processed_result = MappingService.process_mapping_files(source_data, destination_data, excel_data,source_file_type,destination_file_type)

        logger.info('Files processed')
        componenetId = ComponentUtilsService.extract_component_id(processed_result)

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
    LogUtils.log_api_request(logger, request, "profile_xml_generator")
    try:
        file_type = request.POST.get('type')
        content_file = request.FILES.get('content')
        
        content = content_file.read()
        xml_response = MappingService.profile_component_generator(content,file_type)
        
        xml_boomi_response = BoomiApiService.upload_component(xml_response)
        logger.info("Uploaded component successfully")
        logger.info(xml_boomi_response)
        componenetId = ComponentUtilsService.extract_component_id(xml_boomi_response)

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
    logger.info("Request received for mapping_excel_generator")
    LogUtils.log_api_request(logger, request, "mapping_excel_generator")
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

        processed_result = ExcelMappingGenerator.main(source_type, source_data, destination_type, target_data)
        return processed_result

    except Exception as e:
        tb = traceback.format_exc()
        return JsonResponse({
            'error': str(e),
            'traceback': tb,
            'function': 'mapping_excel_generator'
        }, status=500)
