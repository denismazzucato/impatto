from abc import ABC, abstractmethod
from typing import Any

from src.abstract_domains.abstract_domain import AbstractDomain
from src.buckets import Buckets


class Analysis(ABC):
  @abstractmethod
  def __init__(self, pres: list[AbstractDomain], buckets:Buckets):
    pass

  @abstractmethod
  def run(self, target_variable: str) -> Any:
    pass

class NothingAnalysis(Analysis):
  def __init__(self, pres: list[AbstractDomain], buckets:Buckets):
    pass

  def run(self, target_variable: str) -> Any:
    return None