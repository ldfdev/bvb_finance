## To start a mongo container
docker run -d -p 27017:27017 --name mongo-server mongo

## To run all unit tests
python3  -m unittest discover tests/