from typing import Any
from src.utils.string import from_dash_to_uppercase, from_uppercase_to_dash


def to_class_name(key: str, suffix: str) -> str:
  return from_dash_to_uppercase(key) + suffix

def choose(class_name: str, env: dict[str, Any], DestClass: type) -> Any:
  if not class_name in env:
    raise Exception(f'Class {class_name} not found in the environment ({env})')
  class_obj: DestClass = env[class_name]
  if not issubclass(class_obj, DestClass):
    raise Exception(f'{class_name} is not a subclass of type {DestClass}')
  return class_obj

def available(suffix: str, env: dict[str, Any]) -> list[str]:
  class_names = [c.removesuffix(suffix) for c in env if c.endswith(suffix) and c != suffix]
  return [from_uppercase_to_dash(c) for c in class_names]