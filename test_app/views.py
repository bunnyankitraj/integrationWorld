from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from rest_framework.decorators import api_view
from django.http import JsonResponse
from test_app.service.addition_service import AdditionService
from test_app.service.profileCreator import generate_xml


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

