
import logging
import requests

from elasticsearch_cmd_ui.config import elasticsearch_url_format_str

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def query_elasticsearch(index: str, query: dict):
    log.debug("Querying index " + index + " with query: " + str(query))
    url = elasticsearch_url_format_str.format(index)
    headers = {"Content-type": "application/json"}
    response = requests.get(url, headers=headers, data=json.dumps(query))
    data = response.json()
    if "error" in data:
        log.error(data["error"])
        return None
    return data["hits"]

def abbreviate_id(id: str, places_before_ellipsis: int = 4, places_after_ellipsis: int = 4) -> str:
    return id[0:places_before_ellipsis] + "…" + id[-places_after_ellipsis:]
