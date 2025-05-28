import xml.etree.ElementTree as ET
from copy import deepcopy
from collections import defaultdict

def merge_elements(elem1, elem2):
    merged = deepcopy(elem1)
    tag_to_elements = defaultdict(list)

    for child in merged:
        tag_to_elements[child.tag].append(child)

    for child in elem2:
        matches = tag_to_elements.get(child.tag)
        if matches:
            if len(matches) == 1 and len(list(matches[0])) == 0 and len(list(child)) == 0:
                # Leaf node, merge text
                if matches[0].text != child.text:
                    matches[0].text = matches[0].text or ""
                    matches[0].text += f"|{child.text}"
            elif len(matches) == 1 and list(matches[0]):
                # Nested structure: merge child elements
                merge_child = matches[0]
                for grandchild in child:
                    merge_child.append(deepcopy(grandchild))
            else:
                # Multiple matches or complex case: append
                merged.append(deepcopy(child))
        else:
            merged.append(deepcopy(child))

    return merged

def generate_sample_with_all_fields_xml(xml_string):
    root = ET.fromstring(xml_string)
    if len(root) == 0:
        return xml_string

    merged = deepcopy(root[0])
    for child in root[1:]:
        merged = merge_elements(merged, child)

    new_root = ET.Element(root.tag)
    new_root.append(merged)
    return ET.tostring(new_root, encoding='unicode')

# # Example input
# xml_input = '''
# <students>
#     <student>
#         <name>John Doe</name>
#         <subjects>
#             <subject>Mathematics</subject>
#             <subject>Science</subject>
#         </subjects>
#     </student>
#     <student>
#         <name>Jane Smith</name>
#         <subjects>
#             <subject>History</subject>
#             <subject>English</subject>
#         </subjects>
#     </student>
# </students>
# '''

# # Run the function
# merged_xml = generate_sample_with_all_fields_xml(xml_input)
# print(merged_xml)
