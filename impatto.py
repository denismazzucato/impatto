from src.buckets import Buckets
from src.input_bounds import read_input_bounds
from src.manager import run_engine_each_bucket, run_analysis_each_variable
from src.program import read_program
from src.utils.cli import cli_helper
from src.engines.engines_picker import choose_engine
from src.impacts.impacts_picker import choose_analysis


def main(raw_args: list[str] | None = None):
  args = cli_helper(raw_args)
  inputs = read_input_bounds(args.inputs)
  buckets = Buckets(args.buckets)
  program = read_program(args.program)
  Engine = choose_engine(args.engine)
  Analysis = choose_analysis(args.analysis)
  if args.interest:
    variables_of_interest = [args.interest]
  else:
    variables_of_interest = program.get_variables()

  # retrieve the input-output observations from the engine
  loaded_engine = Engine(program, inputs)
  preconditions = run_engine_each_bucket(loaded_engine, buckets)

  # run the analysis
  loaded_analysis = Analysis(preconditions, buckets)
  results = run_analysis_each_variable(loaded_analysis, variables_of_interest)

if __name__ == '__main__':
  main()