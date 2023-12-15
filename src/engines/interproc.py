from logging import debug
from pathlib import Path
import re
import subprocess
from src.buckets import Bucket

from src.engines.base import TMP_DIR, read_engine_conf, Engine
from src.program import Program, SPLProgram
from src.input_bounds import InputBounds, SPLInputBounds
from src.utils.string import clean, from_variable_to_harmonic
from src.abstract_domains.poly import Poly


def get_variables(pres):
  variables = []
  for pre in pres:
    variables += pre.variables
  return list(set(variables))

class InterprocInv:
  def __init__(self, variables: list[str], ctx: str):
    # e.g., ctx = (L3 C5) [|x=0; -y+19>=0; y>=0|]
    # e.g., ctx = (L8 C14) bottom
    # e.g., ctx = (L6 C16)
    #  [|-930257069563x+4349059158133y+17674884321697>=0; -x+19>=0; -y+19>=0;
    #    x-1>=0|]
    self.ctx = re.sub(r'\s+', ' ', ctx) # remove extra spaces
    self.l = int(re.findall(r'L(\d+)', ctx)[0])
    self.c = int(re.findall(r'C(\d+)', ctx)[0])
    self.is_bottom = 'bottom' in ctx
    self.is_top = 'top' in ctx
    self.variables = variables
    matches = re.search(r'\[\|([^|]+)\|\]', ctx)
    if matches:
      constraints = matches.group(1).strip()
      raw_poly = [clean(constraint) for constraint in constraints.split(';')]
    else:
      raw_poly = []
    self.raw_poly = raw_poly

  def poly(self, variable_mapping=from_variable_to_harmonic):
    if self.is_bottom:
      return Poly.bottom()
    if self.is_top:
      return Poly.top()
    return Poly.from_string_constraints(self.variables, variable_mapping, self.raw_poly)

  def satisfiable(self):
    return not self.is_bottom and not self.poly().is_bottom()
  
  def __str__(self):
    return self.ctx

class InterprocEngine(Engine):
  def __init__(self, program: Program, inputs: InputBounds, config:Path=Path("./engines/interproc.json")):
    assert(isinstance(program, SPLProgram))
    assert(isinstance(inputs, SPLInputBounds))

    TMP_DIR.mkdir(parents=True, exist_ok=True)
    conf = read_engine_conf(config)
    self.engine_path = Path(conf['path'])
    self.args = conf["args"]
    if not self.engine_path.exists():
      raise Exception(f'Engine path for interproc ({self.engine_path}) does not exist')
    
    self.base_program = program.replace_input_bounds(inputs, TMP_DIR)
    if conf.get('unroll', False):
      self.base_program = self.base_program.unroll_loops(int(conf['unroll']), TMP_DIR)

    self.inv: None | InterprocInv = None

  def create_command(self, program: SPLProgram):
    return [str(self.engine_path.absolute()), *self.args, str(program.path.absolute())]

  @staticmethod
  def parse_interproc_output(variables: list[str], output: str) -> InterprocInv:
    last_analysis = output.split("Annotated program after ")[-1]

    # retrieve the content of all the comments
    comments = r"\/\*(.*?)\*\/"
    matches = [InterprocInv(variables, x) for x in re.findall(comments, last_analysis, re.DOTALL)]

    # the minimum is the necessary precondition
    necessary_precondition = min(matches, key=lambda x: x.l)
    return necessary_precondition

  def run(self, bucket: Bucket) -> Poly:
    variables = self.base_program.get_variables()
    program = self.base_program.replace_bucket(bucket, TMP_DIR)

    command = self.create_command(program)
    str_command = ' '.join(command)
    debug(f'Running interproc: \n  > {str_command}')
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error:
      raise Exception(f'Error running command: {str_command}\n\n{error}')
    else:
      debug('Command executed successfully')
    
    self.inv = InterprocEngine.parse_interproc_output(variables, output.decode('utf-8'))
    self.poly = self.inv.poly()

    return self.poly
  
  def get_variables(self) -> list[str]:
    return [str(x) for x in self.poly.variables]
  
class InterprocFastEngine(InterprocEngine):
  def __init__(self, program: Program, inputs: InputBounds):
    super().__init__(program, inputs, Path("./engines/interproc-fast.json"))

class InterprocStrongEngine(InterprocEngine):
  def __init__(self, program: Program, inputs: InputBounds):
    super().__init__(program, inputs, Path("./engines/interproc-strong.json"))