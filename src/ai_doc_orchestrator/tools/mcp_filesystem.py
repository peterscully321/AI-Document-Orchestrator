"""MCP File System Read tool."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional


class MCPFileSystemTool:
    """Tool for reading files from the local file system (MCP-style)."""

    def __init__(self, base_path: Optional[str] = None):
        """Initialize the file system tool.

        Args:
            base_path: Base path for file operations (defaults to current directory)
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()

    def read_file(self, file_path: str) -> Dict[str, Any]:
        """Read a file from the file system.

        Args:
            file_path: Path to the file (relative to base_path or absolute)

        Returns:
            Dictionary with file content and metadata

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file cannot be read
        """
        path = Path(file_path)
        if not path.is_absolute():
            path = self.base_path / path

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if not path.is_file():
            raise ValueError(f"Path is not a file: {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try binary mode for non-text files
            with open(path, "rb") as f:
                content = f.read()
                return {
                    "path": str(path),
                    "content": content,
                    "is_binary": True,
                    "size": len(content),
                }

        return {
            "path": str(path),
            "content": content,
            "is_binary": False,
            "size": len(content),
            "encoding": "utf-8",
        }

    def list_files(self, directory: str = ".", pattern: Optional[str] = None) -> List[str]:
        """List files in a directory.

        Args:
            directory: Directory path (relative to base_path or absolute)
            pattern: Optional glob pattern to filter files

        Returns:
            List of file paths
        """
        dir_path = Path(directory)
        if not dir_path.is_absolute():
            dir_path = self.base_path / dir_path

        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {dir_path}")

        if not dir_path.is_dir():
            raise ValueError(f"Path is not a directory: {dir_path}")

        if pattern:
            files = list(dir_path.glob(pattern))
        else:
            files = list(dir_path.iterdir())

        return [str(f) for f in files if f.is_file()]

