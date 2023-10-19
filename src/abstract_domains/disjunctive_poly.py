

from src.abstract_domains.abstract_domain import AbstractDomain
from src.abstract_domains.poly import Poly, Status
from src.utils.progress_bar import progress_bar, subprogress_bar


class DisjunctivePoly(AbstractDomain):
  def __init__(self, polyhedra: list[Poly]):
    self.polyhedra = polyhedra
    self.status = Status.UNKNOWN

  @staticmethod
  def top() -> 'DisjunctivePoly':
    this = DisjunctivePoly([])
    this.status = Status.TOP
    return this
    
  @staticmethod
  def bottom() -> 'DisjunctivePoly':
    this = DisjunctivePoly([])
    this.status = Status.BOTTOM
    return this

  def intersect(self, other: 'DisjunctivePoly') -> 'DisjunctivePoly':
    if self.is_bottom() or other.is_bottom():
      return DisjunctivePoly.bottom()
    if self.is_top():
      return other
    if other.is_top():
      return self
    polys = []
    for p1 in subprogress_bar(self.polyhedra):
      for p2 in subprogress_bar(other.polyhedra):
        intersection = p1.intersect(p2)
        if not intersection.is_bottom():
          polys.append(p1.intersect(p2))
    return DisjunctivePoly(polys)
  
  def remove_bottoms(self) -> 'DisjunctivePoly':
    return DisjunctivePoly([p for p in self.polyhedra if not p.is_bottom()])
  
  def eliminate(self, variable: str) -> 'DisjunctivePoly':
    if self.is_bottom() or self.is_top():
      return self
    polyhedra = [p.eliminate(variable) for p in self.polyhedra]
    return DisjunctivePoly(polyhedra)
  
  def is_top(self) -> bool:
    if self.status == Status.TOP:
      return True
    if self.status == Status.BOTTOM:
      return False
    if any([p.is_top() for p in self.polyhedra]):
      return True
    return False
  
  def is_bottom(self) -> bool:
    if self.status == Status.BOTTOM:
      return True
    if self.status == Status.TOP:
      return False
    if any([not p.is_bottom() for p in self.polyhedra]):
      return False
    return True
  
  def __str__(self) -> str:
    if self.is_bottom():
      return "bottom"
    if self.is_top():
      return "top"
    return f"DisjunctivePoly({len(self.polyhedra)} polyhedra)"
    return "\n\n=== or ===\n\n".join([str(p) for p in self.polyhedra])
  