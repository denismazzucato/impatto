from functools import reduce
from src.abstract_domains.abstract_domain import AbstractDomain
from src.abstract_domains.disjunctive_poly import DisjunctivePoly
from src.abstract_domains.poly import intersecting_cliques, intersecting_components
from src.buckets import Buckets
from src.impacts.intersections import Analysis
from src.utils.flags import get_older_algorithm
from src.utils.progress_bar import progress_bar, subprogress_bar


def all_intersections(states, index, old=False) -> int:
  assert(isinstance(states, list))
  assert(all([isinstance(s, DisjunctivePoly) for s in states]))
  if len(states) != 2:
    raise Exception("Only 2 buckets supported in changes")

  projected = [state.eliminate(index) for state in states]

  # if not original:
  #   count = 0
  #   for i in [0, 1]:
  #     this = projected[i]
  #     other = projected[0 if i == 1 else 1]
  #     for p in this.polyhedra:
  #       intersecting_impacts_without_target = intersecting_cliques([p, *other.polyhedra])
  #       xss = intersecting_impacts_without_target.values()
  #       local_max = max([len(xs) for xs in xss], default=0)
  #       count = max(count, local_max)
  #       # print(local_max, count)
  #   return count
  
  if not old:
    xs = projected[0].polyhedra
    ys = projected[1].polyhedra
    abs_maximum = max(len(xs), len(ys))
    rel_maximum_counter = 0
    outer = subprogress_bar(xs, desc=f'Changes$ rel counter=0/{abs_maximum}')
    for i, xi in enumerate(outer): 
      counter = 0
      inner = subprogress_bar(ys, desc=f'Changes$ loc counter=0')
      for j, yi in enumerate(inner):
        if not xi.intersect(yi).is_bottom():
          counter += 1
          inner.set_description(f'Changes$ counter={counter}')
        if len(inner) - j + counter < rel_maximum_counter:
          break
      rel_maximum_counter = max(rel_maximum_counter, counter)
      if rel_maximum_counter >= abs_maximum:
        return rel_maximum_counter
      outer.set_description(f'Changes$ rel counter={rel_maximum_counter}/{abs_maximum}')
    return rel_maximum_counter
  else:
    xs = projected[0].polyhedra
    ys = projected[1].polyhedra
    abs_maximum = len(xs)*len(ys)
    rel_maximum_counter = 0
    outer = subprogress_bar(xs, desc=f'counter=0/{abs_maximum}')
    counter = 0
    for xi in outer: 
      inner = subprogress_bar(ys, desc=f'counter={counter}')
      for yi in inner:
        if not xi.intersect(yi).is_bottom():
          counter += 1
          inner.set_description(f'counter={counter}')
        if counter >= abs_maximum:
          return counter
      rel_maximum_counter = max(rel_maximum_counter, counter)
      outer.set_description(f'counter={rel_maximum_counter}/{abs_maximum}')
    return rel_maximum_counter

  # return 
  # intersections = []
  # pbar = progress_bar(total=len(projected))
  # for i, x in enumerate(projected):
  #   for j, y in enumerate(projected):
  #     pbar.update()
  #     if i == j:
  #       continue
  #     intersections.append(x.intersect(y)) # only feasible intersections
  # return max([len(intersection.polyhedra) for intersection in intersections], default=0)

class ChangesAnalysis(Analysis):
  def __init__(self, pres: list[AbstractDomain], buckets:Buckets):
    assert(all([isinstance(x, DisjunctivePoly) for x in pres]))
    self.pres = pres
    self.buckets = buckets

  def run(self, target_variable) -> int:
    intersection_count = all_intersections(self.pres, target_variable, old=get_older_algorithm())
    return intersection_count
