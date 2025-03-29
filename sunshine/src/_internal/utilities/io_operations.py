import logging
import os
import shutil
from pathlib import Path

from proj_logging import LoggerFactory
logger = LoggerFactory.get_logger(name=__name__)

def get_or_create_directory(path: Path) -> Path:
    """
    Ensure a directory exists at the given path.
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Verified or created directory: {path}")
        return path
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {e}")
        raise

def copy_file(src: Path, dst: Path) -> None:
    """
    Copy a single file from src to dst.
    """

    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        logger.debug(f"Copied file from {src} to {dst}")
    except Exception as e:
        logger.error(f"Failed to copy file from {src} to {dst}: {e}")
        raise

def copy_directory(src_folder: Path, dest_folder: Path) -> None:
    """
    Copy all contents from src_folder to dest_folder.
    """

    try:
        if not src_folder.exists() or not src_folder.is_dir():
            logger.warning(f"Source directory {src_folder} does not exist or is not a directory.")
            return

        for item in src_folder.rglob('*'):
            relative_path = item.relative_to(src_folder)
            dest_path = dest_folder / relative_path

            if item.is_dir():
                get_or_create_directory(dest_path)
            elif item.is_file():
                copy_file(item, dest_path)

    except Exception as e:
        logger.error(f"Failed to copy contents of {src_folder} to {dest_folder}: {e}")
        raise

def clear_directory(directory: Path) -> None:
    """
    Clear all contents from a directory without deleting the directory itself.
    """

    if not directory.exists():
        logger.warning(f"Path '{directory}' does not exist. Nothing to clear.")
        return

    if not directory.is_dir():
        logger.warning(f"Path '{directory}' is not a directory.")
        return

    for entry in directory.iterdir():
        try:
            if entry.is_file() or entry.is_symlink():
                entry.unlink()
                logger.debug(f"Removed file/symlink: {entry}")
            elif entry.is_dir():
                shutil.rmtree(entry)
                logger.info(f"Deleted directory and contents: {entry}")
        except Exception as e:
            logger.error(f"Failed to delete '{entry}': {e}")
            logger.warning("Proceeding to next item...")

def directory_is_empty(directory: Path) -> bool:
    """
    Check if a directory is empty.
    """

    if not directory.exists():
        raise FileNotFoundError(f"Path '{directory}' does not exist.")
    if not directory.is_dir():
        raise NotADirectoryError(f"Path '{directory}' is not a directory.")

    is_empty = not any(directory.iterdir())
    logger.debug(f"Directory '{directory}' is {'empty' if is_empty else 'not empty'}.")
    return is_empty

def safe_delete(path: Path) -> None:
    """
    Safely delete a file or directory.
    """

    try:
        if path.is_file() or path.is_symlink():
            path.unlink()
            logger.info(f"Deleted file/symlink: {path}")
        elif path.is_dir():
            shutil.rmtree(path)
            logger.info(f"Deleted directory and contents: {path}")
    except Exception as e:
        logger.error(f"Failed to delete {path}: {e}")
        raise

def find_project_root() -> Path:
    """
    Detect the project root using:
    - PROJECT_ROOT env variable
    - /opt for production scenarios
    - Walk-up search for marker files
    """

    env_root = os.getenv("PROJECT_ROOT")
    if env_root:
        logger.info(f"Using PROJECT_ROOT from environment: {env_root}")
        return Path(env_root).resolve()

    if Path('/opt').exists():
        logger.info("Detected /opt environment. Using /opt as project root.")
        return Path('/opt')

    current_dir = Path(__file__).resolve().parent
    marker_file = 'project.marker'
    for parent in [current_dir] + list(current_dir.parents):
        if (parent / marker_file).exists():
            logger.info(f"Found project root at {parent} via '{marker_file}'.")
            return parent

    logger.warning("No project root marker found. Falling back to current working directory.")
    return Path.cwd().resolve()
