from mappingUtility.service import BoomiComponentUploader,MappingComponentXmlGenerator, ComponentService,FileTypeChecker
import json
from mappingUtility.strategy.JSONProcessor import JSONProcessor
from mappingUtility.strategy.XMLProcessor import XMLProcessor
from mappingUtility.strategy.FileProcessingContext import FileProcessingContext
from mappingUtility.strategy.FileProcessor import FileProcessor

def process_json_file(file_content,file_type):
        if file_type == 'json' or file_type == 'JSON':
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
        print("Starting process_mapping_files execution.")
        
        sourceTempXml = process_json_file(source_data, source_file_type)
        sourceXml = BoomiComponentUploader.upload_component(sourceTempXml)
        sourceComponentId = ComponentService.extract_component_id(sourceXml)
        print(f"Extracted source component ID: {sourceComponentId}")
        
        destinationTempXml = process_json_file(destination_data, destination_file_type)
        destinationXml = BoomiComponentUploader.upload_component(destinationTempXml)
        destinationComponentId = ComponentService.extract_component_id(destinationXml)
        print(f"Extracted destination component ID: {destinationComponentId}")
        
        mapTempComponentXml = MappingComponentXmlGenerator.generate_boomi_map(
            excel_data,
            sourceXml,
            destinationXml,
            source_col="Source Field (Dropdown)",
            target_col="Target Field",
            from_profile_id=sourceComponentId,
            to_profile_id=destinationComponentId
        )
        print("Generated Boomi map component XML.")
        
        mapComponentXml = BoomiComponentUploader.upload_component(mapTempComponentXml)
        print("Uploaded map component.")
        
        return mapComponentXml

    except Exception as e:
        print(f"An error occurred during process_mapping_files execution: {e}")
        raise
