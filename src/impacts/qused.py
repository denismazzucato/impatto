from logging import warning
from src.abstract_domains.abstract_domain import AbstractDomain
from src.abstract_domains.poly import Poly
from src.buckets import Buckets
from src.impacts.base import Analysis


class QusedAnalysis(Analysis):
  def __init__(self, pres: list[AbstractDomain], buckets:Buckets):
    self.pres = pres
    warning("QUsed returns the minumum quantity, hence the highest means unused")

  def run(self, variable) -> int:

    quantities = {}
    for i, pre in enumerate(self.pres):
      reduced_pre = pre.eliminate(variable)
      assert isinstance(reduced_pre, Poly)
      count = reduced_pre.count_integers_between()
      quantities[i] = count
    return min([q for q in quantities.values()])