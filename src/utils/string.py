import re


alphabet_order = "xyzwklmnopqrstuvabcdfgh"

VARIABLE_MAPPING = dict()
def from_variable_to_harmonic(variable: str) -> str:
  global VARIABLE_MAPPING
  if variable not in VARIABLE_MAPPING:
    if len(VARIABLE_MAPPING) >= len(alphabet_order):
      raise Exception(f"Too many variables to map: {variable}")
    VARIABLE_MAPPING[variable] = alphabet_order[len(VARIABLE_MAPPING)]
  return VARIABLE_MAPPING[variable]

def from_harmonic_to_variable(harmonic: str) -> str:
  global VARIABLE_MAPPING
  for variable, harmonic_ in VARIABLE_MAPPING.items():
    if harmonic == harmonic_:
      return variable
  raise Exception(f"Unknown harmonic: {harmonic}")

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
