from src.abstract_domains.abstract_domain import AbstractDomain
from src.buckets import Buckets
from src.impacts.intersections import CountIntersectionsAnalysis


class OutcomesAnalysis(CountIntersectionsAnalysis):
  def __init__(self, pres: list[AbstractDomain], buckets:Buckets):
    super().__init__(pres, buckets)

  def run(self, target_variable: int) -> int:
    return max(super().run(target_variable).values(), default=0)

