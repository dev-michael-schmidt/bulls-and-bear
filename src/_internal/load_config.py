import tomllib
from pathlib import Path
from typing import Optional, List, Dict, Any

from configs import GeneralConfig, RuntimeConfig
from utilities.io_operations import find_project_root

from utilities.proj_logging import LoggerFactory
logger = LoggerFactory.get_logger(name=__name__)

def read_toml_config(config_path: Path) -> Dict[str, Any]:
    logger.info(f"Reading configuration from {config_path}")
    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    try:
        with config_path.open('rb') as f:
            return tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        logger.error(f"TOML parsing error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error reading TOML: {e}")
        raise

def apply_overrides_to_dict(base_dict: Dict[str, Any], overrides: Optional[List[str]]) -> Dict[str, Any]:
    if not overrides:
        return base_dict

    updated_config = base_dict.copy()
    for override in overrides:
        try:
            key, value = override.split('=', 1)
            logger.info(f"Applying override: {key} = {value}")
            # Attempt to parse numeric values or fallback to string
            if value.isdigit():
                value = int(value)
            elif value.replace('.', '', 1).isdigit():
                value = float(value)
            updated_config[key.strip()] = value
        except ValueError as e:
            logger.error(f"Invalid override format '{override}': {e}")
            raise
    return updated_config

def parse_general_config(config_data: Dict[str, Any]) -> GeneralConfig:
    def resolve_path(path_str: Optional[str]) -> Path:
        return (find_project_root() / path_str).resolve() if path_str else Path()

    return GeneralConfig(
        input_path=resolve_path(config_data.get('input_path')),
        output_path=resolve_path(config_data.get('output_path')),
        execution_path=resolve_path(config_data.get('execution_path')),
        coefficient_term_expansion=config_data.get('coefficient_term_expansion', 0),
        standard_temperature=config_data.get('standard_temperature', 0),
        execution_order=config_data.get('execution_order', []),
        load_all_files=config_data.get('load_all_files', True),
        delete_execution_data=config_data.get('delete_execution_data', False)
    )

def load_config(module_name: Optional[str] = None, config_file: Optional[str] = None, overrides: Optional[List[str]] = None) -> RuntimeConfig:
    logger.info("Starting configuration load process...")
    config_path = Path(config_file).resolve() if config_file else find_project_root() / 'app-config.toml'

    config_data = read_toml_config(config_path)

    if overrides:
        config_data = apply_overrides_to_dict(config_data, overrides)

    general_config = parse_general_config(config_data)
    module_config = config_data.get(module_name, {}) if module_name else {}
    storage_type = config_data.get('storage_type', 'local')

    logger.info(f"Configuration loaded successfully. Storage type: {storage_type}, Module: {module_name or 'None'}")

    return RuntimeConfig(general=general_config, module=module_config, storage_type=storage_type)
