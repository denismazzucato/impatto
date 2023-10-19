import numpy as np
from scipy.optimize import linprog
from typing import Callable
from logging import warning
import pulp
import gurobipy as gb
from gurobipy import GRB

from scipy.linalg import LinAlgWarning
import warnings
warnings.filterwarnings(action='ignore', category=LinAlgWarning, module='scipy')
warnings.filterwarnings(action='ignore', category=RuntimeWarning, module='scipy')
warnings.filterwarnings(action='ignore', category=Warning)

class SolverError(Exception):
  pass

def timeout(seconds):
  def decorate(func):
    def wrapper(*args, **kwargs):
      import signal
      def handler(signum, frame):
        raise TimeoutError()
      signal.signal(signal.SIGALRM, handler)
      signal.alarm(seconds)
      try:
        result = func(*args, **kwargs)
      except TimeoutError:
        result = None
      finally:
        signal.alarm(0)
      return result
    return wrapper
  return decorate

class Scheduler:
  def __init__(self):
    self.tasks: list[Callable[[np.ndarray, np.ndarray, np.ndarray], None | tuple[bool, np.ndarray]]] = []
    
  def schedule(self, task: Callable[[np.ndarray, np.ndarray, np.ndarray], None | tuple[bool, np.ndarray]]) -> 'Scheduler':
    self.tasks.append(task)
    return self

  def call(self, obj: np.ndarray, A: np.ndarray, b: np.ndarray) -> tuple[None | bool, np.ndarray]:
    at_least_one_false = False
    for task in self.tasks:
      try:
        result = task(obj, A, b)
      except ValueError as e:
        warning(f'ValueError: {e}')
        result = None
      if result is not None and result[0]:
        return result
      if result is not None and not result[0]:
        at_least_one_false = True
    return (None if not at_least_one_false else False), np.array([])
    

SECONDS = 10

@timeout(SECONDS)
def scipy_solve_interior_point(obj: np.ndarray, A: np.ndarray, b: np.ndarray) -> tuple[bool, np.ndarray]:
  result = linprog(c=obj, A_ub=A, b_ub=b, bounds=(-100000, 100000), method='interior-point')
  return result.success, result.x

@timeout(SECONDS)
def scipy_solve_simplex(obj: np.ndarray, A: np.ndarray, b: np.ndarray) -> tuple[bool, np.ndarray]:
  result = linprog(c=obj, A_ub=A, b_ub=b, bounds=(-100000, 100000), method='revised simplex')
  return result.success, result.x

@timeout(SECONDS)
def pulp_solve(obj: np.ndarray, A: np.ndarray, b: np.ndarray) -> tuple[bool, np.ndarray]:
  lp_problem = pulp.LpProblem("Matrix_LP_Problem", pulp.LpMaximize)
  num_variables = len(obj)
  variables = [pulp.LpVariable(f"x{i}", lowBound=0) for i in range(1, num_variables + 1)]
  lp_problem += pulp.lpDot(obj, variables), "Z"
  for i in range(len(A)):
    lp_problem += pulp.lpDot(A[i], variables) <= b[i], f"Constraint_{i + 1}"
  solver = pulp.getSolver('COIN_CMD', msg=0, timeLimit=SECONDS)
  lp_problem.solve(solver)
  return lp_problem.status == 1, np.array([x.varValue for x in variables])

@timeout(SECONDS)
def gurobi(obj: np.ndarray, A: np.ndarray, b: np.ndarray) -> tuple[bool, np.ndarray]:
  # def solve(self, obj, sense, bbox=DEFAULT_BBOX):
  bbox = (-100000, 100000)
  nvars = len(obj)
  # status, objval, xval
  with gb.Env(empty=True) as env:
    env.setParam('OutputFlag', 0)
    env.start()
    with gb.Model(env=env) as m:
      x = m.addMVar(nvars, lb=bbox[0], ub=bbox[1])
      m.addConstr(A @ x <= b)
      m.setObjective(obj @ x, GRB.MINIMIZE)
      m.optimize()
      return m.status == GRB.OPTIMAL, x.X if m.status == GRB.OPTIMAL else np.array([])

def solve(obj: np.ndarray, A: np.ndarray, b: np.ndarray) -> tuple[bool, np.ndarray]:
  success, value = Scheduler() \
    .schedule(scipy_solve_interior_point) \
    .schedule(scipy_solve_simplex) \
    .call(obj, A, b)
  if success is None:
    warning('All solvers failed, raising top.')
    raise SolverError()
    return False, value
  return success, value
  