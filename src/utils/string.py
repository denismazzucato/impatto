import re


alphabet_order = "xyzwklmnopqrstuvabcdfgh"

def from_dash_to_uppercase(name: str) -> str:
  return "".join([word.capitalize() for word in name.split("-")])

def from_uppercase_to_dash(name: str) -> str:
  return "-".join([word.lower() for word in re.findall('[A-Z][^A-Z]*', name)])

def add_prefix_each_line(text: str, prefix: str="  ") -> str:
  return "\n".join([prefix + line for line in text.split("\n")])

def clean(text: str) -> str:
  return ''.join(text.split())

def cut_between(text:str, start: int=100, end: int=100) -> str:
  if len(text) <= start + end:
    return text
  return text[:start] + " ... " + text[-end:]

def represents_integer(s):
  try:
    int(s)
    return True
  except ValueError:
    return False
