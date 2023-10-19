from abc import ABC, abstractmethod
from logging import debug
from pathlib import Path
import re

from src.buckets import Bucket
from src.input_bounds import InputBounds
from src.utils.string import add_prefix_each_line, clean
from src.utils.networks import NN
from src.utils.string import alphabet_order

class Program(ABC):
  def __init__(self, path: Path, silent: bool=False):
    pass

  @abstractmethod
  def get_variables(self) -> list[str]:
    pass

class SPLProgram(Program):
  def __init__(self, path: Path, silent: bool=False):
    self.path = path
    self.name = self.path.stem
    self.content = self.path.read_text().strip()

    if not silent:
      debug(f'Program "{self.name}"')
      debug(f'Path "{self.path}"')
      # debug('Content:\n' + add_prefix_each_line(self.content))
      debug(f'Variables: {", ".join(self.get_variables())}')

  def __str__(self):
    return f'Program "{self.name}"\nPath "{self.path}"\nContent: "{self.content}"'
  
  def replace_input_bounds(self, input_bounds: InputBounds, dir: Path) -> 'SPLProgram':
    match = '// INPUTBOUNDS'
    if self.content.count(match) != 1:
      raise Exception(f'Could not find "{match}" in {self.path}')
    
    ctx = input_bounds.to_target()
    assert isinstance(ctx, str)
    return SPLProgram.create_from_content(
      self.content.replace(match, ctx),
      dir / (self.name + '_inputbounds.spl'))
  
  def replace_bucket(self, bucket: Bucket, dir: Path) -> 'SPLProgram':
    match = '// BUCKET'
    if self.content.count(match) != 1:
      raise Exception(f'Could not find "{match}" in {self.path}')
    
    return SPLProgram.create_from_content(
      self.content.replace(match, bucket.to_spl()),
      dir / (self.name + f'_bucket{bucket.id}.spl'))
  
  @staticmethod
  def create_from_content(content: str, file_path: Path):
    file_path.write_text(content)
    return SPLProgram(file_path, silent=True)
  
  def get_variables(self) -> list[str]:
    """
      Program of example:
      var x : int, y : int, result : int;
      begin
        // INPUTBOUNDS
        while x > 0 do
          x = x + y - 5;
          y = -2 * y;
        done;
        result = y;
        // BUCKET
      end

      The variables are: ['x', 'y', 'result'] between the keyword var and ;

      Each variable is followed by semi-colon and the type of the variable.
    """
    variable_match = re.findall(r'var (.+);', self.content)[0]
    variables_and_types = clean(variable_match).split(',')
    variables = [x.split(':')[0] for x in variables_and_types]
    return variables

  def unroll_loops(self, number_of_unrollings_each: int, dir: Path, unroll_within_loop: bool= False) -> 'SPLProgram':
    if number_of_unrollings_each == 0:
      debug('Not unrolling loops')
      return self

    condition_all = re.findall(r'while (.+) do', self.content)
    body_all = re.findall(re.compile(r'do(.*?)done', re.DOTALL), self.content)
    if len(condition_all) == 0:
      debug('No loop to unroll')
      return self
    
    content = self.content
    for condition, body in zip(condition_all, body_all):
      loop = f'while {condition} do{body}done'
      debug(f'Unrolling {number_of_unrollings_each} times the loop body: "{loop}"')
      number_of_tabs = len(re.findall(r' ', body.split('\n')[-2]))

      unrolling_body = "\n".join(
        f'if {condition} then{body}endif;'.split('\n') * number_of_unrollings_each)
      
      if unroll_within_loop:
        content = content.replace(body, body + unrolling_body + "\n")
      else:
        content = content.replace(loop, unrolling_body + "\n" + loop + "\n")
      
    
    return SPLProgram.create_from_content(
      content,
      dir / (self.name + '_unrolled.spl'))
  
class NetworkProgram(Program):
  def __init__(self, path: Path, silent: bool=False):
    self.path = path
    self.name = self.path.stem
    self.content = self.path.read_text().strip()
    self.nn = NN.read_python(self.path)

    if not silent:
      debug(f'Program "{self.name}"')
      debug(f'Path "{self.path}"')
      # debug('Content:\n' + add_prefix_each_line(self.content))
      debug(f'Variables: found {self.nn.ninputs} input features')

  def get_variables(self) -> list[str]:
    return list(alphabet_order[:self.nn.ninputs])

def read_program(path: Path) -> Program:
  if path.suffix == '.spl':
    return SPLProgram(path)
  elif path.suffix == '.py':
    return NetworkProgram(path)
  else:
    raise Exception(f'Unknown program type for {path}. Supported types are: .spl, .py')