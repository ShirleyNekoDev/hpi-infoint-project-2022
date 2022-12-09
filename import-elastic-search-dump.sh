
elasticdump --output=http://localhost:9200/companies --input=./data/companies-mapping.json --type=mapping --bulk=true
elasticdump --output=http://localhost:9200/companies --input=./data/companies-data.json --type=data --bulk=true

elasticdump --output=http://localhost:9200/filtered_announcements --input=./data/filtered_announcements-mapping.json --type=mapping --bulk=true
elasticdump --output=http://localhost:9200/filtered_announcements --input=./data/filtered_announcements-data.json --type=data --bulk=true

elasticdump --output=http://localhost:9200/trade-events --input=./data/trade-events-mapping.json --type=mapping --bulk=true
elasticdump --output=http://localhost:9200/trade-events --input=./data/trade-events-data.json --type=data --bulk=true

elasticdump --output=http://localhost:9200/persons --input=./data/persons-mapping.json --type=mapping --bulk=true
elasticdump --output=http://localhost:9200/persons --input=./data/persons-data.json --type=data --bulk=true
