import re
from typing import List, Union, Dict

def construct_regex(a_list):
      return re.compile('|'.join(["(?<![a-z])" + kw + "(?![a-z])" for kw in a_list]))

def obj_to_str(obj: Union[Dict,str]) -> str:
    ans = ""

    if isinstance(obj,str):
        return obj

    if isinstance(obj, dict):
        for field in obj:
            if obj[field] and isinstance(obj[field], str):
                value = obj[field].strip()+';'
            elif obj[field]:
                value = obj_to_str(obj[field]).strip()

            if len(value)>0:
                ans += value.replace(';;',';')
        return ans
    
    if isinstance(obj, list):
        for e in obj:
            value = obj_to_str(e).strip()+';'
            if len(value)>0:
                ans += value.replace(';;',';')
        return ans


