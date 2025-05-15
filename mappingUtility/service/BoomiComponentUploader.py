import requests
from resources.globlas import boomi_endpoint_url, auth_token

def upload_component(xml_body: str):

    try:
        
        headers = {
            'Content-Type': 'application/xml',
            'Accept': 'application/xml',
            'Authorization': f'Basic {auth_token}',
        }

        response = requests.post(boomi_endpoint_url, headers=headers, data=xml_body)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error": str(e),
            "response": getattr(e.response, "text", None)
        }
