
import re
from Crypto.Hash import SHA256
from cleanco import basename
from unidecode import unidecode

alphanumeric_regex = re.compile("[^a-z0-9]")

def standardize_company_name(company_name: str) -> str:
    bracket_index = company_name.find("(")
    if bracket_index > 0:
        company_name = company_name[0:company_name.find("(")]
    company_name = company_name.replace("&", "und").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    company_name = unidecode(company_name)
    company_name = basename(company_name).casefold()
    company_name = alphanumeric_regex.sub("", company_name)
    return company_name

def company_id_generator(company_name: str) -> str:
    return sha256(standardize_company_name(company_name))

def sha256(string: str) -> str:
    hash = SHA256.new()
    hash.update(string.encode())
    return hash.hexdigest()

# test_str = "Paula´s & Paul Pauß' Würstchenbude e.V. Co KG (haftungsbeschränkt) (ehemals Dieters Bratwurstbutze)"
# print(company_id_generator(test_str))
