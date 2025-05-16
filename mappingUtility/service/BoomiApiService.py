import requests
from resources.globlas import boomi_endpoint_url, auth_token
import logging

logger = logging.getLogger(__name__)

def upload_component(xml_body):
    logger.info("Uploading component to Boomi API.", extra={"xml_body": xml_body})
    try:
        headers = {
            'Content-Type': 'application/xml',
            'Accept': 'application/xml',
            'Authorization': f'Basic {auth_token}',
        }
        response = requests.post(boomi_endpoint_url, headers=headers, data=xml_body)
        logger.info("Boomi API response received.", extra={"status_code": response.status_code, "response_text": response.text})
        if response.status_code == 201:
            logger.info("Component uploaded successfully.")
            return response.text
        elif response.status_code == 400:
            logger.error("Bad request. Check the XML format.", extra={"response_text": response.text})
            raise ValueError("Bad request. Check the XML format.")
        elif response.status_code == 401:
            logger.error("Unauthorized access. Check authentication.", extra={"response_text": response.text})
            raise ValueError("Unauthorized access. Check authentication.")
        elif response.status_code == 403:
            logger.error("Forbidden access. Check permissions.", extra={"response_text": response.text})
            raise ValueError("Forbidden access. Check permissions.")
        else:
            logger.error(f"Unexpected error: {response.status_code}", extra={"response_text": response.text})
            raise ValueError(f"Unexpected error: {response.status_code}")
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}", extra={"request_exception": str(e)})
        return {
            "status": "error",
            "error": str(e),
            "response": getattr(e.response, "text", None)
        }
