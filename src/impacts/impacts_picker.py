from logging import debug
from typing import cast

from src.impacts.base import Analysis
# from src.impacts.base import Analysis, NothingAnalysis
from src.utils.picker import choose, available, to_class_name


# add here all available analyses
# from src.impacts.intersections import IntersectionsAnalysis
from src.impacts.outcomes import OutcomesAnalysis
from src.impacts.range import RangeAnalysis
from src.impacts.unused import UnusedAnalysis
# from src.impacts.qused import *
from src.impacts.changes import ChangesAnalysis

def choose_analysis(analysis: str) -> type[Analysis]:
  analysis_class_name = to_class_name(analysis, 'Analysis')
  AnalysisClass = cast(type[Analysis], choose(analysis_class_name, globals(), Analysis))
  debug(f'Chosen analysis: {analysis_class_name}')
  return AnalysisClass

def available_analyses():
  return available('Analysis', globals())

def default_analysis():
  return 'outcomes'