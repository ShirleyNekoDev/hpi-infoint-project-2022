
import logging
import textwrap
import requests
import json
from prettytable import PrettyTable

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


elasticsearch_url_format_str = "http://localhost:9200/{}/_search"
max_company_display_count = 10

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


def run():
    # get company for best matching search term
    search_term = input("Enter the company you are searching for:\n")
    print("You are searching for: " + search_term + "\n")

    data = query_elasticsearch("companies", {
        "query": {
            "multi_match": {
                "query": search_term,
                "fields": ["name", "std_name"]
            }
        }
    })
    company_count = 0
    selection_index = 0
    if data:
        company_count = data["total"]["value"]
        matching_companies = data["hits"][0:max_company_display_count]

        company_table = PrettyTable(['position', 'id (abbr.)', 'name', 'description'])
        for index, company_document in enumerate(matching_companies):
            company_obj = company_document["_source"]
            company_table.add_row([
                str(index+1)+")",
                company_obj["id"][0:4] + "…" + company_obj["id"][-4:], 
                company_obj["name"],
                textwrap.shorten(company_obj["description"], width=160, placeholder="…")
            ])

        if company_count == 0:
            print(f"No match found for your input")
            exit(0)
        elif company_count == 1:
            selection_index = 1
            print(f"Found this company for your input:")
        elif company_count > max_company_display_count:
            print(f"Found these companies for your input (first {max_company_display_count} only / total {company_count}):")
            company_count = max_company_display_count
        else:
            print(f"Found these companies for your input (total {company_count}):")
        print(f"\n{str(company_table)}\n")

    while not selection_index:
        input_text = input(f"Select the company, you want to query data for (1-{company_count}):\n")
        selection_index = int(input_text) if input_text.isdigit() else 0
        if selection_index > company_count or selection_index < 1:
            print("Invalid value, please try again.")
            selection_index = 0

    company_data = matching_companies[selection_index-1]["_source"]
    company_id = company_data["id"]
    company_name = company_data["name"]
    print(f"\nUsing first matching company named \"{company_name}\" (id={company_id})")

    # matching

    # fetch announcements by company_id
    announcements_data = query_elasticsearch("filtered_announcements", {
        "query": {
            "match": {
                "company_id": {
                    "query": company_id
                }
            }
        }
    })

    announcement_table = PrettyTable(["id", "rb_id", "state", "court", "reference_id", "event_date", "event_type", "status"])
    for announcement_document in announcements_data["hits"]:
        announcement_obj = announcement_document["_source"]
        announcement_table.add_row([
            announcement_obj["id"], 
            announcement_obj["rb_id"], 
            announcement_obj["state"], 
            announcement_obj["court"], 
            announcement_obj["reference_id"], 
            announcement_obj["event_date"], 
            announcement_obj["event_type"], 
            announcement_obj["status"]
        ])
    print(f"\nRB Announcements for \"{company_name}\":\n{str(announcement_table)}\n")

    # fetch trades by company_id
    trades_data = query_elasticsearch("filtered_trade-events", {
        "query": {
            "match": {
                "company_id": {
                    "query": company_id
                }
            }
        }
    })

    trade_table = PrettyTable(["id", "time", "isin", "product_type", "issuer", "price", "volume"])
    for trade_document in trades_data["hits"]:
        trade_obj = trade_document["_source"]
        trade_table.add_row([
            trade_obj["id"], 
            trade_obj["time"], 
            trade_obj["isin"], 
            trade_obj["product_type"], 
            trade_obj["issuer"], 
            trade_obj["price"], 
            trade_obj["volume"]
        ])
    print(f"\nFFB Trade Events for \"{company_name}\":\n{str(trade_table)}\n")


if __name__ == "__main__":
    run()
