from pathlib import Path
import sys

# add bvb_finance project path in tests
sys.path.append(Path(__file__).parent.parent)

resources = 'resources'

def load_resource_file(file_name) -> str:
    with open(Path(__file__).parent / resources / file_name, 'r') as reader:
        return reader.read()

def get_full_path(resource_file: str) -> Path:
    if resources in Path(resource_file).parts:
        return Path(__file__).parent  / resource_file
    return Path(__file__).parent / resources / resource_file
