import logging
import logging.handlers
from datetime import date
logger = None
import os

#Make log folder
if not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')):
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs'))
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
today = date.today()
sysdate = today.strftime("%d-%m-%Y")
log_name = "Logs"+'-'+sysdate+".log"
log_fname = os.path.join(log_dir, log_name)
if not os.path.isfile(log_fname):
    f=open(log_fname, 'w')
    f.close()
logger = logging.getLogger("applog")
formatter = logging.Formatter('%(levelname)s : %(asctime)s : %(message)s')
logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(log_fname, maxBytes=5000000, backupCount=10)
handler.setFormatter(formatter)
logger.addHandler(handler)