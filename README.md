# About the `resources` folder
Currently the list of portfolio ticker that user is interested in is stored in `portfolio_companies.json`
The file represent a valid JSON list, such as
```json
[
    "AQ",
    "BRD"
]
```

## To start a mongo container
docker run -d -p 27017:27017 --name mongo-server mongo

## To run all unit tests
`python3  -m unittest discover tests/`

## To lint
`flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics`
