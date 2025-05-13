def load_yaml_config(config: tuple[list[str],str]):
    """
    Function that loads selected yaml configs into dict
    :param configs: list of tuples with input of [field, preset] e.g. ["inputs_configs","default"]
    :return: dictionary of preset options
    """
    fields = {
        "inputs_configs": inputs_configs,
        "outputs_configs:": inputs_configs,
        "satellite_configs": satellite_configs,
    }

    field, preset = config
    #field doesn't exist
    if not(field in fields):
        raise Exception(f"yaml_configs {field} doesn't exist ")

    # internal function to apply functions inside of dictionary
    def process(process_field, process_sub_field, process_preset):
        return process_field(process_sub_field, process_preset)
    #loads in yaml config for that set of configurations.
    yaml_config = process(fields.get(field[0]),
                     field,
                     preset)

    return yaml_config

def full_yaml_config(preset: str):
    """
    will have to be removed when working on scrum 42
    currently will just return dictionary representation of example_ppp.yaml
    """
    field_full_config = { "ppp_example":{'inputs': {'inputs_root': './products/', 'atx_files': ['igs20.atx'], 'igrf_files': ['tables/igrf13coeffs.txt'], 'erp_files': ['finals.data.iau2000.txt'], 'planetary_ephemeris_files': ['tables/DE436.1950.2050'], 'troposphere': {'gpt2grid_files': ['tables/gpt_25.grd']}, 'tides': {'ocean_tide_loading_blq_files': ['tables/OLOAD_GO.BLQ'], 'atmos_tide_loading_blq_files': ['tables/ALOAD_GO.BLQ'], 'ocean_pole_tide_loading_files': ['tables/opoleloadcoefcmcor.txt']}, 'snx_files': ['igs_satellite_metadata.snx', 'tables/sat_yaw_bias_rate.snx', 'tables/qzss_yaw_modes.snx', 'tables/bds_yaw_modes.snx', 'IGS1R03SNX_20191950000_07D_07D_CRD.SNX'], 'satellite_data': {'clk_files': ['IGS2R03FIN_20191990000_01D_30S_CLK.CLK'], 'bsx_files': ['IGS2R03FIN_20191990000_01D_01D_OSB.BIA'], 'sp3_files': ['IGS2R03FIN_20191990000_01D_05M_ORB.SP3']}, 'gnss_observations': {'gnss_observations_root': '../data/', 'rnx_inputs': ['ALIC00AUS_R_20191990000_01D_30S_MO.rnx']}}, 'outputs': {'metadata': {'config_description': 'ppp_example_<BRANCH>'}, 'outputs_root': './outputs/<CONFIG>', 'gpx': {'output': True, 'filename': '<RECEIVER>_<CONFIG>_<YYYY><DDD><HH>.GPX'}, 'pos': {'output': True, 'filename': '<RECEIVER>_<CONFIG>_<YYYY><DDD><HH>.POS'}, 'trace': {'level': 2, 'output_receivers': True, 'output_network': True, 'receiver_filename': '<RECEIVER>_<CONFIG>_<YYYY><DDD><HH>.TRACE', 'network_filename': '<RECEIVER>_<CONFIG>_<YYYY><DDD><HH>.TRACE', 'output_residuals': True, 'output_residual_chain': True, 'output_config': True, 'output_initialised_states': True, 'output_predicted_states': True}}, 'satellite_options': {'global': {'error_model': 'ELEVATION_DEPENDENT', 'code_sigma': 0, 'phase_sigma': 0, 'models': {'phase_bias': {'enable': False}}}}, 'receiver_options': {'global': {'elevation_mask': 15, 'error_model': 'ELEVATION_DEPENDENT', 'code_sigma': 0.3, 'phase_sigma': 0.003, 'clock_codes': ['AUTO', 'AUTO'], 'zero_dcb_codes': ['AUTO', 'AUTO'], 'rec_reference_system': 'GPS', 'models': {'phase_bias': {'enable': False}, 'troposphere': {'enable': True, 'models': ['gpt2']}, 'tides': {'atl': True, 'enable': True, 'opole': True, 'otl': True, 'solid': True, 'spole': True}}}}, 'processing_options': {'process_modes': {'preprocessor': True, 'spp': True, 'ppp': True, 'ionosphere': False, 'slr': False}, 'epoch_control': {'epoch_interval': 30, 'wait_next_epoch': 3600}, 'gnss_general': {'add_eop_component': True, 'sys_options': {'gps': {'process': True, 'reject_eclipse': False, 'code_priorities': ['L1W', 'L1C', 'L2W']}, 'gal': {'reject_eclipse': False, 'code_priorities': ['L1C', 'L5Q', 'L1X', 'L5X']}}}, 'preprocessor': {'cycle_slips': {'mw_process_noise': 0, 'slip_threshold': 0.05}, 'preprocess_all_data': True}, 'spp': {'max_lsq_iterations': 12, 'outlier_screening': {'raim': True, 'max_gdop': 30}}, 'ppp_filter': {'outlier_screening': {'chi_square': {'enable': False, 'mode': 'innovation'}, 'prefit': {'max_iterations': 3, 'omega_test': False, 'sigma_check': True, 'state_sigma_threshold': 4, 'meas_sigma_threshold': 4}, 'postfit': {'max_iterations': 10, 'sigma_check': True, 'state_sigma_threshold': 4, 'meas_sigma_threshold': 4}}, 'ionospheric_components': {'common_ionosphere': True, 'use_gf_combo': False, 'use_if_combo': False}, 'chunking': {'by_receiver': True, 'by_satellite': False, 'size': 0}, 'rts': {'enable': True, 'lag': -1, 'inverter': 'LDLT', 'filename': '<CONFIG>_<RECEIVER>.rts'}, 'periodic_reset': None}, 'model_error_handling': {'meas_deweighting': {'deweight_factor': 1000, 'enable': True}, 'state_deweighting': {'deweight_factor': 1000, 'enable': True}, 'error_accumulation': {'enable': True, 'receiver_error_count_threshold': 4, 'receiver_error_epochs_threshold': 4}, 'ambiguities': {'outage_reset_limit': 300, 'phase_reject_limit': 2, 'reset_on': {'gf': True, 'lli': True, 'mw': True, 'scdia': True}}}}, 'estimation_parameters': {'global_models': {'eop': {'sigma': [1000], 'process_noise': [0]}, 'eop_rates': {'sigma': [1000], 'process_noise': [0]}, 'ion': {'estimated': [False], 'sigma': [-1], 'process_noise': [0]}}, 'receivers': {'global': {'pos': {'estimated': [True], 'sigma': [100]}, 'pos_rate': {'estimated': [False], 'sigma': [0], 'process_noise': [0]}, 'clock': {'estimated': [True], 'sigma': [1000], 'process_noise': [100]}, 'ant_delta': {'estimated': [True], 'sigma': [10], 'process_noise': [1], 'tau': [100]}, 'clock_rate': {'estimated': [False], 'sigma': [0.005], 'process_noise': [0.0001]}, 'ambiguities': {'estimated': [True], 'sigma': [1000], 'process_noise': [0]}, 'ion_stec': {'estimated': [True], 'sigma': [200], 'process_noise': [10]}, 'trop': {'estimated': [True], 'sigma': [0.3], 'process_noise': [0.0001]}, 'trop_grads': {'estimated': [True], 'sigma': [0.03], 'process_noise': [1e-06]}, 'code_bias': {'estimated': [True], 'sigma': [20], 'process_noise': [0]}, 'phase_bias': {'estimated': [False], 'sigma': [10], 'process_noise': [0]}}}}, 'mongo': {'enable': 'primary', 'primary_uri': 'mongodb://localhost:27017', 'primary_database': '<CONFIG>', 'primary_suffix': '', 'output_components': 'primary', 'output_states': 'primary', 'output_measurements': 'primary', 'output_test_stats': 'primary', 'delete_history': 'primary', 'output_trace': 'primary'}}


    }


    if not(preset in field_full_config):
        raise Exception(f"yaml_configs full_config {preset} doesn't exist")


    return field_full_config[preset]



def inputs_configs(preset: str):
    raise NotImplementedError
def outputs_configs(config: str):
    raise NotImplementedError
def satellite_configs(config: str):
    raise NotImplementedError
def receiver_options(config: str):
    raise NotImplementedError
def processing_options(config: str):
    raise NotImplementedError
def estimation_parameters(config: str):
    raise NotImplementedError
def mongo(config: str):
    raise NotImplementedError
