from ruamel.yaml import YAML
from pathlib import Path

yaml = YAML() # Create the parser instance
yaml.preserve_quotes = True # Do not remove quotes around values
yaml.indent(mapping=4, sequence=4, offset=4) # Preserve indenting through the file

def update_yaml_value(file_path: str, key_path: str, new_value):
    """
    Modify a YAML key in the provided file path to a new value.

    :param file_path: The path to the YAML file to modify (e.g. "resources/ppp_example.yaml")
    :param key_path: Dotted path to the YAML key to modify (e.g. "outputs.outputs_root")
    :param new_value: The new value to modify attribute_path to (string, int, list, etc.)
    """
    path = Path(file_path)
    data = yaml.load(path.read_text()) # Create a dictionary-like structure

    # Move through the provided dotted path
    keys = key_path.split(".")
    node = data
    for k in keys[:-1]: # Iterate to the key before the one we want to edit
        if k not in node:
            raise KeyError(f"Path segment '{k}' not found in {key_path}")
        node = node[k]

    last_key = keys[-1]
    if last_key not in node:
        raise KeyError(f"Final key '{last_key}' not found in {key_path}")

    node[last_key] = new_value
    yaml.dump(data, path.open("w")) # Open file_path with write permission and dump in change
