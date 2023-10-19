from abc import ABC, abstractmethod


class AbstractDomain(ABC):
  @abstractmethod
  def intersect(self, other: 'AbstractDomain') -> 'AbstractDomain':
    pass

  def does_intersect(self, other: 'AbstractDomain') -> bool:
    if self.is_bottom() or other.is_bottom():
      return False
    if self.is_top() or other.is_top():
      return True
    intersected = self.intersect(other)
    return not intersected.is_bottom()

  @abstractmethod
  def eliminate(self, variable: str) -> 'AbstractDomain':
    pass

  @abstractmethod
  def is_top(self) -> bool:
    pass

  @abstractmethod
  def is_bottom(self) -> bool:
    pass

  @abstractmethod
  def top(self) -> 'AbstractDomain':
    pass

  @abstractmethod
  def bottom(self) -> 'AbstractDomain':
    pass
