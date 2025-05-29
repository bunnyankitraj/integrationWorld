import logging
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString
from mappingUtility.strategy.ComponentGenerator import FileProcessor
import xml.etree.ElementTree as ET

from resources.globlas import folder_id, folder_path, branch_id, branch_name, boomi_component_bns_url, boomi_component_xsi_url
import os

logger = logging.getLogger(__name__)

class EDIFACTProcessor(FileProcessor):
    def process(self, file_content):
        logger.info("Processing EDIFACT file content.")
        return EDIFACTProcessor.getD96_order_xml()
    
    def getD96_order_xml():
        resource_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'resources', 'edifact', 'D96_ORDERS.xml')
        xml_response =  EDIFACTProcessor.read_file_from_resources(resource_path)
        return EDIFACTProcessor.update_values_from_xml(xml_response)
    
    def read_file_from_resources(file_path):
        with open(file_path, 'r') as file:
            return file.read()
        
    def update_values_from_xml(xml_response):
        updates = {
            'branchId': branch_id,
            'branchName': branch_name,
            'currentVersion': 'true',
            'deleted': 'true',
            'folderFullPath': folder_path,
            'folderId': folder_id,
            'folderName': folder_path.split('/')[-1],
            'name': 'D96_ORDERS',
            'type': 'profile.edi',
            'version': '1',
        }
        return EDIFACTProcessor.update_boomi_component_attributes(xml_response, updates)

    def update_boomi_component_attributes(xml_string, updates):
        ns = {'bns': 'http://api.platform.boomi.com/'}
        ET.register_namespace('bns', ns['bns'])
        ET.register_namespace('xsi', 'http://www.w3.org/2001/XMLSchema-instance')

        root = ET.fromstring(xml_string)

        for attr, new_val in updates.items():
            if attr in root.attrib:
                root.attrib[attr] = new_val

        return ET.tostring(root, encoding='unicode')