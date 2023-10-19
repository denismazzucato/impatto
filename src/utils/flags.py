

from argparse import ArgumentParser

from src.utils.progress_bar import set_show_progress_bar


OLDER_ALGORITHM = True


def add_additional_flags(parser: ArgumentParser) -> None:
  parser.add_argument('--progress-bar', action='store_true',
                      help='show progress bar')
  # parser.add_argument('--changes-fast', action='store_true'
  #                     , help='use the new fast changes algorithm')
  
def handle_additional_flags(args) -> None:
  global OLDER_ALGORITHM
  
  set_show_progress_bar(args.progress_bar)
  # OLDER_ALGORITHM = not args.changes_fast

def get_older_algorithm() -> bool:
  return OLDER_ALGORITHM
