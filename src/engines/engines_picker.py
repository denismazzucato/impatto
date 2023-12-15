from logging import debug
from typing import cast

from src.engines.base import Engine
from src.utils.picker import choose, available, to_class_name


# add here all available engines
from src.engines.interproc import InterprocEngine, InterprocFastEngine, InterprocStrongEngine
from src.engines.libra import LibraEngine, DisjunctiveCompletionEngine

def choose_engine(engine: str) -> type[Engine]:
  engine_class_name = to_class_name(engine, 'Engine')
  EngineClass = cast(type[Engine], choose(engine_class_name, globals(), Engine))
  debug(f'Chosen engine: {engine_class_name}')
  return EngineClass

def available_engines():
  return available('Engine', globals())

def default_engine():
  return 'interproc'