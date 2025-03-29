import importlib
import logging

from configs import ModuleExecutionContext, RuntimeConfig, ProjectPaths, ExecutionPaths
from src._internal.execution_helpers import prepare_module_execution_context
from utilities.io_operations import copy_directory
from utilities.proj_logging import LoggerFactory

logger = LoggerFactory.get_logger(name=__name__)
paths = ProjectPaths.create()

def execute_module(
    module_ctx: ModuleExecutionContext,
    execution_paths: ExecutionPaths,
) -> None:
    """
    Dynamically imports and runs a module's main() function with input/output/config.
    Copies output from module output to the central execution-output folder after successful execution.
    """
    try:
        logger.info(f"Starting execution for module: {module_ctx.name}")
        module = importlib.import_module(f"modules.{module_ctx.name}.main")

        if not hasattr(module, 'main'):
            logger.error(f"Module '{module_ctx.name}' has no main() function.")
            raise AttributeError(f"Module '{module_ctx.name}' missing main()")

        # Call module's main()
        module.main(context=module_ctx)

        logger.info(f"Execution of module '{module_ctx.name}' completed.")

        # Copy results to the execution-output folder
        if module_ctx.output_path.exists():
            copy_directory(module_ctx.output_path, execution_paths.execution_output_path)
            logger.info(f"Output from '{module_ctx.name}' copied to execution-output directory.")
        else:
            logger.warning(f"No output found for module '{module_ctx.name}'; nothing copied.")

    except Exception as e:
        logger.error(f"Execution failed for module '{module_ctx.name}': {e}")
        raise


def execute_modules(
    runtime_config: RuntimeConfig,
    execution_paths: ExecutionPaths,
) -> None:
    """
    Executes all modules defined in runtime_config.general.execution_order.
    For each module, prepares an execution context and runs it.
    """
    logger.info("Starting execution of all modules.")

    for module_name in runtime_config.general.execution_order:
        logger.info(f"Preparing execution context for module: {module_name}")
        module_ctx = prepare_module_execution_context(
            runtime_config=runtime_config,
            module_name=module_name,
            execution_paths=execution_paths,
        )

        execute_module(module_ctx, execution_paths)

    logger.info("All modules executed successfully.")
