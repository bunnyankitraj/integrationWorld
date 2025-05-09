import xml.etree.ElementTree as ET

def extract_component_id(xml_response):
    try:
        namespace = {'bns': 'http://api.platform.boomi.com/'}
        root = ET.fromstring(xml_response)
        
        component_id = root.attrib.get('componentId')
        return component_id
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return None
