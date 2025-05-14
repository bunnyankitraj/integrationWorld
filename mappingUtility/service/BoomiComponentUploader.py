import requests


def upload_component(xml_body: str):

    try:
        endpoint_url = "https://api.boomi.com/api/rest/v1/dpwsubaccount1-FZOWUA/Component"
        auth_token = "cHJhdGlrLmFyb3JhQGV4dC5kcHdvcmxkLmNvbTpJbmZ5QDk4NzY1"

        headers = {
            'Content-Type': 'application/xml',
            'Accept': 'application/xml',
            'Authorization': f'Basic {auth_token}',
        }

        response = requests.post(endpoint_url, headers=headers, data=xml_body)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error": str(e),
            "response": getattr(e.response, "text", None)
        }
