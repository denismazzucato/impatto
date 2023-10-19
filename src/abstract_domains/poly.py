from logging import debug, warning
import numpy as np
import re
import sympy as sp
from enum import Enum
from itertools import product
import networkx as nx

from src.utils.lp import SolverError, solve
from src.utils.progress_bar import subprogress_bar
from src.abstract_domains.abstract_domain import AbstractDomain

eps = 1e-5


class Status(Enum):
  TOP = 'top'
  BOTTOM = 'bottom'
  UNKNOWN = 'unknown'

def eliminate_single(index: int, A: np.ndarray, b: np.ndarray, atol: float = 1e-10) -> tuple[np.ndarray, np.ndarray]:
  assert(index < A.shape[1])
  assert(A.shape[0] == b.shape[0])

  phi_positive=[i for i in range(A.shape[0]) if A[i,index]>=atol] # list of positive var entries
  phi_negative=[i for i in range(A.shape[0]) if A[i,index]<=-atol]  # list of negative var entries
  phi_core=[i for i in range(A.shape[0]) if abs(A[i,index])<atol]  # list of zero var entries
  s_smaller=np.diag(1/A[phi_positive,index]) # positive
  s_larger=np.diag(1/A[phi_negative,index]) # negative
  A_positive=np.dot(s_smaller,A[phi_positive,:]) # A of postives scaled by var entries
  b_positive=np.dot(s_smaller,b[phi_positive,:])
  A_negative=np.dot(s_larger,A[phi_negative,:])
  b_negative=np.dot(s_larger,b[phi_negative,:]) 
  """ We have A_positive x_other + x_r <= b_positive
  --> We have A_negative x_other + x_r >= b_negative
  --> We have b_postive - b_negative >= (A_neg - A _pos) * x_other (all combinations)
  """
  A_new=np.empty((0,A.shape[1]-1))
  b_new=np.empty((0,1))
  other=list(range(0,index))+list(range(index+1,A.shape[1]))
  for i in range(len(phi_positive)):
    for j in range(len(phi_negative)):
      alpha=(-A_negative[j,other]+A_positive[i,other]).reshape(1,len(other))
      beta=b_positive[i,:]-b_negative[j,:]
      A_new=np.vstack((A_new,alpha))
      b_new=np.vstack((b_new,beta))
  if phi_core!=[]:
    A_new=np.vstack((A_new,A[phi_core,:][:,other]))
    b_new=np.vstack((b_new,b[phi_core,:]))
  return A_new,b_new

def parse_polyhedra_constraints(variables: list[str], constraints: list[str]) -> tuple[list[str], np.ndarray, np.ndarray]:
  A = []  # Coefficient matrix
  b = []  # Right-hand side vector

  sym_variables = sp.symbols(variables)
  
  for constraint in constraints:
    try:
      parsed_constraint = sp.parse_expr(constraint, transformations='all')
      if parsed_constraint == True:
        continue
      operator = parsed_constraint.rel_op
      normalized_constraint = sp.simplify(parsed_constraint.lhs - parsed_constraint.rhs)
      coefficients_dict = normalized_constraint.as_coefficients_dict()
      coefficients = np.array([coefficients_dict[variable] for variable in sym_variables])
      free_coeff = -(coefficients_dict[1])
    except Exception as e:
      raise Exception(f'Error {e} while parsing constraint:\n{constraint}\nOver constraints:\n{constraints}')
    
    if operator == "<=":
      A.append(coefficients)
      b.append(free_coeff)
    elif operator == ">=":
      A.append(-coefficients)
      b.append(-free_coeff)
    elif operator == "==":
      A.append(coefficients)
      b.append(free_coeff)
      A.append(-coefficients)
      b.append(-free_coeff)
    elif operator == "<":
      A.append(coefficients)
      b.append(free_coeff - eps)
    elif operator == ">":
      A.append(-coefficients)
      b.append(-free_coeff - eps)

    elif operator == "<" or operator == ">":
      raise Exception(f'Operator {operator} not supported at the moment')
    else:
      raise Exception(f'Unknown operator {operator}')

  A = np.array(A)
  b = np.array(b)
  return variables, A, b

class Poly(AbstractDomain):

  def __init__(self, variables: list[str], A: np.ndarray, b: np.ndarray):
    self.variables = variables
    self.A = A
    self.b = b
    self.status = Status.UNKNOWN

  @staticmethod
  def from_string_constraints(variables: list[str], variable_mapping,string_constraints: list[str]) -> 'Poly':
    if string_constraints == []:
      warning("Empty list of constraints, returning bottom")
      return Poly.bottom()
    replaced_string_constriaints = []
    for constraint in string_constraints:
      for variable in variables:
        constraint = constraint.replace(variable, variable_mapping(variable))
      replaced_string_constriaints.append(constraint)
    return Poly(*parse_polyhedra_constraints(variables, replaced_string_constriaints))

  @staticmethod
  def top() -> 'Poly':
    poly = Poly([], np.array([]), np.array([]))
    poly.status = Status.TOP
    return poly
  
  @staticmethod
  def bottom() -> 'Poly':
    poly = Poly([], np.array([]), np.array([]))
    poly.status = Status.BOTTOM
    return poly

  def eliminate(self, variable: str) -> 'Poly':
    if self.is_bottom() or self.is_top():
      return self
    index = self.variables.index(variable)
    if index == -1:
      raise Exception(f'Variable {variable} not found in {self.variables}')
    A, b = eliminate_single(index, self.A, self.b.reshape(-1, 1))
    variables = self.variables[:index] + self.variables[index+1:]
    return Poly(variables, A, b)

  def intersect(self, other: 'Poly') -> 'Poly':
    if self.is_bottom() or other.is_bottom():
      return Poly.bottom()
    assert(self.variables == other.variables)
    A = np.vstack((self.A, other.A))
    b = np.vstack((self.b, other.b))
    return Poly(self.variables, A, b)

  def is_bottom(self) -> bool:
    if self.status == Status.BOTTOM:
      return True
    if self.status == Status.TOP:
      return False
    obj = np.array([0] * len(self.variables))
    try:
      result, _ = solve(obj, self.A, self.b)
    except SolverError:
      self.status = Status.TOP
      return False
    if not result:
      self.status = Status.BOTTOM
      return True
    return False

  def is_top(self) -> bool:
    if self.status == Status.TOP:
      return True
    if self.status == Status.BOTTOM:
      return False
    return False # TODO: how to check if it is top? Need domain bounds

  def to_inequalities(self) -> list[sp.core.relational.LessThan]:
    # assert(not self.is_bottom() and not self.is_top())
    sym = sp.Matrix(self.variables)
    A = sp.Matrix(self.A)
    b = sp.Matrix(self.b)
    acc = []
    for lhs, rhs in zip(A * sym, b): # type: ignore # b does not have __iter__
      acc.append(lhs <= rhs)
    return acc

  def _str(self):
    inequalities = [str(x) for x in self.to_inequalities()]
    return " && \n".join(inequalities)

  def __str__(self):
    if self.is_bottom():
      return "bottom"
    if self.is_top():
      return "top"
    inequalities = [str(x) for x in self.to_inequalities()]
    return " && \n".join(inequalities)
  
  def count_integers_between(self, lowerbound:int=0, upperbound:int=20) -> int:
    if self.is_bottom():
      return 0
    if self.is_top():
      return int('inf')
    k = len(self.variables)
    points = list(product(*(range(lowerbound, upperbound) for i in range(k))))
    count = [all([np.dot(A, point) <= b for A, b in zip(self.A, self.b)]) for point in points]
    return sum(count)
  
def intersecting_pairs(polys:list[Poly]) -> list[tuple[int, int]]:
  # find all the poly that intersect
  intersecting = set()
  for i in range(len(polys)):
    for j in range(len(polys)):
      if i != j and (j, i) not in intersecting and polys[i].does_intersect(polys[j]):
        intersecting.add((i, j))
  return list(intersecting)

def intersecting_cliques(polys:list[Poly]) -> dict[int, set[frozenset[int]]]:
  edges = intersecting_pairs(polys)
  graph = nx.Graph(edges)
  cliques = list(nx.find_cliques(graph))

  acc = {}
  for clique in cliques:
    for node in clique:
      current = frozenset(set(clique) - { node })
      if node not in acc:
        acc[node] = { current }
      else:
        acc[node].add(current)

  return acc

def intersecting_components(polys:list[Poly]) -> dict[int, set[int]]:
  warning("Deprecated")
  # find all the poly that intersect
  intersecting = {}
  for i in range(len(polys)):
    intersecting[i] = set()
    for j in range(len(polys)):
      if i != j and polys[i].does_intersect(polys[j]):
        intersecting[i].add(j)
  return intersecting

  acc = intersecting_cliques(polys)
  flatten = lambda l: {item for sublist in l for item in sublist}
  return {k: flatten(v) for k, v in acc.items()}