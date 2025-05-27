import xml.etree.ElementTree as ET
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


def load_segment_structure_from_xml(xml_content):
    if isinstance(xml_content, str):
        xml_content = ET.ElementTree(ET.fromstring(xml_content))
    root = xml_content.getroot()

    segment_structure = {}

    def process_element(elem, path_stack):
        tag = elem.tag.split('}')[-1]

        if tag == 'EdiLoop':
            loop_name = elem.attrib.get('name', 'UnknownLoop')
            path_stack.append(loop_name)
            for child in elem:
                process_element(child, path_stack)
            path_stack.pop()

        elif tag == 'EdiSegment':
            segment_name = elem.attrib.get('name')
            if not segment_name:
                logger.warning(f"Skipping EdiSegment with no name in XML: {ET.tostring(elem, encoding='unicode')}")
                return

            # Build path from stack
            segment_path = '/'.join(path_stack + [segment_name])

            fields = []
            for data_elem in elem.findall(".//"):
                sub_tag = data_elem.tag.split('}')[-1]
                if sub_tag == 'EdiDataElement':
                    name = data_elem.attrib.get('name')
                    if name:
                        fields.append(name)

            segment_structure[segment_name] = {
                'path': segment_path,
                'fields': fields
            }

    # Start processing from DataElements
    data_elements = root.find(".//DataElements")
    if data_elements is not None:
        for top_level_elem in data_elements:
            process_element(top_level_elem, path_stack=[])

    return segment_structure


def extract_segment_names_from_edifact(edifact_message):
    segments = edifact_message.strip().split("'")
    return {seg.split('+')[0].strip() for seg in segments if seg.strip()}


def parse_segment_line(segment_line, segment_fields):
    """
    segment_line: raw EDIFACT segment line, e.g. "BGM+220::6365+12345+9"
    segment_fields: list of field names from XML for this segment, e.g.
      ['BGM01', 'BGM01.1', 'BGM01.2', 'BGM01.3', 'BGM02', 'BGM03']

    Returns dict of field_name -> value (only if field_name in segment_fields)
    """
    parts = segment_line.split('+')
    segment_name = parts[0]

    field_data = {}
    # elements start from BGM01 -> parts[1] is BGM01, parts[2] is BGM02, etc.
    for idx, element_value in enumerate(parts[1:], start=1):
        field_base = f"{segment_name}{idx:02d}"  # e.g. BGM01, BGM02
        # Check if element_value has subcomponents
        subcomponents = element_value.split(':')
        if len(subcomponents) > 1:
            # Multiple subcomponents
            for sub_idx, sub_val in enumerate(subcomponents, start=1):
                field_name = f"{field_base}.{sub_idx}"  # e.g. BGM01.1, BGM01.2
                if field_name in segment_fields:
                    field_data[field_name] = sub_val
        else:
            # Single component
            if field_base in segment_fields:
                field_data[field_base] = element_value

    return field_data


def generate_all_fields_for_used_segments(xml_content, edifact_message):
    segment_structure = load_segment_structure_from_xml(xml_content)

    logger.info("Loaded segments from XML:")
    # for s, v in segment_structure.items():
    #     logger.info(f"  {s}: {v['path']} ({len(v['fields'])} fields)")

    if isinstance(edifact_message, bytes):
        edifact_message = edifact_message.decode('utf-8')
        
    segments_lines = [seg.strip() for seg in edifact_message.strip().split("'") if seg.strip()]
    logger.info("Segments found in EDIFACT message:")
    # for s in segments_lines:
    #     logger.info(f"  {s}")

    all_segments_data = defaultdict(list)  # key=segment_name, value=list of dicts of fields

    for segment_line in segments_lines:
        segment_line = segment_line.strip()
        if not segment_line:
            continue

        segment_name = segment_line.split('+')[0].strip()
        if segment_name not in segment_structure:
            logger.error(f"[SKIPPED] Segment '{segment_name}' not found in XML structure")
            continue

        segment_info = segment_structure[segment_name]
        segment_path = segment_info['path']
        segment_fields = segment_info['fields']

        parsed_fields = parse_segment_line(segment_line, segment_fields)

        # Store parsed fields dict for this occurrence
        all_segments_data[segment_name].append(parsed_fields)

        # for field_name, value in parsed_fields.items():
        #     full_path = f"{segment_path}/{field_name}"
        #     logger.info(f"[OK] {full_path} = {value}")

    return all_segments_data

def info_fields_with_full_path(paths_with_values, segment_structure):
    for segment_name, occurrences in paths_with_values.items():
        segment_path = segment_structure[segment_name]['path']
        for i, occurrence in enumerate(occurrences, 1):
            # logger.info a blank line between occurrences except the first
            # if i > 1:
            #     logger.info()
            for field_name, value in occurrence.items():
                full_path = f"{segment_path}/{field_name}"
                logger.info(f"{full_path} = {value}")


def get_flat_field_path_list(paths_with_values, segment_structure, edifact_message):
    if isinstance(edifact_message, bytes):
        edifact_message = edifact_message.decode('utf-8')
    segments_in_order = [seg.split('+')[0].strip() for seg in edifact_message.strip().split("'") if seg.strip()]
    seen_paths = set()
    flat_list = []

    for segment_name in segments_in_order:
        if segment_name not in paths_with_values:
            continue
        occurrences = paths_with_values[segment_name]
        segment_path = segment_structure[segment_name]['path']
        for occurrence in occurrences:
            for field_name in occurrence:
                full_path = f"{segment_path}/{field_name}"
                if full_path not in seen_paths:
                    seen_paths.add(full_path)
                    flat_list.append(full_path)
    return flat_list


def get_edifact_fields(xml_content, edifact_content):

    logger.info("Parsing EDIFACT message and matching fields:")
    segment_structure = load_segment_structure_from_xml(xml_content)
    paths_with_values = generate_all_fields_for_used_segments(xml_content, edifact_content)

    logger.info("Final field paths with values:")
    # info_fields_with_full_path(paths_with_values, segment_structure)

    logger.info("Flattened field path list (CSV format):")
    flat_list = get_flat_field_path_list(paths_with_values, segment_structure, edifact_content)
    return flat_list

if __name__ == "__main__":
    xml_file = "/Users/ankit.raj/Developer/django-project/integrationWorld/resources/D96_ORDERS.xml"
    edifact_sample = """UNH+1+ORDERS:D:96A:UN'
BGM+220::6365+12345+9'
DTM+137:20240301:102'
NAD+BY+CUST001::91'
NAD+ST+123 Main St+New York++10001'
CUX+2:USD'
MOA+9:250.00'
UNT+7+1'"""
    xml_content = ET.parse(xml_file)

    get_edifact_fields(xml_content, edifact_sample)