curl -X GET "localhost:9200/_search?pretty" -H 'Content-Type: application/json' -d'
{
    "query": {
        "match": {
            "reference_id":"HRB 31499"
        }
    }
}
'
