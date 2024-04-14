import logging
import os
import sqlite3
import sys

from pyload.core.log_factory import LogFactory
from pyload.core.threads.database_thread import DatabaseThread

logger = logging.getLogger("pyload")
consoleform = logging.Formatter(
    LogFactory.LINEFORMAT, LogFactory.DATEFORMAT, LogFactory.LINESTYLE
)
consolehdlr = logging.StreamHandler(sys.stdout)
consolehdlr.setFormatter(consoleform)
logger.addHandler(consolehdlr)

LogFactory.get_logger = lambda self, name: logger


def new_db_thread_run(self):
    convert = self._check_version()

    self.conn = sqlite3.connect(
        self.db_path,
        isolation_level=None,
        check_same_thread=False,  # <- this is the only change of the patch
    )
    os.chmod(self.db_path, 0o600)

    self.c = self.conn.cursor()

    if convert is not None:
        self._convert_db(convert)

    self._create_tables()

    self.conn.commit()

    self.setuplock.set()

    while True:
        j = self.jobs.get()
        if j == "quit":
            self.c.close()
            self.conn.close()
            break
        j.process_job()


DatabaseThread.run = new_db_thread_run
