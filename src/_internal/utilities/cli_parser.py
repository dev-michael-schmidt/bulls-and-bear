"""
TODO add more details (as module takes shape)
"""
import logging
import argparse
from pathlib import Path


from proj_logging import LoggerFactory
logger = LoggerFactory.get_logger(name=__name__)


# Apply overrides to configurations
def apply_overrides(config: dict, overrides: list[str]) -> None:

    logger.info(f'{len(overrides)} runtime overrides requested')

    for override in overrides:
        try:
            key, value = override.split('=', 1)  # Split only at the first '='
            key = key.strip()
            value = value.strip()
            logger.debug(f'key: {key}, {type(key)}, value: {value}')
            # Convert value to appropriate type based on existing config value
            if key in config:
                if isinstance(config[key], int):
                    config[key] = int(value)
                elif isinstance(config[key], float):
                    config[key] = float(value)
                elif isinstance(config[key], list):
                    config[key] = value.split(',')  # Handle list overrides
                elif isinstance(config[key], bool):
                    config[key] = value.lower() in ('true', '1', 'yes')
                else:
                    config[key] = value
            else:
                logger.warning(f"Warning: '{key}' is not a valid configuration key")
        except ValueError as exc:
            logger.error(f"Invalid format for override: '{override}'")
            raise ValueError(f"Invalid format for override: '{override}'")

def get_args():
    parser = argparse.ArgumentParser(description='Moonshine Project Argument Parser')

    parser.add_argument(
        '--config',
        type=str,
        default='app-config.toml',
        help='Path to the configuration file (default: app-config.toml)'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )

    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Set the logging level (default: INFO)'
    )

    parser.add_argument(
        '--overrides',
        type=str,
        nargs='*',
        help='Override configuration values at runtime using key=value pairs (e.g., --overrides foo=bar baz=42)'
    )

    return parser.parse_args()
