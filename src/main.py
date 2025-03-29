import os
import sys
import logging
from datetime import datetime, timezone

from src._internal.configs import  ProjectPaths, ExecutionPaths
from src._internal.executor import execute_modules
from src._internal.load_config import load_config
from src._internal.utilities.io_operations import get_or_create_directory, clear_directory
from src._internal.utilities.cli_parser import get_args

from src._internal.utilities.proj_logging import LoggerFactory
logger = LoggerFactory.get_logger(
    name="execution",
    level=logging.DEBUG,
)
logger.info("Execution starting...")


def main(args=None):
    # current_time = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    project_paths = ProjectPaths.create()
    # exec_log_file = project_paths.logs / f"execution-{current_time}.log"

    if args.debug or os.getenv('DEBUG', 'FALSE').upper() == 'TRUE':
        import debugpy
        debugpy.listen(('0.0.0.0', 5678))
        logger.info('Waiting for debugger...')
        debugpy.wait_for_client()

    runtime_config = load_config(config_file=args.config)
    execution_paths = ExecutionPaths.create(project_paths.root)

    logger.info(f"Execution ID: {execution_paths.execution_id}")
    get_or_create_directory(execution_paths.current_exec_path)
    get_or_create_directory(execution_paths.execution_output_path)

    logger.info(f'Using config: {args.config}')
    logger.debug(f'Execution order: {runtime_config.general.execution_order}')

    # Run all modules
    execute_modules(runtime_config, execution_paths)

    if runtime_config.general.delete_execution_data:
        clear_directory(execution_paths.current_exec_path)

    logger.info('Execution finished')
    sys.exit(0)


if __name__ == '__main__':
    main_args = get_args()
    try:
        main(main_args)
    except Exception as e:
        logger.error(f'Execution failed: {e}')
        sys.exit(1)
    finally:
        logger.info('The process has completed')
