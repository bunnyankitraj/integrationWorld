from mappingUtility.service import BoomiComponentUploader,  MapComponentXMLgenerator, ProfileCreator,ComponentService;


def process_mapping_files(source_data, destination_data, excel_data):
    try:
        print("Starting process_mapping_files execution.")
        
        sourceTempXml = ProfileCreator.generate_xml(source_data)
        sourceXml = BoomiComponentUploader.upload_component(sourceTempXml)
        sourceComponentId = ComponentService.extract_component_id(sourceXml)
        print(f"Extracted source component ID: {sourceComponentId}")
        
        destinationTempXml = ProfileCreator.generate_xml(destination_data)
        destinationXml = BoomiComponentUploader.upload_component(destinationTempXml)
        destinationComponentId = ComponentService.extract_component_id(destinationXml)
        print(f"Extracted destination component ID: {destinationComponentId}")
        
        mapTempComponentXml = MapComponentXMLgenerator.generate_boomi_map(
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
