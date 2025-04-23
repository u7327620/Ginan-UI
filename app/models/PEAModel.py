import os
import subprocess

class PEAModel:
    """Executes PEA and maintains the configuration for the PEA model."""
    def __init__(self, config_path: str):
        self.config_path = config_path

    def __str__(self):
        return (f"PEAModel:\n"
                f"- config path: {self.config_path}")

    def execute_config(self):
        """
        Executes PEA using the provided file paths from __init__.
        PEA is executed from the config_path directory

        :param self: Reference to self
        """
        print("Executing " + self.__str__())

        # Concatenate the PEA command
        command = ["pea", "--config", self.config_path]

        try:
            # Run PEA using a subprocess at the directory "config_path"
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                    cwd=os.path.dirname(self.config_path)
            )
            print("PEA output:\n" + result.stdout)
            if result.stderr:
                print("PEA errors:\n" + result.stderr)

        # Error handling for outputting PEAModel and PEA errors
        except subprocess.CalledProcessError as e:
            print("PEA execution failed with error code", e.returncode)
            print("PEA stderr:\n" + e.stderr)
            print("PEA stdout (if any):\n" + e.stdout)
            raise