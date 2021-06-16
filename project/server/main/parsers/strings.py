"""String utils."""
import string
import unicodedata
import collections
from typing import Dict
import bs4
import re

def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html).replace("\n", " ")
    return cleantext

def keep_digits(x):
    return "".join([c for c in x if c.isdigit()]).strip()

def remove_punction(s):
    for p in string.punctuation:
        s=s.replace(p,' ').replace('  ',' ')
    return s.strip()

def strip_accents(w: str) -> str:
    """Normalize accents and stuff in string."""
    return "".join(
        c for c in unicodedata.normalize("NFD", w)
        if unicodedata.category(c) != "Mn")

def get_orcid(x: str) -> str:
    ans = x
    for s in x.split('/'):
        v = s.strip()
        if len(v) == 19:
            ans = v
        if len(v) == 16:
            ans = '-'.join([v[0:4], v[4:8], v[8:12], v[12:16]])
    return ans.upper()

def get_doi(x):
    x = x.split('.org/')[-1]
    x = x.split('#')[0]
    return x.lower()

def delete_punct(w: str) -> str:
    """Delete all puctuation in a string."""
    return w.lower().translate(
        str.maketrans(string.punctuation, len(string.punctuation)*" "))


def generate_str_id_from_dict(dct: Dict, sort: bool = True) -> str:
    """Return a normalized stringify dict."""
    return normalize_text(stringify_dict(dct, sort=sort))


def stringify_dict(dct: Dict, sort: bool = True) -> str:
    """Stringify a dictionnary."""
    text = ""
    if sort is True:
        for k, v in collections.OrderedDict(dct).items():
            text += str(v)
    else:
        for k, v in dct.items():
            text += str(v)
    return text

def get_clean_text(elt):
    if(isinstance(elt, bs4.element.NavigableString)):
        text = elt
    if(isinstance(elt, str)):
        text = elt
    elif elt:
        text = elt.get_text(separator=' ')
    else:
        text=''
    text = text.replace("\n", " ")
    text = text.replace("\t", " ")
    text = text.replace('\xa0', ' ')
    text = re.sub('\s+',' ',text).strip()
    return text.strip()

def get_text_class(subsoup, classname):
    elt = subsoup.find_all(class_=classname)
    if len(elt) > 0:
        return ";;;".join([get_clean_text(e) for e in elt])
    return None

def get_text_obj(subsoup, obj):
    elt = subsoup.find_all(obj)
    if len(elt) > 0:
        return ";;;".join([get_clean_text(e) for e in elt])
    return None

def normalize_text(text: str, remove_sep=True) -> str:
    """Normalize string. Delete puctuation and accents."""
    if isinstance(text, str):
        text = text.replace("\n", " ")
        text = text.replace('\xa0', ' ')
        text = delete_punct(text)
        text = strip_accents(text)
        if remove_sep:
            sep = ""
        else:
            sep = " "
        text = sep.join(text.split())
    return text or ""
