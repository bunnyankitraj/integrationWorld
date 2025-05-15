import json
from collections import OrderedDict
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString
from mappingUtility.strategy.FileProcessor import FileProcessor
from resources.globlas import folder_id, folder_path, branch_id, branch_name, boomi_component_bns_url, boomi_component_xsi_url

class JSONProcessor(FileProcessor):
    def process(self, file_content):
        print("Processing JSON file content.")
        # Example of processing JSON data
        xml_output = JSONProcessor.generate_profile_xml(file_content)
        print("XML output generated successfully.")
        print(xml_output)
        return xml_output

    def create_component_root(is_source=True):
        component =  Element("bns:Component", {
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
            "type": "profile.json", #need change
            "version": "1"
        })
        SubElement(component, "bns:encryptedValues")
        SubElement(component, "bns:description")
        return component

    def create_root_profile_structure(component_elem):
        bns_object = SubElement(component_elem, "bns:object")
        profile = SubElement(bns_object, "JSONProfile", {"strict": "false"})
        data_elements = SubElement(profile, "DataElements")

        root = SubElement(data_elements, "JSONRootValue", {
            "dataType": "character", "isMappable": "true", "isNode": "true",
            "key": "1", "name": "Root"
        })
        SubElement(root, "DataFormat").append(Element("ProfileCharacterFormat"))

        SubElement(profile, "tagLists")

        return profile, root

    def process_object_entries(obj_elem, data, key_counter):
        for field_name, value in data.items():
            key_counter[0] += 1
            field_key = str(key_counter[0])

            entry = SubElement(obj_elem, "JSONObjectEntry", {
                "dataType": JSONProcessor.get_data_type(value),
                "isMappable": "true", "isNode": "true",
                "key": field_key, "name": field_name
            })

            df = SubElement(entry, "DataFormat")
            JSONProcessor.add_format(df, value)

            if isinstance(value, dict):
                key_counter[0] += 1
                inner_obj = SubElement(entry, "JSONObject", {
                    "isMappable": "false", "isNode": "true",
                    "key": str(key_counter[0]), "name": "Object"
                })
                JSONProcessor.process_object_entries(inner_obj, value, key_counter)

            elif isinstance(value, list):
                JSONProcessor.process_array(entry, value, key_counter)

    def process_array(parent_elem, array_value, key_counter):
        key_counter[0] += 1
        array = SubElement(parent_elem, "JSONArray", {
            "elementType": "repeating", "isMappable": "false", "isNode": "true",
            "key": str(key_counter[0]), "name": "Array"
        })

        key_counter[0] += 1
        element = SubElement(array, "JSONArrayElement", {
            "dataType": "character", "isMappable": "true", "isNode": "true",
            "key": str(key_counter[0]), "maxOccurs": "-1", "minOccurs": "0", "name": "ArrayElement1"
        })
        df = SubElement(element, "DataFormat")
        SubElement(df, "ProfileCharacterFormat")

        if array_value and isinstance(array_value[0], dict):
            key_counter[0] += 1
            inner_obj = SubElement(element, "JSONObject", {
                "isMappable": "false", "isNode": "true",
                "key": str(key_counter[0]), "name": "Object"
            })
            JSONProcessor.process_object_entries(inner_obj, array_value[0], key_counter)

    def get_data_type(value):
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, (int, float)):
            return "number"
        return "character"

    def add_format(df_elem, value):
        if isinstance(value, bool):
            return  # boolean: do not add <ProfileBooleanFormat/>
        elif isinstance(value, (int, float)):
            SubElement(df_elem, "ProfileNumberFormat", {"numberFormat": ""})
        else:
            SubElement(df_elem, "ProfileCharacterFormat")

    def generate_profile_xml(json_data, is_source=True):
        json_data = json.loads(json_data, object_pairs_hook=OrderedDict)

        component = JSONProcessor.create_component_root(is_source)
        profile, root = JSONProcessor.create_root_profile_structure(component)

        key_counter = [1]

        if isinstance(json_data, list):
            JSONProcessor.process_array(root, json_data, key_counter)
        elif isinstance(json_data, dict):
            key_counter[0] += 1
            obj = SubElement(root, "JSONObject", {
                "isMappable": "false", "isNode": "true",
                "key": str(key_counter[0]), "name": "Object"
            })
            JSONProcessor.process_object_entries(obj, json_data, key_counter)

        return parseString(tostring(component, encoding="utf-8")).toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")

    # # --------------------------- Main Entry ---------------------------

    # def main():
    #     # ✅ Raw JSON string input
    #     raw_json = '''
    #     {
    #         "Company": {
    #             "Department": {
    #                 "name": "Engineering",
    #                 "Employee": {
    #                     "ID": 101,
    #                     "Name": "John Doe",
    #                     "Role": "Software Developer",
    #                     "Salary": 80000
    #                 }
    #             }
    #         }
    #     }
    #     '''

    #     # Parse raw JSON string to OrderedDict to preserve key order

    #     xml_output = JSONProcessor.generate_profile_xml(raw_json)
    #     # xml_output = generate_profile_xml(raw_json)

    #     with open("sourceProfile.xml", "w") as f:
    #         f.write(xml_output)

    #     print("✅ Boomi XML generated successfully.")


    # if __name__ == "__main__":
    #     main()
        
