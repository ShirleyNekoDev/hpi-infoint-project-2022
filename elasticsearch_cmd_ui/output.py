
import textwrap
from prettytable import PrettyTable, SINGLE_BORDER

from elasticsearch_cmd_ui.config import available_positions
from elasticsearch_cmd_ui.utils import abbreviate_id, query_elasticsearch

company_table = PrettyTable(["Choice", "Id (abbr)", "Name", "Description"])
company_table.set_style(SINGLE_BORDER)
company_table.custom_format["Choice"] = lambda f, v: f"{available_positions[v]})"
company_table.custom_format["Id (abbr)"] = lambda f, v: abbreviate_id(v)
company_table.custom_format["Description"] = lambda f, v: textwrap.shorten(v, width=160, placeholder="…")
company_table.align["Choice"] = "r"
company_table.align["Id (abbr)"] = "c"
company_table.align["Name"] = "l"
company_table.align["Description"] = "l"

announcement_table = PrettyTable(["ID (abbr)", "RB Id", "State", "Court", "Reference Id", "Date", "Event Type", "Status"])
announcement_table.set_style(SINGLE_BORDER)
announcement_table.sortby = "Date"
announcement_table.custom_format["Id (abbr)"] = lambda f, v: abbreviate_id(v)
announcement_table.align["Id (abbr)"] = "l"
announcement_table.align["RB Id"] = "l"
announcement_table.align["State"] = "c"
announcement_table.align["Court"] = "l"
announcement_table.align["Reference Id"] = "l"
announcement_table.align["Date"] = "c"
announcement_table.align["Event Type"] = "c"
announcement_table.align["Status"] = "c"

trade_table = PrettyTable(["Id (abbr)", "Time", "ISIN", "Product Type", "Issuer", "Price", "Volume"])
trade_table.set_style(SINGLE_BORDER)
trade_table.sortby = "Time"
trade_table.custom_format["Id (abbr)"] = lambda f, v: abbreviate_id(v)
trade_table.custom_format["Price"] = lambda f, v: f"{v:.2f}€"
trade_table.align["Id (abbr)"] = "l"
trade_table.align["Time"] = "l"
trade_table.align["ISIN"] = "c"
trade_table.align["Product Type"] = "l"
trade_table.align["Issuer"] = "l"
trade_table.align["Price"] = "r"
trade_table.align["Volume"] = "r"


# TODO paginate

def print_companies(company_data, show_table_header: bool = True):
    for index, company_document in enumerate(company_data["hits"]):
        company_obj = company_document["_source"]
        company_table.add_row([
            index,
            company_obj["id"],
            company_obj["name"],
            company_obj["description"]
        ])
    if show_table_header:
        #TODO
        pass
    print(f"\n{str(company_table)}\n")

def output_results(company_data):
    company_id = company_data["id"]
    company_name = company_data["name"]

    # TODO: show company info (address, persons etc)

    query_and_print_announcements(company_id, company_name)
    query_and_print_trade_events(company_id, company_name)

def query_and_print_announcements(company_id: str, company_name: str):
    announcements_data = query_elasticsearch("filtered_announcements", {
        "query": {
            "match": {
                "company_id": {
                    "query": company_id
                }
            }
        }
    })

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

def query_and_print_trade_events(company_id: str, company_name: str):
    trades_data = query_elasticsearch("filtered_trade-events", {
        "query": {
            "match": {
                "company_id": {
                    "query": company_id
                }
            }
        }
    })

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