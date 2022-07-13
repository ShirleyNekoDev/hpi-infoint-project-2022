from locale import atof, setlocale, LC_NUMERIC
import re

from build.gen.student.academic.v1.rb_company_pb2 import RBCompany, CompanyPosition
from build.gen.student.academic.v1.rb_person_pb2 import RBPerson
from id_generator import company_id_generator, sha256, standardize_company_name


setlocale(LC_NUMERIC, "de_DE")

definition_regex = re.compile("\s+(?P<role>[^.,;]*?):")
separator_regex = re.compile("[.,;]\s+")
enumeration_regex = re.compile("\s?(?P<index>\d+)\.\s?")
personnel_name_regex = re.compile("\s+(?P<last_name>[^.,]*?),\s?(?P<first_name>[^.,]*?),")
personnel_birth_date_regex = re.compile("\s+\*(?P<birth_date>\d{2}.\d{2}.\d{4})[.,]")
not_personnel_definitions = re.compile("Vertretungsregelung|Rechtsform|Gesellschaftsvertrag")

def extract_personnel(information: str) -> dict:
    information = information.replace("\n", " ").replace("\\n", " ")
    persons = []
    positions = []
    for match in definition_regex.finditer(information):
        role = match.group("role")
        if not_personnel_definitions.search(role):
            continue

        position = CompanyPosition()
        position.role = role

        person = RBPerson()
        match = personnel_name_regex.search(information, match.end())
        if not match:
            continue

        person.first_name = match.group("first_name")
        person.last_name = match.group("last_name")
        enumeration_match = enumeration_regex.match(person.last_name)
        if enumeration_match:
            person.last_name = person.last_name[enumeration_match.end():]

        end_of_name = match.end()
        match = personnel_birth_date_regex.search(information, match.end())
        if not match:
            continue

        person.birth_date = match.group("birth_date")
        if match.start() == end_of_name:
            # birth place comes after date
            end_of_place_match = separator_regex.search(information, match.end())
            if not end_of_place_match:
                continue
            person.birth_place = information[match.end():end_of_place_match.start()].strip()
        else:
            # birth place comes before date 
            person.birth_place = information[end_of_name:match.start()-1].strip()
        
        person.id = sha256(person.first_name + person.last_name + person.birth_date + person.birth_place)
        position.person_id = person.id

        persons.append(person)
        positions.append(position)
    return {
        "persons": persons,
        "positions": positions
    }

company_name_regex = re.compile("^(?P<name>[^,;]*?),")
company_business_address_regex = re.compile("Geschäftsanschrift: (?P<street>.+?), (?P<zipcode>\d{5}) (?P<city>.+?)[\.;]")
company_address_regex = re.compile(r'\s+.*?, (?P<street>.+?), (?P<zipcode>\d{5}) (?P<city>.+?)\.')
company_description_regex = re.compile("Gegenstand(?: des Unternehmens)?: (?P<description>.+?.)\.")
company_capital_stock_regex = re.compile("[kK]apital: (?P<value>[\d.,]+) (?P<currency>[A-Z]+?)[\.;]")

def extract_company(information: str) -> dict:
    name_match = company_name_regex.search(information)
    if name_match:
        company = RBCompany()
        company.name = name_match.group("name").strip()
        company.std_name = standardize_company_name(company.name)
        company.id = company_id_generator(company.name)
        last_match_position = name_match.end()

        address_match = company_business_address_regex.search(information, name_match.end())
        if address_match:
            company.address.city = address_match.group("city")
            company.address.zipcode = address_match.group("zipcode")
            company.address.street = address_match.group("street")
            last_match_position = max(last_match_position, address_match.end())
        else:
            address_match = company_address_regex.search(information, name_match.end())
            if address_match:
                company.address.city = address_match.group("city")
                company.address.zipcode = address_match.group("zipcode")
                company.address.street = address_match.group("street")

        description_match = company_description_regex.search(information, name_match.end())
        if description_match:
            company.description = description_match.group("description")
            last_match_position = max(last_match_position, description_match.end())

        capital_stock_match = company_capital_stock_regex.search(information, name_match.end())
        if capital_stock_match:
            company.capital_stock.value = atof(capital_stock_match.group("value"))
            company.capital_stock.currency = capital_stock_match.group("currency")
            last_match_position = max(last_match_position, capital_stock_match.end())
        # positions will be inserted after person extraction

        return {
            "company": company,
            "end_of_match": last_match_position
        }
    else:
        return None
