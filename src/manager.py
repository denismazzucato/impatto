from logging import debug, info

from src.abstract_domains.abstract_domain import AbstractDomain
from src.buckets import Buckets
from src.engines.base import Engine
from src.impacts.base import Analysis
from src.input_bounds import InputBounds
from src.utils.string import add_prefix_each_line, from_variable_to_harmonic


def run_engine_each_bucket(
    engine: Engine,
    buckets: Buckets) -> list[AbstractDomain]:
  acc = []
  info("Computing backward analsysis...")
  for bucket in buckets:
    debug(f'Running engine for bucket ({bucket})')
    observations = engine.run(bucket)
    debug(f"Input preconditions for bucket ({bucket}):\n{add_prefix_each_line(str(observations))}")
    acc.append(observations)
  return acc

def run_analysis_each_variable(
    analysis: Analysis,
    variables: list[str]) -> list[AbstractDomain]:
  acc = []
  info("Analysis results:")
  for variable in variables:
    print(f'Running "{analysis.__class__.__name__}" for variable "{variable}":')
    result = analysis.run(from_variable_to_harmonic(variable))
    print(add_prefix_each_line(str(result).replace("frozenset", "")))
    acc.append(analysis)
  return acc
