

from tqdm import tqdm


SHOW_PROGRESS_BAR: bool = False

def progress_bar(*args, **kwargs):
  if SHOW_PROGRESS_BAR:
    return tqdm(*args, **kwargs)
  else:
    return tqdm(*args, **kwargs, disable=True)
  
def subprogress_bar(*args, **kwargs):
  return progress_bar(leave=False, *args, **kwargs)

def set_show_progress_bar(show: bool) -> None:
  global SHOW_PROGRESS_BAR
  SHOW_PROGRESS_BAR = show