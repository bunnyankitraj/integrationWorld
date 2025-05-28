import logging
import re
import xml.etree.ElementTree as ET
from io import BytesIO
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

import pandas as pd

from resources.globlas import (boomi_component_bns_url,
                               boomi_component_xsi_url, branch_id, branch_name,
                               folder_id, folder_path, map_name)

logger = logging.getLogger(__name__)


def extract_paths_from_json_profile(profile_xml_content):
    try:
        logger.info(f"Parsing XML content from provided string")
        root = ET.fromstring(profile_xml_content)
        logger.info(f"Successfully parsed XML content")
    except Exception as e:
        logger.error(f"Error parsing XML content: {e}")
        return {}

    mappings = {}
    for child in root:
        traverse_and_extract_mappings(child, "", "", mappings)

    logger.info(f"Extracted {len(mappings)} field mappings from profile XML")
    return mappings


def extract_main_node(parent_path):
    parts = parent_path.split("/")

    filtered_parts = [
        part
        for part in parts
        if part not in ["Root", "Object", "Array"]
        and not re.match(r"ArrayElement\d*$", part)
    ]

    return "/".join(filtered_parts) if filtered_parts else ""


def traverse_and_extract_mappings(element, parent_name_path, parent_key_path, mappings):
    is_mappable = element.get("isMappable") == "true"
    element_name = element.get("name")
    element_key = element.get("key")

    current_name_path = parent_name_path
    current_key_path = parent_key_path

    if element_name:
        current_name_path = (
            f"{current_name_path}/{element_name}" if current_name_path else element_name
        )

    if element_key:
        key_part = f"*[@key='{element_key}']"
        current_key_path = (
            f"{current_key_path}/{key_part}" if current_key_path else key_part
        )

    filtered_parent_path = extract_main_node(current_name_path)

    if is_mappable and element_name and element_key:
        mappings[filtered_parent_path] = {
            "name_path": current_name_path,
            "key_path": current_key_path,
        }
        # logger.info(f"Found field: {element_name} -> {current_name_path} ({current_key_path})")

    for child in element:
        traverse_and_extract_mappings(
            child, current_name_path, current_key_path, mappings
        )


def normalize_field_name(field_name):
    field_name = re.sub(r"\[\*\]", "", field_name).lstrip("/").strip()

    # Handle dot-separated input
    if "." in field_name and "/" not in field_name:
        parts = field_name.split(".")

        # Check if the last two parts form something like "GIR04.3"
        if (
            len(parts) >= 2
            and re.match(r"^\d+$", parts[-2][-2:])
            and re.match(r"^\d+$", parts[-1])
        ):
            # Combine last two parts with dot, others with slash
            new_last = parts[-2] + "." + parts[-1]
            return "/".join(parts[:-2] + [new_last])
        else:
            return "/".join(parts)

    return field_name


def extract_final_key(path):
    matches = re.findall(r"\[@key='(\d+)'\]", path)
    return matches[-1] if matches else None


def create_boomi_component():
    component = Element(
        "bns:Component",
        {
            "xmlns:bns": boomi_component_bns_url,
            "xmlns:xsi": boomi_component_xsi_url,
            "branchId": branch_id,
            "branchName": branch_name,
            "currentVersion": "true",
            "deleted": "false",
            "folderFullPath": folder_path,
            "folderId": folder_id,
            "folderName": folder_path.split("/")[-1],
            "name": map_name,
            "type": "transform.map",
            "version": "1",
        },
    )

    SubElement(component, "bns:encryptedValues")
    SubElement(component, "bns:description").text = f"Auto-generated field mapping"
    return component


def generate_boomi_map(
    excel_data,
    source_component_xml_path,
    target_component_xml_path,
    source_col,
    target_col,
    from_profile_id,
    to_profile_id,
):
    try:
        logger.info(f"Reading Excel file from uploaded content")
        df = pd.read_excel(BytesIO(excel_data), sheet_name="Field Mapping")
        df = df[[target_col, source_col]].dropna()
        logger.info(f"Found {len(df)} mapping entries in Excel")
    except Exception as e:
        logger.error(f"Error reading Excel file: {e}")
        return None

    # logger.info(f"Processing source component XML: {source_component_xml_path}")
    source_mappings = extract_paths_from_json_profile(source_component_xml_path)
    logger.info(f"Found {len(source_mappings)} mappings in source component XML")
    # logger.info(f"Source mappings: {source_mappings}")

    # logger.info(f"Processing target component XML: {target_component_xml_path}")
    target_mappings = extract_paths_from_json_profile(target_component_xml_path)
    logger.info(f"Found {len(target_mappings)} mappings in target component XML")
    # logger.info(f"Target mappings: {target_mappings}")

    if not source_mappings:
        logger.warning("Warning: No mappings found in source component XML")
    if not target_mappings:
        logger.warning("Warning: No mappings found in target component XML")

    component = create_boomi_component()
    obj = SubElement(component, "bns:object")
    map_ = SubElement(
        obj, "Map", {"fromProfile": from_profile_id, "toProfile": to_profile_id}
    )

    mappings_element = SubElement(map_, "Mappings")

    successful_mappings = 0
    for _, row in enumerate(df.itertuples(index=False), 1):
        target_field, source_field = row
        source_field_name = normalize_field_name(source_field)
        target_field_name = normalize_field_name(target_field)

        # logger.info(f"Processing mapping: {source_field} -> {target_field}")
        # logger.info(f"Normalized: {source_field_name} -> {target_field_name}")
        if not source_field_name or not target_field_name:
            logger.warning(
                f"⚠️ Skipping empty mapping: {source_field} -> {target_field}"
            )

        source_info = source_mappings.get(source_field_name)
        target_info = target_mappings.get(target_field_name)

        if not source_info:
            for field, info in source_mappings.items():
                if field.endswith(source_field_name):
                    source_info = info
                    break

        if not target_info:
            for field, info in target_mappings.items():
                if field.endswith(target_field_name):
                    target_info = info
                    break

        if not source_info:
            logger.warning(f"Source mappings available: {len(source_mappings)} entries")
            logger.warning(
                f"⚠️ Warning: No mapping found for source field: {source_field} (Normalized: {source_field_name}, Info: {source_info})"
            )
            continue
        if not target_info:
            logger.warning(
                f"⚠️ Warning: No mapping found for target field: {target_field}"
            )
            logger.warning(f"Target mappings available: {len(target_mappings)} entries")
            continue

        from_key = extract_final_key(source_info["key_path"])
        to_key = extract_final_key(target_info["key_path"])

        if not from_key or not to_key:
            logger.warning(
                f"⚠️ Skipping mapping due to missing key in path: {source_field} -> {target_field}"
            )
            continue

        mapping_attrs = {
            "fromKey": from_key,
            "fromKeyPath": source_info["key_path"],
            "fromNamePath": source_info["name_path"],
            "fromType": "profile",
            "toKey": to_key,
            "toKeyPath": target_info["key_path"],
            "toNamePath": target_info["name_path"],
            "toType": "profile",
        }

        SubElement(mappings_element, "Mapping", mapping_attrs)
        successful_mappings += 1
        logger.info(
            f"✓ Added mapping: {source_info['name_path']} -> {target_info['name_path']}"
        )

    SubElement(map_, "Functions", {"optimizeExecutionOrder": "true"})
    SubElement(map_, "Defaults")
    SubElement(map_, "DocumentCacheJoins")

    xml_str = minidom.parseString(tostring(component)).toprettyxml(indent="  ")

    logger.info(
        f"✅ Successfully created {successful_mappings} field mappings out of {len(df)} total."
    )
    return xml_str


if __name__ == "__main__":
    logger.info("Starting Boomi mapping generation script...")

    xml_output = generate_boomi_map(
        excel_data="AI_Field_Mapping.xlsx",
        source_component_xml_path="sourceProfile.xml",
        target_component_xml_path="destinationProfile.xml",
        source_col="Source Field (Dropdown)",
        target_col="Target Field",
        from_profile_id="273c6754-54ba-4c54-ae6b-566d82e407e1",
        to_profile_id="273c6754-54ba-4c54-ae6b-566d82e407e1",
    )

    if xml_output:
        output_path = "generated_boomi_map.xml"
        with open(output_path, "w") as f:
            f.write(xml_output)
        logger.info(f"✅ Boomi XML generated successfully at {output_path}")
    else:
        logger.error("❌ Failed to generate Boomi XML")
