from pathlib import Path

resources = 'resources'

def load_resource_file(file_name) -> str:
    with open(Path(__file__).parent / resources / file_name, 'r') as reader:
        return reader.read()
