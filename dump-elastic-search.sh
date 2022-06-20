elasticdump --input=http://localhost:9200/rb_announcements --output ./data/rb_announcements-data.json --type=data
elasticdump --input=http://localhost:9200/rb_announcements --output ./data/rb_announcements-mapping.json --type=mapping
elasticdump --input=http://localhost:9200/rb_companies --output ./data/rb_companies-data.json --type=data
elasticdump --input=http://localhost:9200/rb_companies --output ./data/rb_companies-mapping.json --type=mapping
elasticdump --input=http://localhost:9200/rb_persons --output ./data/rb_persons-data.json --type=data
elasticdump --input=http://localhost:9200/rb_persons --output ./data/rb_persons-mapping.json --type=mapping
elasticdump --input=http://localhost:9200/ffb_trade-events --output ./data/ffb_trade-events-data.json --type=data
elasticdump --input=http://localhost:9200/ffb_trade-events --output ./data/ffb_trade-events-mapping.json --type=mapping
