from argparse import ArgumentParser, Namespace
from logging import debug, error, info
from pathlib import Path

from src.utils.colors import RED, ENDC
from src.utils.flags import add_additional_flags, handle_additional_flags
from src.utils.logging import setup_logs, setup_log_levels
from src.impacts.impacts_picker import available_analyses, default_analysis
from src.engines.engines_picker import available_engines, default_engine


TIMEOUT_SECONDS = 60

def cli_helper(raw_args_without_program: list[str] | None) -> Namespace:
  setup_logs()
  parser = ArgumentParser(description='Impatto, A Static Analyzer for Quantitative Input Data Usage')
  parser.add_argument('program', metavar='PROGRAM', type=Path,
                      help='path to the input program PROGRAM')
  parser.add_argument('inputs', metavar='INPUTS.json', type=Path,
                      help='path to the INPUTS.json file for input specifications')
  parser.add_argument('buckets', metavar='BUCKETS.json', type=Path,
                      help='path to the BUCKETS.json file for output buckets')
  parser.add_argument('-d', '--debug', action='store_true',
                      help='set log level to DEBUG')
  parser.add_argument('-a', '--analysis', metavar='IMPACT', type=str, default=default_analysis(),
                      help='impact analysis: ' + ', '.join(available_analyses()))
  parser.add_argument('-e', '--engine', metavar='ENGINE', type=str, default=default_engine(),
                      help='backward engines: ' + ', '.join(available_engines()))
  parser.add_argument('-i', '--interest', metavar='VARIABLE', type=str, help='variable of interest')
  add_additional_flags(parser)

  args = parser.parse_args(raw_args_without_program)
  setup_log_levels(args.debug)
  handle_additional_flags(args)
  # debug(f'CLI arguments: {raw_args_without_program}')

  if not args.program.exists():
    raise Exception(f'Program file {RED}{args.program.name}{ENDC} does not exist')

  if not args.inputs.exists():
    raise Exception(f'Inputs file {RED}{args.inputs.name}{ENDC} does not exist')

  if not args.buckets.exists():
    raise Exception(f'Buckets file {RED}{args.buckets.name}{ENDC} does not exist')

  if args.analysis not in available_analyses():
    raise Exception(f'Analysis {RED}{args.analysis}{ENDC} not supported, please choose one of: {", ".join(available_analyses())}')

  if args.engine not in available_engines():
    raise Exception(f'Engine {RED}{args.engine}{ENDC} not supported, please choose one of: {", ".join(available_engines())}')

  # debug("Debugging mode on")
  return args
