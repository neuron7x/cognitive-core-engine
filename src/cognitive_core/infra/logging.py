import logging
import sys

LEVEL = logging.INFO
FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(FORMAT))

root = logging.getLogger()
root.setLevel(LEVEL)
root.handlers.clear()
root.addHandler(handler)
