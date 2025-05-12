from mappingUtility.service import BoomiComponentUploader,  mapComponentXMLgenerator, profileCreator,ComponentService;
import tempfile
import os

def process_files(source_data, destination_data, excel_data):

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_excel:
        temp_excel.write(excel_data)
        excel_path = temp_excel.name

    try:
        sourceTempXml = ProfileCreator.generate_xml(source_data)
        sourceXml = BoomiComponentUploader.upload_component(sourceTempXml)
        sourceComponentId = ComponentService.extract_component_id(sourceXml)
        
        destinationTempXml = ProfileCreator.generate_xml(destination_data)
        destinationXml = BoomiComponentUploader.upload_component(destinationTempXml)
        destinationComponentId = ComponentService.extract_component_id(destinationXml)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as temp_source_xml:
            temp_source_xml.write(sourceXml.encode('utf-8'))
            source_xml_path = temp_source_xml.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as temp_destination_xml:
            temp_destination_xml.write(destinationXml.encode('utf-8'))
            destination_xml_path = temp_destination_xml.name

        mapTempComponentXml = MapComponentXMLgenerator.generate_boomi_map(
            excel_path=excel_path,
            source_component_xml_path=source_xml_path,
            target_component_xml_path=destination_xml_path,
            source_col="Source Field (Dropdown)",
            target_col="Target Field",
            from_profile_id=sourceComponentId,
            to_profile_id=destinationComponentId
        )
        
        mapComponentXml = BoomiComponentUploader.upload_component(mapTempComponentXml)
        return mapComponentXml

    finally:
        # Clean up all temporary files
        for path in [source_xml_path, destination_xml_path, excel_path]:
            if os.path.exists(path):
                os.remove(path)
