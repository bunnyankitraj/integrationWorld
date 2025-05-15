from xml.etree import ElementTree
import json

def get_file_type(file):
    try:
        print("Detecting file type...")
        filename = file.name.lower()
        if filename.endswith('.json'):
            return 'json'
        elif filename.endswith('.xml'):
            return 'xml'

        file.seek(0)
        content = file.read(2048).decode('utf-8').strip()
        file.seek(0)

        try:
            json.loads(content)
            return 'json'
        except json.JSONDecodeError:
            pass

        try:
            ElementTree.fromstring(content)
            return 'xml'
        except ElementTree.ParseError:
            pass

        return 'unknown'
    except Exception:
        return 'unknown'
