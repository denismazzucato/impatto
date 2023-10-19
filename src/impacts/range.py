from src.abstract_domains.abstract_domain import AbstractDomain
from src.buckets import Buckets
from src.impacts.intersections import IntersectionsAnalysis


class AllRangeAnalysis(IntersectionsAnalysis):
  def __init__(self, pres: list[AbstractDomain], buckets:Buckets):
    super().__init__(pres, buckets)

  def run(self, variable) -> dict[int, set[tuple[int, int]]]:
    intersections = super().run(variable)
    ranges = {}
    for k, vs in intersections.items():
      ranges[k] = set()
      for v in vs:
        lk, uk = self.buckets[k].range()
        for bid in v:
          lbid, ubid = self.buckets[bid].range()
          lk = min(lk, lbid)
          uk = max(uk, ubid)
        ranges[k].add((lk, uk))
    return ranges
  
class RangeAnalysis(AllRangeAnalysis):
  def __init__(self, pres: list[AbstractDomain], buckets:Buckets):
    super().__init__(pres, buckets)

  def run(self, variable) -> int:
    ranges = super().run(variable)
    return max([ub - lb for vs in ranges.values() for lb, ub in vs], default=0)

