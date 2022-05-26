
from distutils.log import info
import json
import re


persons_regex = re.compile("(?P<role>[^;]*?):\s?(?P<index>\d+)\.[\n\\n ]+?(?P<last_name>.*?),\s?(?P<first_name>.*?),\s?\*(?P<birth_date>\d{2}.\d{2}.\d{4}),\s?(?P<birth_place>.*?);\s?(?:[^;]*?);\s?")

def extract_persons(information: str) -> "list[dict]":
    information = information.replace("\n", " ").partition(".  ")[2]
    persons = []
    for match in persons_regex.finditer(information):
        persons.append({
            "role": match.group("role"),
            "index": int(match.group("index")),
            "last_name": match.group("last_name"),
            "first_name": match.group("first_name"),
            "birth_date": match.group("birth_date"),
            "birth_place": match.group("birth_place"),
        })
    return persons

company_name_regex = re.compile("Firma: (?P<name>.+?);")
company_address_regex = re.compile("Geschäftsanschrift: (?P<street>.+?), (?P<zipcode>\d{5}) (?P<city>.+?);")
company_description_regex = re.compile("Gegenstand: (?P<description>.+?) Stamm-")
company_capital_stock_regex = re.compile("Stamm- bzw\. Grundkapital: (?P<value>[\d.,]+) (?P<currency>[A-Z]+?);")

def extract_company(information: str) -> dict:
    name_match = company_name_regex.search(information)
    if name_match:
        address_match = company_address_regex.search(information, name_match.end())
        if not address_match:
            return None
        description_match = company_description_regex.search(information, name_match.end())
        capital_stock_match = company_capital_stock_regex.search(information, name_match.end())
        return {
            "name": name_match.group("name"),
            "description": description_match.group("description") if description_match else None,
            "address": {
                "city": address_match.group("city"),
                "zipcode": address_match.group("zipcode"),
                "street": address_match.group("street"),
            },
            "capital_stock": {
                "value": capital_stock_match.group("value"), # TODO: parse float
                "currency": capital_stock_match.group("currency"),
            } if capital_stock_match else None,
        }
    else:
        return None

def extract(information: str) -> dict:
    return {
        "company": extract_company(information),
        # "persons": extract_persons(information),
    }

def run():
    test_data=[
        "HRB 242356 B: Karl-Marx-Straße 222 Gastro UG (haftungsbeschränkt), Berlin, Karl-Marx-Straße 222, 12055 Berlin. Firma: Karl-Marx-Straße 222 Gastro UG (haftungsbeschränkt); Sitz / Zweigniederlassung: Berlin; Geschäftsanschrift: Karl-Marx-Straße 222, 12055 Berlin; Gegenstand: Gastronomie. Stamm- bzw. Grundkapital: 100,00 EUR; Vertretungsregelung: Ist ein Geschäftsführer bestellt, so vertritt er die Gesellschaft allein. Sind mehrere Geschäftsführer bestellt, wird die Gesellschaft durch sämtliche Geschäftsführer gemeinsam vertreten.  Geschäftsführer: 1.\nRadeva, Elenka, *14.12.1999, Berlin; mit der Befugnis Rechtsgeschäfte mit sich selbst oder als Vertreter Dritter abzuschließen; Rechtsform: Gesellschaft mit beschränkter Haftung; Gesellschaftsvertrag vom: 11.04.2022",
        "HRB 242309 B: Paybackflott UG (haftungsbeschränkt), Berlin, Luisenstraße 33, 12209 Berlin. Firma: Paybackflott UG (haftungsbeschränkt); Sitz / Zweigniederlassung: Berlin; Geschäftsanschrift: Luisenstraße 33, 12209 Berlin; Gegenstand: Der Vertrieb, die Vermietung und die Überlassung von Elektrofahrzeugen; Stamm- bzw. Grundkapital: 1.000,00 EUR; Vertretungsregelung: Ist ein Geschäftsführer bestellt, so vertritt er die Gesellschaft allein. Sind mehrere Geschäftsführer bestellt, wird die Gesellschaft durch sämtliche Geschäftsführer gemeinsam vertreten.  Geschäftsführer: 1.\nElahi, Peyman, *21.09.1987, Berlin; mit der Befugnis Rechtsgeschäfte mit sich selbst oder als Vertreter Dritter abzuschließen; Rechtsform: Gesellschaft mit beschränkter Haftung; Gesellschaftsvertrag vom: 19.04.2022",
        "HRB 242319 B: Delta Spa UG (haftungsbeschränkt), Berlin, Matkowskystraße 2, 10245 Berlin. Firma: Delta Spa UG (haftungsbeschränkt); Sitz / Zweigniederlassung: Berlin; Geschäftsanschrift: Matkowskystraße 2, 10245 Berlin; Gegenstand: Einzelhandel mit naturnahen Körper- und Schönheitspflegemitteln und auf diesen Bereich bezogene Beratungsdienstleistungen; Stamm- bzw. Grundkapital: 2.500,00 EUR; Vertretungsregelung: Ist ein Geschäftsführer bestellt, so vertritt er die Gesellschaft allein. Sind mehrere Geschäftsführer bestellt, wird die Gesellschaft durch sämtliche Geschäftsführer gemeinsam vertreten.  Geschäftsführer: 1.\nNisch, Margret, *21.03.1976, Berlin; mit der Befugnis Rechtsgeschäfte mit sich selbst oder als Vertreter Dritter abzuschließen; Rechtsform: Gesellschaft mit beschränkter Haftung; Gesellschaftsvertrag vom: 26.04.2022",
        "VR 39621 B: Götterfunke - Wirkstatt für Potentialentfaltung e.V., Berlin.",
        "HRB 242308 B: BWC Black Water Consulting UG (haftungsbeschränkt), Berlin, Friedrichstraße 171, 10117 Berlin. Firma: BWC Black Water Consulting UG (haftungsbeschränkt); Sitz / Zweigniederlassung: Berlin; Geschäftsanschrift: Friedrichstraße 171, 10117 Berlin; Gegenstand: Die Erbringung von Marketingleistungen und die Tätigkeit als sog. Tippgeber, d.h. die genehmigungsfreie Vermittlung eines abschlusswilligen Kunden an einen Anbieter gegen Provision in verschiedenen Geschäftsbereichen, u.a. im Bereich Immobilien, Finanz-Makler und Anwälte. Stamm- bzw. Grundkapital: 300,00 EUR; Vertretungsregelung: Ist ein Geschäftsführer bestellt, so vertritt er die Gesellschaft allein. Sind mehrere Geschäftsführer bestellt, wird die Gesellschaft durch sämtliche Geschäftsführer gemeinsam vertreten.  Geschäftsführer: 1.\nPfisterer, Felix, *21.04.1997, Stuttgart; mit der Befugnis Rechtsgeschäfte mit sich selbst oder als Vertreter Dritter abzuschließen; Rechtsform: Gesellschaft mit beschränkter Haftung; Gesellschaftsvertrag vom: 23.03.2022",
        "HRB 242307 B: Sam Chermayeff Office GmbH, Berlin, Zikadenweg 5 a, 14055 Berlin. Firma: Sam Chermayeff Office GmbH; Sitz / Zweigniederlassung: Berlin; Geschäftsanschrift: Zikadenweg 5 a, 14055 Berlin; Gegenstand: Die gemeinsame Berufsausübung der Gesellschafter, die Erbringung von Planungsleistungen, konzeptionelle, gestalterische und technische Entwicklung, Beratung, Planung von Projekten, deren Durchführung und Betreuung, insbesondere die konzeptionelle und gestalterische Planung von Möbelstücken und Dekorationen für den Innen- und Außenbereich, sowie die Beratung auf diesem Gebiet. Stamm- bzw. Grundkapital: 25.000,00 EUR; Vertretungsregelung: Ist ein Geschäftsführer bestellt, so vertritt er die Gesellschaft allein. Sind mehrere Geschäftsführer bestellt, wird die Gesellschaft durch sämtliche Geschäftsführer gemeinsam vertreten.  Geschäftsführer: 1.\nChermayeff, Sam Clark, *20.09.1981, Berlin; Rechtsform: Gesellschaft mit beschränkter Haftung; Gesellschaftsvertrag vom: 31.01.2022",
        "HRB 242346 B: Gruttmann Capital GmbH, Berlin, Kurfürstendamm 132 A, 10711 Berlin. Firma: Gruttmann Capital GmbH; Sitz / Zweigniederlassung: Berlin; Geschäftsanschrift: Kurfürstendamm 132 A, 10711 Berlin; Gegenstand: Die Verwaltung eigenen Vermögens, insbesondere der Erwerb und die Verwaltung von Grundvermögen und von Beteiligungen im In- und Ausland, im eigenen Namen und auf eigene Rechnung, nicht als Dienstleistung für Dritte. Stamm- bzw. Grundkapital: 25.000,00 EUR; Vertretungsregelung: Ist ein Geschäftsführer bestellt, so vertritt er die Gesellschaft allein. Sind mehrere Geschäftsführer bestellt, wird die Gesellschaft gemeinschaftlich durch zwei Geschäftsführer oder durch einen Geschäftsführer in Gemeinschaft mit einem Prokuristen vertreten.  Geschäftsführer: 1.\nGruttmann, Britta, *31.12.1974, Berlin; mit der Befugnis die Gesellschaft allein zu vertreten\nmit der Befugnis Rechtsgeschäfte mit sich selbst oder als Vertreter Dritter abzuschließen; Rechtsform: Gesellschaft mit beschränkter Haftung; Gesellschaftsvertrag vom: 22.02.2022",
        "HRB 242327 B: ELJAKO-AL GmbH, Berlin, Kurfürstendamm 226, 10719 Berlin. Firma: ELJAKO-AL GmbH; Sitz / Zweigniederlassung: Berlin; Geschäftsanschrift: Kurfürstendamm 226, 10719 Berlin; Gegenstand: Bauarbeiten für Wohn- und Nichtwohngebäude, Kauf und Einbau von Tischlerarbeiten, Handel mit Immobilien, Gestaltung und Konstruktion der Fassade. Stamm- bzw. Grundkapital: 25.000,00 EUR; Vertretungsregelung: Ist ein Geschäftsführer bestellt, so vertritt er die Gesellschaft allein. Sind mehrere Geschäftsführer bestellt, wird die Gesellschaft gemeinschaftlich durch zwei Geschäftsführer oder durch einen Geschäftsführer in Gemeinschaft mit einem Prokuristen vertreten.  Geschäftsführer: 1.\nKolodziejski, Jacek Slawomir, *10.05.1949, Warzawa/Polen; mit der Befugnis die Gesellschaft allein zu vertreten\nmit der Befugnis Rechtsgeschäfte mit sich selbst oder als Vertreter Dritter abzuschließen; Geschäftsführer: 2.\nMichalczyk, Jacek Tadeusz, *22.01.1974, Piaseczno/Polen; mit der Befugnis die Gesellschaft allein zu vertreten\nmit der Befugnis Rechtsgeschäfte mit sich selbst oder als Vertreter Dritter abzuschließen; Rechtsform: Gesellschaft mit beschränkter Haftung; Gesellschaftsvertrag vom: 02.03.2022",
        "HRA 60230 B: RGP3 Leipzig GmbH & Co. KG, Berlin, Marburger Straße 2, 10789 Berlin (Unternehmensgegenstand: Der Erwerb, die Verwaltung, das Halten, der Verkauf, die Finanzierung und Refinanzierung, der Betrieb und die Vermietung und Verpachtung von Grundstücken, insbesondere, aber nicht ausschließlich in Leipzig, jeweils ausschließlich im eigenen Namen und für eigene Rechnung.). Firma: RGP3 Leipzig GmbH & Co. KG; Sitz / Zweigniederlassung: Berlin; Geschäftsanschrift: Marburger Straße 2, 10789 Berlin; Vertretungsregelung: Jeder persönlich haftende Gesellschafter vertritt die Gesellschaft allein.  Persönlich haftender Gesellschafter: 1.\nREALITY GERMANY General 3 GmbH, Berlin\n(Amtsgericht Charlottenburg, HRB 223027 B); mit der für sich sowie ihre Geschäftsführer geltenden Befugnis Rechtsgeschäfte mit sich selbst oder als Vertreter Dritter abzuschließen; Rechtsform: Kommanditgesellschaft",
        "HRB 242317 B: Baxtum Ventures UG (haftungsbeschränkt), Berlin, c/o Holy Energy GmbH, Rosenthaler Straße 13, 10119 Berlin. Firma: Baxtum Ventures UG (haftungsbeschränkt); Sitz / Zweigniederlassung: Berlin; Geschäftsanschrift: c/o Holy Energy GmbH, Rosenthaler Straße 13, 10119 Berlin; Gegenstand: Der Erwerb sowie die Verwaltung, Verwertung und Veräußerung von Vermögensbeteiligungen aller Art im eigenen Namen und für eigene Rechnung, nicht für Dritte und unter Ausschluss von Tätigkeiten, die einer Erlaubnis nach dem Kreditwesengesetz oder dem Kapitalanlagegesetzbuch bedürfen. Stamm- bzw. Grundkapital: 900,00 EUR; Vertretungsregelung: Ist ein Geschäftsführer bestellt, so vertritt er die Gesellschaft allein. Sind mehrere Geschäftsführer bestellt, wird die Gesellschaft gemeinschaftlich durch zwei Geschäftsführer oder durch einen Geschäftsführer in Gemeinschaft mit einem Prokuristen vertreten.  Geschäftsführer: 1.\nHorsch, Mathias Karl Ulrich, *02.09.1994, Berlin; mit der Befugnis die Gesellschaft allein zu vertreten\nmit der Befugnis Rechtsgeschäfte mit sich selbst oder als Vertreter Dritter abzuschließen; Geschäftsführer: 2.\nJost, Frederick Alexander, *31.08.1994, Berlin; mit der Befugnis die Gesellschaft allein zu vertreten\nmit der Befugnis Rechtsgeschäfte mit sich selbst oder als Vertreter Dritter abzuschließen; Geschäftsführer: 3.\nNaß, Philipp Norbert, *24.11.1994, Berlin; mit der Befugnis die Gesellschaft allein zu vertreten\nmit der Befugnis Rechtsgeschäfte mit sich selbst oder als Vertreter Dritter abzuschließen; Rechtsform: Gesellschaft mit beschränkter Haftung; Gesellschaftsvertrag vom: 05.05.2022"
    ]
    for info_str in test_data:
        if info_str.startswith("HRB"):
            info = extract(info_str)
            print(json.dumps(info, indent=2, default=str))
        else:
            # ignore
            pass

if __name__ == "__main__":
    run()
