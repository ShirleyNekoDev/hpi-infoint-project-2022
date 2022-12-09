
elasticdump --input=http://localhost:9200/companies --output ./data/companies-data.json --type=data --limit 10000
elasticdump --input=http://localhost:9200/companies --output ./data/companies-mapping.json --type=mapping

elasticdump --input=http://localhost:9200/filtered_announcements --output ./data/filtered_announcements-data.json --type=data --limit 10000
elasticdump --input=http://localhost:9200/filtered_announcements --output ./data/filtered_announcements-mapping.json --type=mapping

elasticdump --input=http://localhost:9200/trade-events --output ./data/trade-events-data.json --type=data --limit 10000
elasticdump --input=http://localhost:9200/trade-events --output ./data/trade-events-mapping.json --type=mapping

elasticdump --input=http://localhost:9200/persons --output ./data/persons-data.json --type=data --limit 10000
elasticdump --input=http://localhost:9200/persons --output ./data/persons-mapping.json --type=mapping
