import xml.etree.ElementTree as ET
from mappingUtility.strategy.ComponentGenerator import FileProcessor
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString
from resources.globlas import folder_id, folder_path, branch_id, branch_name, boomi_component_bns_url, boomi_component_xsi_url
import logging
from mappingUtility.Utility import XmlCleaner

logger = logging.getLogger(__name__)

class XMLProcessor(FileProcessor):
    def process(self, file_content):
        logger.info("Processing XML file content.")
        cleaned_content = XmlCleaner.generate_sample_with_all_fields_xml(file_content)
        output = XMLProcessor.generate_boomi_xml_from_xml(cleaned_content)
        logger.info("XML output generated successfully.")
        return output

    def add_data_format(parent):
        df = SubElement(parent, "DataFormat")
        SubElement(df, "ProfileCharacterFormat")


    def add_xml_attribute(parent, attr_name, key_counter):
        key_counter[0] += 1
        attr_elem = SubElement(parent, "XMLAttribute", {
            "dataType": "character", "isMappable": "true", "isNode": "true",
            "key": str(key_counter[0]), "name": attr_name,
            "required": "false", "useNamespace": "-1"
        })
        XMLProcessor.add_data_format(attr_elem)


    def process_xml_element(obj_elem, element, key_counter):
        key_counter[0] += 1
        entry = SubElement(obj_elem, "XMLElement", {
            "dataType": "character", "isMappable": "true", "isNode": "true",
            "key": str(key_counter[0]), "name": element.tag,
            "maxOccurs": "1", "minOccurs": "0", "useNamespace": "-1"
        })
        XMLProcessor.add_data_format(entry)

        for attr_name in element.attrib:
            XMLProcessor.add_xml_attribute(entry, attr_name, key_counter)

        for child in element:
            XMLProcessor.process_xml_element(entry, child, key_counter)


    def create_component_root(is_source):

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
            "type": "profile.xml", #need change
            "version": "1"
        })

        SubElement(component, "bns:encryptedValues")
        SubElement(component, "bns:description")
        return component


    def build_xml_profile_structure(component, root_element, key_counter):

        bns_object = SubElement(component, "bns:object")
        profile = SubElement(bns_object, "XMLProfile", {
            "modelVersion": "2", "strict": "true"
        })

        profile_props = SubElement(profile, "ProfileProperties")
        SubElement(profile_props, "XMLGeneralInfo")
        SubElement(profile_props, "XMLOptions", {
            "encoding": "utf8", "implicitElementOrdering": "true",
            "parseRespectMaxOccurs": "true", "respectMinOccurs": "false",
            "respectMinOccursAlways": "false"
        })

        data_elements = SubElement(profile, "DataElements")

        root = SubElement(data_elements, "XMLElement", {
            "dataType": "character", "isMappable": "true", "isNode": "true",
            "key": str(key_counter[0]), "name": root_element.tag,
            "maxOccurs": "1", "minOccurs": "1", "useNamespace": "-1"
        })
        XMLProcessor.add_data_format(root)

        for child in root_element:
            XMLProcessor.process_xml_element(root, child, key_counter)

        namespaces = SubElement(profile, "Namespaces")
        xml_namespace = SubElement(namespaces, "XMLNamespace", {
            "key": "-1", "name": "Empty Namespace"
        })
        SubElement(xml_namespace, "Types")

        SubElement(profile, "tagLists")


    def generate_boomi_xml_from_xml(xml_data, is_source=True):
        try:
            root_element = ET.fromstring(xml_data)
        except ET.ParseError as e:
            logger.error(f"❌ Failed to parse input XML: {e}")
            raise

        component = XMLProcessor.create_component_root(is_source)
        key_counter = [1]
        XMLProcessor.build_xml_profile_structure(component, root_element, key_counter)

        return parseString(tostring(component, encoding="utf-8")).toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")

