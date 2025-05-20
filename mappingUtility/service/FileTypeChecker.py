from xml.etree import ElementTree
import json
import logging

logger = logging.getLogger(__name__)

def get_file_type(file):
    try:
        filename = file.name.lower()
        if filename.endswith('.json'):
            return 'json'
        elif filename.endswith('.xml'):
            return 'xml'
        elif filename.endswith('.edi') or filename.endswith('.edifact'):
            return 'edifact'
        elif filename.endswith('.x12'):
            return 'x12'

        file.seek(0)
        content = file.read(2048).decode('utf-8').strip()
        file.seek(0)

        try:
            json.loads(content)
            return 'json'
        except json.JSONDecodeError:
            logger.error("Error detecting JSONDecodeError.")
            pass

        try:
            ElementTree.fromstring(content)
            return 'xml'
        except ElementTree.ParseError:
            logger.error("Error detecting ElementTree.ParseError.")
            pass

        if content.startswith("UNA") or content.startswith("UNB"):
            return 'edifact'

        if content.startswith("ISA"):
            return 'x12'

        return 'unknown'
    except Exception as e:
        logger.error(f"Error detecting file type: {e}")
        return 'unknown'
