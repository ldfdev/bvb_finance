import pathlib
import subprocess
import docker
import datetime
from bvb_finance.company_reports import constants
from bvb_finance.persist import db_constants
from bvb_finance import datetime_conventions
import pathlib
import os

container_path = '/docker_files'
host_path = pathlib.Path(constants.root_dir) / (container_path.strip(os.sep))
mongo_conrainer = f'mongo-server-{constants.bvb_finance}'

client = docker.from_env()

def create_container_path():
    host_path.mkdir(parents=True, exist_ok=True)

def get_container(container_name):
    c = [c for c in client.containers.list() if c.name == container_name]
    if len(c) == 0:
        return
    return c[0]

def is_container_running(container_name):
    return not (get_container(container_name) is None)

def clear_exited_container(container_name0):
    lst = [c for c in client.containers.list(all=True) if c.name == container_name0]
    for c in lst:
        if c.status == 'exited':
            c.remove()
    clear_volumes()

def clear_volumes():
    for vol in client.volumes.list():
        try:
            vol.remove()
        except docker.errors.APIError:
            pass

def start_mongo_container():
    if is_container_running(mongo_conrainer):
        return
    clear_exited_container(mongo_conrainer)
    create_container_path()
    cmd = f'docker run -d -p 27017:27017 -v {host_path.as_posix()}:/{container_path}:rw --rm --name {mongo_conrainer} mongo'
    subprocess.run(cmd, shell=True, check=True)

def export_mongo_container_db() -> str:
    '''
    return the file to which database content has been exported
    '''
    if not is_container_running(mongo_conrainer):
        return
    container = get_container(mongo_conrainer)
    now = datetime.datetime.now()
    json_file = pathlib.Path(container_path) / f'{db_constants.bvb_companies_collection}.{now.strftime(datetime_conventions.date_time_file_format)}.json'
    json_file = json_file.as_posix()
    cmd = f'mongoexport --uri=mongodb://localhost/{db_constants.bvb_companies_db_name} --collection={db_constants.bvb_companies_collection}  --out={json_file}'
    container.exec_run(cmd)
    return (host_path / json_file.name).as_posix()
