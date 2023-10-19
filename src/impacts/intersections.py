from src.abstract_domains.abstract_domain import AbstractDomain
from src.abstract_domains.poly import intersecting_components, intersecting_cliques
from src.buckets import Buckets
from src.impacts.base import Analysis


def intersecting_analysis(target: int, impacts, buckets) -> dict[int, set[frozenset[int]]]:
  impacts_without_target = []
  for impact in impacts:
    impact_without_target = impact.eliminate(target)
    # print(impact_without_target)
    impacts_without_target.append(impact_without_target)

  intersecting_impacts_without_target = intersecting_cliques(impacts_without_target)

  return intersecting_impacts_without_target

class IntersectionsAnalysis(Analysis):
  def __init__(self, pres: list[AbstractDomain], buckets:Buckets):
    self.impacts = pres
    self.buckets = buckets

  def run(self, target_variable: int) -> dict[int, set[frozenset[int]]]:
    return intersecting_analysis(target_variable, self.impacts, self.buckets)
  
class CountIntersectionsAnalysis(IntersectionsAnalysis):
  def __init__(self, pres: list[AbstractDomain], buckets:Buckets):
    super().__init__(pres, buckets)

  def run(self, target_variable: int) -> dict[int, int]:
    return {k:max([len(v) for v in vs]) for k, vs in super().run(target_variable).items()}
