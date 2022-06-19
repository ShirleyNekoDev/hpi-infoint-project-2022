
import re
from Crypto.Hash import SHA256

alphanumeric_regex = re.compile("[^a-z0-9]")

def company_id_generator(company_name: str) -> str:
    key = company_name[0:company_name.find("(")]
    key = key.replace("&", "und").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    key = alphanumeric_regex.sub("", key.casefold())
    return sha256(key)

def sha256(string: str) -> str:
    hash = SHA256.new()
    hash.update(string.encode())
    return hash.hexdigest()

test_str = "Paula´s & Paul Pauß' Würstchenbude e.V. Co KG (haftungsbeschränkt) (ehemals Dieters Bratwurstbutze)"
print(company_id_generator(test_str))
