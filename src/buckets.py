from json import load
from logging import debug, error, warning
from pathlib import Path
from src.utils.colors import ENDC, RED

from src.utils.string import add_prefix_each_line, clean, represents_integer


class Buckets:
  def __init__(self, path: Path):
    with open(path, 'r') as f:
      ctx = load(f)

    self.interactive = False
    self.type = ctx['type']

    try:
      if ctx['type'] == "direct":
        self.buckets = [Bucket(b, id=i) for i, b in enumerate(ctx['buckets'])]
      elif ctx['type'] == "iterator":
        start, end, step = ctx['start'], ctx['end'], ctx['step']
        rule = ctx['rule']
        ranges = zip(range(start, end, step), range(start+step, end+step, step))
        self.buckets = [Bucket(rule.format(l, min(u, end)), id=i) for i, (l, u) in enumerate(ranges)]
      elif ctx['type'] == "interactive":
        start, step = ctx['start'], ctx['step']
        name = ctx['name']
        self.buckets = [
          Bucket(f"{name} < {start}", id=0),
          Bucket(f"{name} == {start}", id=1),
          Bucket(f"{name} > {start}", id=2)
        ]
        self.interactive = True
        warning(f'Interactive buckets are still experimental. Please confirm your choice [y/n]')
        if input() != 'y':
          raise Exception('Aborted')
      elif ctx['type'] == "network":
        if "labels" in ctx:
          labels = ctx['labels']
        else:
          labels = ["NETWORK_BUCKET"] * ctx['outputs']
        self.buckets = [Bucket(l, i) for i, l in enumerate(labels)]
      else:
        raise Exception(f'Unknown type {ctx["type"]} for buckets. Supported types are: direct, iterator, interactive')
    except KeyError as e:
      error(f'Key {RED}{e}{ENDC} not found in buckets file {RED}{path.name}{ENDC}')
      error("For example, a buckets file should look like this:" + """
  {
    "type": "direct",
    "buckets": [
      "result >= 0 and result < 10",
      "result >= 10 and result < 20"
    ]
  }
  or like this:
  {
    "type": "iterator",
    "start": 0,
    "end": 100,
    "step": 10,
    "rule": "result >= {} and result < {}"
  }
  or
  {
    "type": "interactive",
    "start": 100,
    "step": 100,
    "name": "result"
  }""")
      raise Exception(f'Key {RED}{e}{ENDC} not found in buckets file {RED}{path.name}{ENDC}')

    debug('Buckets:\n' + add_prefix_each_line(str(self)))

  def __str__(self):
    return "\n".join([str(b) for b in self.buckets])
  
  def __iter__(self):
    return iter(self.buckets)
  
  def __getitem__(self, key: int):
    return self.buckets[key]

class Bucket:
  def __init__(self, condition: str, id: int=-1):
    self.condition = condition
    self.id = id

  def to_spl(self) -> str:
    return f'if ({self.condition}) then fail; endif;'

  def __str__(self):
    return f'Bucket {self.id}: {self.condition}'
  
  def range_and_outsiders(self):
    if "or" in self.condition:
      raise Exception(f'Cannot count integers in bucket with or: {self.condition}.\n Please split it into two, or more, buckets')
    constraints = [clean(constr) for constr in self.condition.split("and")]
    equalities = [c for c in constraints if "==" in c]
    upper_bounds, lower_bounds = [], []
    for c in constraints:
      if "<=" not in c and ">=" not in c:
        continue
      a, b = c.split("<=") if "<=" in c else c.split(">=")
      if "<=" in c and represents_integer(b) and not represents_integer(a):
        upper_bounds.append(int(b))
      elif "<=" in c and not represents_integer(b) and represents_integer(a):
        lower_bounds.append(int(a))
      elif ">=" in c and not represents_integer(a) and represents_integer(b):
        lower_bounds.append(int(b))
      elif ">=" in c and represents_integer(a) and not represents_integer(b):
        upper_bounds.append(int(a))
      # else:
      #   error(f'Cannot deal with constraint {RED}{c}{ENDC} in bucket {RED}{self.condition}{ENDC}. Skipping.')
    strict_upper_bounds, strict_lower_bounds = [], []
    for c in constraints:
      if "<" not in c and ">" not in c:
        continue
      a, b = c.split("<") if "<" in c else c.split(">")
      if "<" in c and represents_integer(b) and not represents_integer(a):
        strict_upper_bounds.append(int(b))
      elif "<" in c and not represents_integer(b) and represents_integer(a):
        strict_lower_bounds.append(int(a))
      elif ">" in c and not represents_integer(a) and represents_integer(b):
        strict_lower_bounds.append(int(b))
      elif ">" in c and represents_integer(a) and not represents_integer(b):
        strict_upper_bounds.append(int(a))
      # else:
      #   error(f'Cannot deal with constraint {RED}{c}{ENDC} in bucket {RED}{self.condition}{ENDC}. Skipping.')
      #   continue
    
    if (len(upper_bounds) == 0 and len(strict_upper_bounds) == 0) or (len(lower_bounds) == 0 and len(strict_lower_bounds) == 0):
      no_bounds = True
      exc = f'Cannot count integers in bucket with unlimited bounds: {self.condition}.\n Please add at least a lower and upper bound'
    else:
      no_bounds = False

      lowest_upper_bound = min(upper_bounds) if len(upper_bounds) > 0 else float('inf')
      lowest_strict_upper_bound = min(strict_upper_bounds) if len(strict_upper_bounds) > 0 else float('inf')
      highest_lower_bound = max(lower_bounds) if len(lower_bounds) > 0 else float('-inf')
      highest_strict_lower_bound = max(strict_lower_bounds) if len(strict_lower_bounds) > 0 else float('-inf')

      upper = lowest_upper_bound if lowest_upper_bound < lowest_strict_upper_bound else lowest_strict_upper_bound - 1
      lower = highest_lower_bound if highest_lower_bound > highest_strict_lower_bound else highest_strict_lower_bound + 1
    
    number_of_equalities_outside_range = 0
    points = []
    for e in equalities:
      a, b = e.split("==")
      if represents_integer(a):
        point = int(a)
      elif represents_integer(b):
        point = int(b)
      else:
        error(f'Cannot deal with equality {RED}{e}{ENDC} in bucket {RED}{self.condition}{ENDC}. Skipping.')
        continue
      points.append(point)
      if not no_bounds and not (lower <= point <= upper): # type: ignore
        number_of_equalities_outside_range += 1
      elif no_bounds:
        number_of_equalities_outside_range += 1

    if no_bounds and number_of_equalities_outside_range == 0:
      raise Exception(exc) # type: ignore
    elif no_bounds:
      lower = min(points)
      upper = max(points)
      number_of_equalities_outside_range = 0

    return lower, upper, number_of_equalities_outside_range, points # type: ignore
  
  def range(self):
    lower, upper, _, points = self.range_and_outsiders()
    lowest = min(lower, *points) if len(points) > 0 else lower
    highest = max(upper, *points) if len(points) > 0 else upper
    return lowest, highest

  def count_integers(self):
    lower, upper, number_of_equalities_outside_range, _ = self.range_and_outsiders()
    return upper - lower + 1 - number_of_equalities_outside_range if upper >= lower else 0

