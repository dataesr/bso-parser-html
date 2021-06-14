import re
import json

from strings import normalize_text

def construct_regex(a_list):
      return re.compile('|'.join(["(?<![a-z])" + kw + "(?![a-z])" for kw in a_list]))

def construct_regex_simple(a_list):
      return re.compile('|'.join([kw for kw in a_list]))
  

country_keywords = json.load(open("project/server/main/parsing/country_keywords.json", "r"))
country_keywords_forbidden = json.load(open("project/server/main/parsing/country_forbidden.json", "r"))

country_regex = {}
country_regex_forbidden = {}
for country in country_keywords:
    country_regex[country] = construct_regex(country_keywords[country])

for country in country_keywords_forbidden:
    country_regex_forbidden[country] = construct_regex_simple(country_keywords_forbidden[country])

def detect_country(text):
    detected_countries = []
    text_normalized = normalize_text(text, remove_sep=False)

    for country in country_keywords:
        if re.search(country_regex[country], text_normalized):
            if country in country_regex_forbidden and re.search(country_regex_forbidden[country], text_normalized):
                continue
            detected_countries.append(country)

    if len(detected_countries) > 0:
        return list(set(detected_countries))

    if len(detected_countries) == 0:
        print("///// ", end='', flush=True)
        print(text + " ///// ", flush=True)
        detected_countries.append('UNK')

    return list(set(detected_countries))
