import xml.etree.ElementTree as ET
import logging

logger = logging.getLogger(__name__)

def extract_component_id(xml_response):
    try:
        root = ET.fromstring(xml_response)
        
        component_id = root.attrib.get('componentId')
        return component_id
    except ET.ParseError as e:
        logger.error(f"Error parsing XML: {e}")
        return None
