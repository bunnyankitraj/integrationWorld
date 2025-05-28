from mappingUtility.Utility import ComponentUtils
from mappingUtility.client import BoomiApiService
from mappingUtility.service import MappingComponentXmlGenerator
from mappingUtility.strategy.JsonComponentGenerator import JSONProcessor
from mappingUtility.strategy.XmlComponentGenerator import XMLProcessor
from mappingUtility.strategy.EDIFACTComponentGenerator import EDIFACTProcessor
from mappingUtility.strategy.ComponentGeneratorContext import FileProcessingContext
import logging

logger = logging.getLogger(__name__)

def profile_component_generator(file_content,file_type):
        if file_type == 'edi' or file_type == 'EDIFACT' or file_type == 'edifact':
            strategy = EDIFACTProcessor()
        elif file_type == 'json' or file_type == 'JSON':
            strategy = JSONProcessor()
        elif file_type == 'xml' or file_type == 'XML':
            strategy = XMLProcessor()
        else:
            raise ValueError("Unsupported file type. Please provide 'json' or 'xml'.")

        context = FileProcessingContext(strategy)

        xml_response = context.execute(file_content)
        return xml_response

def process_mapping_files(source_data, destination_data, excel_data, source_file_type, destination_file_type):
    try:
        logger.info("Starting process_mapping_files execution.")
        
        sourceTempXml = profile_component_generator(source_data, source_file_type)
        sourceXml = BoomiApiService.upload_xml_component_to_boomi(sourceTempXml)
        sourceComponentId = ComponentUtils.extract_component_id(sourceXml)
        logger.info(f"Extracted source component ID: {sourceComponentId}")
        
        destinationTempXml = profile_component_generator(destination_data, destination_file_type)
        destinationXml = BoomiApiService.upload_xml_component_to_boomi(destinationTempXml)
        destinationComponentId = ComponentUtils.extract_component_id(destinationXml)
        logger.info(f"Extracted destination component ID: {destinationComponentId}")
        
        mapTempComponentXml = MappingComponentXmlGenerator.generate_boomi_map(
            excel_data,
            sourceXml,
            destinationXml,
            source_col="Source Field (Dropdown)",
            target_col="Target Field",
            from_profile_id=sourceComponentId,
            to_profile_id=destinationComponentId
        )
        logger.info("Generated Boomi map component XML.")
        
        mapComponentXml = BoomiApiService.upload_xml_component_to_boomi(mapTempComponentXml)
        logger.info("Uploaded map component.")
        
        return mapComponentXml

    except Exception as e:
        logger.error(f"An error occurred during process_mapping_files execution: {e}")
        raise
