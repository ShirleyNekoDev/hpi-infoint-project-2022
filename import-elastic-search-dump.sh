elasticdump --output=http://localhost:9200/rb_filtered_announcements --input=./data/rb_filtered_announcements-mapping.json --type=mapping --bulk=true
elasticdump --output=http://localhost:9200/rb_filtered_announcements --input=./data/rb_filtered_announcements-data.json --type=data --bulk=true

elasticdump --output=http://localhost:9200/rb_companies --input=./data/rb_companies-mapping.json --type=mapping --bulk=true
elasticdump --output=http://localhost:9200/rb_companies --input=./data/rb_companies-data.json --type=data --bulk=true

elasticdump --output=http://localhost:9200/rb_persons --input=./data/rb_persons-mapping.json --type=mapping --bulk=true
elasticdump --output=http://localhost:9200/rb_persons --input=./data/rb_persons-data.json --type=data --bulk=true

elasticdump --output=http://localhost:9200/ffb_trade-events --input=./data/ffb_trade-events-mapping.json --type=mapping --bulk=true
elasticdump --output=http://localhost:9200/ffb_trade-events --input=./data/ffb_trade-events-data.json --type=data --bulk=true

elasticdump --output=http://localhost:9200/ffb_companies --input=./data/ffb_companies-events-mapping.json --type=mapping --bulk=true
elasticdump --output=http://localhost:9200/ffb_companies --input=./data/ffb_companies-events-data.json --type=data --bulk=true
