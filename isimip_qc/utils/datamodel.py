import shutil
import subprocess
from typing import Iterable


def _run_tool(tool: str, args: Iterable[str], input_file, output_file) -> None:
    """Run an external tool with the given arguments and files.

    Raises FileNotFoundError if the tool is not available in PATH and
    subprocess.CalledProcessError if the tool returns a non-zero exit code.
    """
    if shutil.which(tool) is None:
        raise FileNotFoundError(f"Required tool '{tool}' not found in PATH")

    cmd = [tool, *args, str(input_file), str(output_file)]
    subprocess.run(cmd, check=True)


def call_cdo(args: Iterable[str], input_file, output_file) -> None:
    _run_tool('cdo', args, input_file, output_file)


def call_nccopy(args: Iterable[str], input_file, output_file) -> None:
    _run_tool('nccopy', args, input_file, output_file)
