from abc import ABC, abstractmethod
import json
from pathlib import Path

from src.program import Program
from src.buckets import Bucket
from src.input_bounds import InputBounds
from src.abstract_domains.abstract_domain import AbstractDomain


TMP_DIR = Path('.tmp')

def read_engine_conf(conf_path: Path):
  # read json conf file, required "path"
  with open(conf_path, 'r') as f:
    conf = json.load(f)
  if 'path' not in conf:
    raise Exception(f'Engine conf file {conf_path} does not contain "path"')
  return conf

class Engine(ABC):
  @abstractmethod
  def __init__(self, program: Program, input_bounds: InputBounds):
    pass

  @abstractmethod
  def run(self, bucket: Bucket) -> AbstractDomain:
    pass

  @abstractmethod
  def get_variables(self) -> list[str]:
    pass