from abc import ABC, abstractmethod
from json import load
from logging import debug
from pathlib import Path

from src.utils.string import add_prefix_each_line


class InputBounds(ABC):
  def __init__(self, path: Path):
    pass
  
  @abstractmethod
  def to_target(self):
    pass

class NetworkInputBounds(InputBounds):
  def __init__(self, path: Path):
    with open(path, 'r') as f:
      ctx = load(f)
    self.lower_bound = ctx['lower_bound']
    self.upper_bound = ctx['upper_bound']

    debug(f'Input bounds: {self.lower_bound} <= x_i <= {self.upper_bound}')

  def to_target(self):
    return self.lower_bound, self.upper_bound
  
  def __str__(self):
    return f'{self.lower_bound} <= x_i <= {self.upper_bound}'

class SPLInputBound:
  def __init__(self, condition: str):
    self.condition = condition

  def __str__(self):
    return self.condition

  def to_spl(self) -> str:
    return f'assume {self.condition};'

class SPLInputBounds(InputBounds):
  def __init__(self, path: Path):
    with open(path, 'r') as f:
      ctx = load(f)
    self.bounds = [SPLInputBound(b) for b in ctx['bounds']]

    debug('Input bounds:\n' + add_prefix_each_line(str(self)))

  def to_spl(self) -> str:
    return '\n  '.join([b.to_spl() for b in self.bounds])
  
  def to_target(self):
    return self.to_spl()
  
  def __str__(self):
    return '\n'.join([str(b) for b in self.bounds])

  def __iter__(self):
    return iter(self.bounds)
  
def read_input_bounds(path: Path) -> InputBounds:
  with open(path, 'r') as f:
    ctx = load(f)
  if ctx['type'] == 'spl':
    return SPLInputBounds(path)
  elif ctx['type'] == 'network':
    return NetworkInputBounds(path)
  else:
    raise ValueError(f'Unknown input bounds type: {ctx["type"]}')
