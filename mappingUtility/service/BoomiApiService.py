import requests
from resources.globlas import boomi_endpoint_url, auth_token
import logging

logger = logging.getLogger(__name__)

def upload_component(xml_body):
    logger.info("Uploading component to Boomi API.")
    try:
        headers = {
            'Content-Type': 'application/xml',
            'Accept': 'application/xml',
            'Authorization': f'Basic {auth_token}',
        }
        response = requests.post(boomi_endpoint_url, headers=headers, data=xml_body)
        logger.info(f"Boomi API response received: {response.status_code}")
        response.raise_for_status()
        logger.info(f"Boomi API response received: {response.status_code} {response.text}")
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}", extra={"request_exception": str(e)})
        return {
            "status": "error",
            "error": str(e),
            "response": getattr(e.response, "text", None)
        }
