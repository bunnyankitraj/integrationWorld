import logging
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString
from mappingUtility.strategy.ComponentGenerator import FileProcessor
from resources.globlas import folder_id, folder_path, branch_id, branch_name, boomi_component_bns_url, boomi_component_xsi_url
import os


logger = logging.getLogger(__name__)


class EDIFACTProcessor(FileProcessor):
    def process(self, file_content):
        logger.info("Processing EDIFACT file content.")
        # edifact_segments = EDIFACTProcessor.parse_edifact(file_content)
        # xml_output = EDIFACTProcessor.generate_profile_xml(edifact_segments)
        # logger.info("XML output generated successfully.")
        return EDIFACTProcessor.getD96_order_xml()
    
    def getD96_order_xml():
        resource_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'resources', 'D96_ORDERS.xml')
        return EDIFACTProcessor.read_file_from_resources(resource_path)
    
    def read_file_from_resources(file_path):
        with open(file_path, 'r') as file:
            return file.read()
        
    def create_component_root(is_source=True):
        component = Element("bns:Component", {
            "xmlns:bns": boomi_component_bns_url,
            "xmlns:xsi": boomi_component_xsi_url,
            "branchId": branch_id,
            "branchName": branch_name,
            "currentVersion": "true",
            "deleted": "false",
            "folderFullPath": folder_path,
            "folderId": folder_id,
            "folderName": folder_path.split("/")[-1],
            "name": "sourceProfile" if is_source else "destinationProfile",
            "type": "profile.edi",  # Updated type for EDIFACT
            "version": "1"
        })
        SubElement(component, "bns:encryptedValues")
        SubElement(component, "bns:description")
        return component

    def create_root_profile_structure(component_elem):
        bns_object = SubElement(component_elem, "bns:object")
        profile = SubElement(bns_object, "EDIFACTProfile", {"strict": "false"})
        data_elements = SubElement(profile, "DataElements")

        root = SubElement(data_elements, "EDIFACTRootSegment", {
            "dataType": "character", "isMappable": "true", "isNode": "true",
            "key": "1", "name": "Root"
        })
        SubElement(root, "DataFormat").append(Element("ProfileCharacterFormat"))

        SubElement(profile, "tagLists")

        return profile, root

    def process_segments(segment_elem, segments, key_counter):
        for segment in segments:
            key_counter[0] += 1
            segment_key = str(key_counter[0])

            entry = SubElement(segment_elem, "EDIFACTSegment", {
                "dataType": "character",
                "isMappable": "true", "isNode": "true",
                "key": segment_key, "name": segment["name"]
            })

            df = SubElement(entry, "DataFormat")
            SubElement(df, "ProfileCharacterFormat")

            if "elements" in segment:
                EDIFACTProcessor.process_elements(entry, segment["elements"], key_counter)

    def process_elements(parent_elem, elements, key_counter):
        for element in elements:
            key_counter[0] += 1
            element_key = str(key_counter[0])

            entry = SubElement(parent_elem, "EDIFACTElement", {
                "dataType": "character",
                "isMappable": "true", "isNode": "true",
                "key": element_key, "name": element
            })
            df = SubElement(entry, "DataFormat")
            SubElement(df, "ProfileCharacterFormat")

    def parse_edifact(file_content):
        segments = []
        for line in file_content.splitlines():
            if line.strip():
                parts = line.split("+")
                segment_name = parts[0]
                elements = parts[1:] if len(parts) > 1 else []
                segments.append({"name": segment_name, "elements": elements})
        return segments

    def generate_profile_xml(edifact_segments, is_source=True):
        component = EDIFACTProcessor.create_component_root(is_source)
        profile, root = EDIFACTProcessor.create_root_profile_structure(component)

        key_counter = [1]
        EDIFACTProcessor.process_segments(root, edifact_segments, key_counter)

        return parseString(tostring(component, encoding="utf-8")).toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")
