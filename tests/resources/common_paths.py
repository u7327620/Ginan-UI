from importlib.resources import files

TEST_DATA_FOLDER = str(files("tests.resources.inputData").joinpath("data"))
TEST_PRODUCT_FOLDER = str(files("tests.resources.inputData").joinpath("products"))
TEST_OUTPUT_FOLDER = str(files("tests.resources").joinpath("output"))
TEST_SAMPLE_CONFIG = str(files("tests.resources").joinpath("ppp_example.yaml"))