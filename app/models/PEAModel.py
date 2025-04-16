import os


class PEAModel:
    """Executes PEA and maintains the configuration for the PEA model."""
    def __init__(self, input_path: str, output_path: str, config_path: str):
        self.input_path = input_path
        self.output_path = output_path
        self.config_path = config_path
        self.verify_path(self.input_path, readable=True, non_empty=True, directory=True)
        self.verify_path(self.output_path, writable=True, directory=True)
        self.verify_path(self.config_path, readable=True)

    def __str__(self):
        return (f"PEAModel:\n"
                f"- input path: {self.input_path},\n"
                f"- output path: {self.output_path},\n"
                f"- config path: {self.config_path}")

    @staticmethod
    def verify_path(path: str, readable: bool=False, writable: bool=False, non_empty=False, directory=False):
        """
        Verifies a given path.

        :param path: Path to verify.
        :param readable: Check if the path is readable (default=False).
        :param writable: Check if the path is writable (default=False).
        :param non_empty: Check if the path is non-empty (default=False).
        :param directory: Check if the path is a directory (default=False).
        """
        if not os.path.exists(path):
            raise ValueError(f"Input path does not exist: {path}")
        if directory:
            if not os.path.isdir(path):
                raise ValueError(f"Input path is not a directory: {path}")
        if readable:
            if not os.access(path, os.R_OK):
                raise ValueError(f"Input path is not readable: {path}")
        if writable:
            if not os.access(path, os.W_OK):
                raise ValueError(f"Input path is not writable: {path}")
        if non_empty:
            if not os.listdir(path):
                raise ValueError(f"Input path is empty: {path}")

    def executeConfig(self):
        print("Executing " + self.__str__())
        