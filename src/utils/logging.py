import logging
import colorlog
import networkx as nx

# Set the logging level to suppress networkx log messages
logging.getLogger("numexpr").setLevel(logging.CRITICAL)

def setup_logs():
  formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)s:%(reset)s %(message)s',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
    reset=True,
    style='%'
  )
  handler = logging.StreamHandler()
  handler.setFormatter(formatter)
  logging.basicConfig(handlers=[handler])

def setup_log_levels(debug=False):
  logging.getLogger().setLevel(logging.DEBUG if debug else logging.INFO)