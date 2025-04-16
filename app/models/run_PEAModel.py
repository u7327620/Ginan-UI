from PEAModel import PEAModel

model = PEAModel(
    input_data_path="/data/ginan/inputData/data",
    input_products_path="/data/ginan/inputData/products",
    output_path="/data/ginan/exampleConfigs/outputs",
    config_path="/data/ginan/exampleConfigs/ppp_example.yaml"
)

model.executeConfig()