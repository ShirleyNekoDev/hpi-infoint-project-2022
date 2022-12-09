
import json

from elasticsearch_cmd_ui.output import print_companies
from elasticsearch_cmd_ui.config import query_page_size
from elasticsearch_cmd_ui.utils import query_elasticsearch







def query_select_company(
    search_term,
    query_state
):
    query_position = query_state["query_page_index"] * query_page_size
    query_data = query_elasticsearch("companies", {
        "query": {
            "multi_match": {
                "query": search_term,
                "fields": ["name", "std_name"]
            }
        },
        "from": query_position,
        "size": query_page_size,
        "sort": [
            "_score"
        ]
    })
    if not query_data:
        print("Failed to query elasticsearch, see log for details")
        exit(0)
    
    queried_company_count = query_data["total"]["value"]
    if queried_company_count >= 10000:
        # cannot paginate larger search queries in elastic
        print("Your search returned too many results. Please try to narrow down your query term.\n")
        return None

    print_companies(query_data)
        
    return state

query_state = {
    "query_page_index": 0,
    "query_page_count": 0,
    "queried_companies": None,
    "selected_company_data": None
}

def restart():
    query_state = {
        "query_page_index": 0,
        "query_page_count": 0,
        "queried_companies": None,
        "selected_company_data": None
    }

def run():
    try:
        search_term = "None"
        while True:
            query_page_count = query_state["query_page_count"]
            # Input validation
            if search_term == "q":
                exit(0)
            elif len(search_term) < 2:
                if query_state["queried_companies"] and len(search_term) == 1:
                    # select companies
                    selection_index = available_positions.find(search_term)
                    if selection_index >= 0:
                        query_state["selected_company_data"] = query_state["queried_companies"][selection_index]
                    else:
                        search_term = input(f"Invalid company selector. Choose from a-{available_positions[company_count-1]}: ")
                        continue
                else:
                    search_term = input("Please provide a longer search term:\n")
                    continue
            elif search_term.isdigit():
                if query_state["queried_companies"] and query_page_count > 0:
                    # company pagination
                    index = int(search_term)
                    if index > 0 and index <= query_page_count:
                        query_state["query_page_index"] = index-1
                    else:
                        search_term = input(f"Invalid pagination index. Choose from 1-{query_page_count}: ")
                        continue
                else:
                    print("Searching numeric-only queries is not supported")
                    search_term = input("Enter the company you are searching for or q to quit:\n")
                    continue
            else:
                if query_state["selected_company_data"]:
                    # user selected company -> display it
                    output_results(query_state["selected_company_data"])
                    query_state["selected_company_data"] = None
                    # start new search
                    search_term = input("Enter another company you are searching for or q to quit:\n")
                    continue
                else:
                    # fresh query
                    search_term = input("Enter the company you are searching for or q to quit:\n")
                    continue
                # query by company name
                        
            if not query_state:
            
            else:
                # initial search
                search_term = input("Enter the company you are searching for:\n")
                continue
            query_state = query_select_company()

            selection_index = 0

            query_page_count = int(company_count / query_page_size)


            if company_count == 0:
                print(f"No match found for your input")
                continue
            elif company_count == 1:
                selection_index = 1
                print(f"Found this company for \"{search_term}\":")
            elif company_count > query_page_size:
                print(f"Found these companies for \"{search_term}\" {query_position+1}-{query_position+query_page_size}/{company_count} [page {query_page_index}/{query_page_count}]:")
                company_count = query_page_size
            else:
                print(f"Found these companies for \"{search_term}\" (total {company_count}):")
            print(f"\n{str(company_table)}\n")

            print(f"Input a-{available_positions[company_count-1]} to select an available company")
            print(f"Input 0-{query_page_count} to select a different pagination page"
            print("Input q to quit")
            print("Or input another search term:")
            while not selection_index:
                input_text = input(f)
                if input_text == "q":
                    exit(0)
                if input_text.isdigit():
                    query_page_index = 
                    return {
                        "mode": "switch_page",
                        "page": int(input_text)
                    }
                if len(input_text) == 1:
                    selection_index = available_positions.find(input_text)
                    if selection_index >= 0:
                        break
                if not validate_company_search_term(search_term):
                # have pagination using ints
                # otherwise restart search
                selection_index = int(input_text) if input_text.isdigit() else 0
                if selection_index > company_count or selection_index < 1:
                    print("Invalid value, please try again.")
                    selection_index = 0

            company_data = matching_companies[selection_index-1]["_source"]
            output_results(company_data)

    except KeyboardInterrupt:
        exit(0)

if __name__ == "__main__":
    run()
