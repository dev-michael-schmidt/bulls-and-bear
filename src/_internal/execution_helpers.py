import logging
from pathlib import Path

from src._internal.configs import RuntimeConfig, ExecutionPaths, ModuleExecutionContext
from src._internal.utilities.io_operations import get_or_create_directory, copy_directory, directory_is_empty, copy_file

from utilities.proj_logging import LoggerFactory
logger = LoggerFactory.get_logger(name=__name__)

def prepare_module_execution_context(
    runtime_config: RuntimeConfig,
    module_name: str,
    execution_paths: ExecutionPaths,
) -> ModuleExecutionContext:
    """
    Sets up the input/output environment for a single module execution.
    - Creates module input/output directories.
    - Copies required input files.
    - Merges output from previous modules if chaining is enabled.
    - Returns a ModuleExecutionContext object with metadata and config.
    """
    module_input = get_or_create_directory(execution_paths.current_exec_path / module_name / "input")
    module_output = get_or_create_directory(execution_paths.current_exec_path / module_name / "output")

    module_config = runtime_config.module.get(module_name, {}).copy()
    module_config['module_input_path'] = module_input
    module_config['module_output_path'] = module_output

    if runtime_config.general.load_all_files:
        copy_directory(runtime_config.general.input_path, module_input)
    else:
        for file in module_config.get('input_files', []):
            copy_file(Path(file), module_input / Path(file).name)

    if not directory_is_empty(execution_paths.execution_output_path):
        copy_directory(execution_paths.execution_output_path, module_input)

    logger.info(f"Prepared execution context for module '{module_name}'")

    return ModuleExecutionContext(
        name=module_name,
        input_path=module_input,
        output_path=module_output,
        config=module_config
    )