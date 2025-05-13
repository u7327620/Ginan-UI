from ruamel.yaml import YAML
from pathlib import Path
from yaml_configs import (load_yaml_config, full_yaml_config)

yaml = YAML() # Create the parser instance
yaml.preserve_quotes = True # Do not remove quotes around values
yaml.indent(mapping=4, sequence=4, offset=4) # Preserve indenting through the file

def load_yaml(file_path: str) -> dict:
    """
    Load a YAML file and return its contents as a dictionary-like structure.

    :param file_path: The path to the YAML file to load (e.g. "/data/resources/ppp_example.yaml")
    :return: Dictionary-like structure containing the contents of the YAML file.
    """
    path = Path(file_path)
    data = yaml.load(path.read_text()) # Create a dictionary-like structure
    return data

def write_yaml(file_path: str, config: dict):
    """
        Save a built configurations as a YAML file.
        :param file_path: The path to the YAML file to save (e.g. "/data/resources/output.yaml")
        :param config: Dictionary-like structure containing the contents of the YAML file.
        :return: Dictionary-like structure containing the contents of the YAML file.
    """
    path = Path(file_path)
    yaml.dump(config, path.open('w'))

def get_key_path(key_path: str) -> list[str]:
    """
    Helper string split function
    :param key_path: Yaml key path e.g. "outputs.outputs_root"
    :return: Yaml key path as list e.g. ["outputs"]["outputs_root"]
    """
    return key_path.split('.')

def modify_yaml_field(config: dict, update:tuple[str,str]):
    """
    Given cached config file it will modify the file and list of return update type
    :param config: Yaml dictionary to modify fields to.
    :update: tuple[str,str]: tuple string input of yaml where [yaml_path,value]
    """
    #config root
    node = config
    key_path, new_value = update
    keys = get_key_path(key_path)
    for key in keys[0:len(keys)-1]:
        if not key in node:
            #path doesn't exist so will add it to the yaml
            node[key] = dict()
        node = node[key]
    node[keys[-1]] = new_value

def modify_yaml_file(config: dict, updates: list[tuple[str,str]]):
    """
    Given cached config file it will modify the file and list of return update type
    :param config: Yaml dictionary to modify fields to.
    :param updates: list of updates to apply.
    :update: tuple[str,str]: tuple string input of yaml where [yaml_path,value]
    """
    for update in updates:
        modify_yaml_field(config, update)


def load_full_yaml_file(preset:str):
    """
    Given preset name it will load the full preset e.g "ppp_example" will return a dictionary representing the ppp_example yaml file.
    :param preset: Preset name e.g. "ppp_example"
    :return: Dictionary-like structure containing the contents of the YAML file.
    """
    # Will return a hard copy as I want the configurations to be immutable
    return full_yaml_config(preset).copy()



def load_yaml_preset_configs(presets: list[tuple[list[str],str]]) -> dict:
    """
    Given preset config options will return a list of tuples where [yaml_path,value]
    :param presets: List of preset options e.g. [(["processing_options","process_modes"],preset_1)] to load the preset
    :return: dictionary representation of selected yaml configs
    """
    if presets is None:
        # Note
        # if working on scrum 44 child tasks I would modify this
        # into something like satellite_option_1
        presets = ["default"]

    yaml_config = {}
    for preset in presets:
        load_yaml_config(preset)


    raise NotImplementedError



if __name__ == "__main__":
    if(False):
        test = {}
        print(test)
        print(get_key_path("hi.hi"))
        modify_yaml_field(test,("hi.hi","wow"))
        print(test)

    if(False):
        test = {}
        modifications = [("1.1","1wow"),("1.2","2wow"),("hello","")]
        modify_yaml_file(test,modifications)
        print(test)

    test = load_full_yaml_file("ppp_example")
    print(test)
    test = load_yaml("./test/ppp_example.yaml")
    print(test)

    pass

