import json


def generate_generic_json(json_content):
    try:
        data = json.loads(json_content)

        if isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list):
            raise ValueError(
                f"Input JSON must be an array of objects or a single object. Received type: {type(data).__name__}."
            )

        sample_object = {}
        for obj in data:
            if isinstance(obj, dict):
                _merge_fields(sample_object, obj)
            else:
                raise ValueError("Each item in the JSON array must be an object.")

        return json.dumps(sample_object, indent=4)

    except json.JSONDecodeError:
        raise ValueError("Invalid JSON content provided.")


def _merge_fields(target, source):
    for key, value in source.items():
        if isinstance(value, dict):
            target[key] = target.get(key, {})
            _merge_fields(target[key], value)
        elif isinstance(value, list):
            if key not in target:
                target[key] = []
            if value:
                if isinstance(value[0], dict):
                    sample_item = {}
                    for item in value:
                        if isinstance(item, dict):
                            _merge_fields(sample_item, item)
                    target[key] = [sample_item]
                else:
                    target[key] = [value[0]]
        else:
            target[key] = value
