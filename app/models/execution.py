import os
import subprocess
from re import error

from app.models.yaml_utils import (load_yaml,
                                   write_yaml,
                                   full_yaml_config)


class Execution:
    def __init__(self,config_path: str, executable):


        self.config_path = config_path
        self.executable = executable
        self.config = None
        #self.config = load_yaml(config_path)

    def edit_config(self, key_path: str, value: str, add_field=False):
        """
        Edits the cached config, ensure the config is written before executing

        :param key_path: Yaml key e.g. "outputs.outputs_root"
        :param value: new Yaml value e.g. "/my/path/to/outputs"
        :param add_field: Adds field if it doesn't exist
        :raises KeyError if key not found
        """
        keys = key_path.split(".")
        node = self.config # Should be a reference
        for key in keys[:-1]: # Ensure key path validity
            if key not in node:
                raise KeyError(f"Key '{key}' not found in {node}")
            node = node[key]
        if not add_field:
            if keys[-1] not in node:
                raise KeyError(f"Key '{keys[-1]}' not found in {node}")
        node[keys[-1]] = value


    def load_config_file(self, source_path):
        self.config = load_yaml(source_path)

    def load_config_preset(self, source_path):
        self.config = full_yaml_config(self.config_path)

    def change_config_file(self, config_path):
        self.config_path = config_path

    def write_config(self):
        write_yaml(self.config_path, self.config)

    def execute_config(self):
        command = [self.executable, "--config", self.config_path]
        try:
            # Run PEA using a subprocess at the directory "config_path"
            subprocess.run(command, check=True, text=True,cwd=os.path.dirname(self.config_path))
        except subprocess.CalledProcessError as e:
            e.add_note("Error executing PEA command")
            raise e