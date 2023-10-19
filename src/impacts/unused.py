from enum import Enum
from src.abstract_domains.abstract_domain import AbstractDomain
from src.buckets import Buckets
from src.impacts.intersections import IntersectionsAnalysis


class SoundOutput(Enum):
  DEF_UNUSED = 0
  MAYBE_USED = 1

class UnusedAnalysis(IntersectionsAnalysis):
  def __init__(self, pres: list[AbstractDomain], buckets:Buckets):
    super().__init__(pres, buckets)

  def run(self, variable) -> SoundOutput:
    intersections = super().run(variable)
    return SoundOutput.DEF_UNUSED if all([len(v) == 0 for v in intersections.values()]) else SoundOutput.MAYBE_USED

