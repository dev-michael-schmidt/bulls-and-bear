import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from utilities.io_operations import find_project_root

from utilities.proj_logging import LoggerFactory
logger = LoggerFactory.get_logger(name=__name__)

@dataclass(frozen=True)
class ExecutionEnvironment:
    exec_folder_name: str
    current_exec_path: Path
    execution_input_path: Path
    execution_output_path: Path



"""
Context: the circumstances that form the setting for an event, and in
    terms of which it can be fully understood and assessed.
    
    a fancy word for "use this for that"
"""
@dataclass(frozen=True)
class ModuleExecutionContext:
    name: str
    input_path: Path
    output_path: Path
    config: Dict[str, Any]


@dataclass(frozen=True)
class GeneralConfig:
    input_path: Path
    output_path: Path
    execution_path: Path
    coefficient_term_expansion: int = 0
    standard_temperature: int = 0
    execution_order: List[str] = field(default_factory=list)
    load_all_files: bool = True
    delete_execution_data: bool = False


@dataclass(frozen=True)
class RuntimeConfig:
    general: GeneralConfig
    module: Dict[str, Any]
    storage_type: str


@dataclass(frozen=True)
class ProjectPaths:
    root: Path
    data: Path
    logs: Path
    tests: Path
    execution_input: Path

    @staticmethod
    def create() -> 'ProjectPaths':
        root = find_project_root()
        return ProjectPaths(
            root=root,
            data=root / 'data',
            logs=root / 'logs',
            tests=root / 'tests' / 'test_data',
            execution_input=root / 'execution-input'
        )


@dataclass(frozen=True)
class ExecutionPaths:
    execution_id: str
    current_exec_path: Path
    execution_input_path: Path
    execution_output_path: Path

    @staticmethod
    def create(project_root: Path) -> 'ExecutionPaths':
        execution_id = f"execution-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4()}"
        current_exec_path = project_root / execution_id
        return ExecutionPaths(
            execution_id=execution_id,
            current_exec_path=current_exec_path,
            execution_input_path=current_exec_path / 'execution-input',
            execution_output_path=current_exec_path / 'execution-output'
        )