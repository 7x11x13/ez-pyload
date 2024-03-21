import glob
import logging
import os
from pathlib import Path
import shutil
import sys

cwd = os.getcwd() # pyload messes with cwd
from pyload.core import Core
from pyload.core.log_factory import LogFactory
from pyload.core.datatypes.enums import Destination
from pyload.core.datatypes.pyfile import PyFile
from pyload.core.datatypes.pypackage import PyPackage
from pyload.core.threads.download_thread import DownloadThread
os.chdir(cwd)

logger = logging.getLogger("pyload")
consoleform = logging.Formatter(
    LogFactory.LINEFORMAT, LogFactory.DATEFORMAT, LogFactory.LINESTYLE
)
consolehdlr = logging.StreamHandler(sys.stdout)
consolehdlr.setFormatter(consoleform)
logger.addHandler(consolehdlr)
def new_get_logger(self, name: str):
    return logger
LogFactory.get_logger = new_get_logger

import tempfile

def _download(pyload: Core, url: str, pkg_name: str = "unknown", pkg_dir: str = "unknown") -> bool:
    urls = [url]
    data = pyload.plugin_manager.parse_urls(urls)
    url, plugin = data[0]
    PyPackage(pyload.file_manager, 0, pkg_name, pkg_dir, None, None, Destination.QUEUE, None)
    pyfile = PyFile(pyload.files, -1, url, url, 0, 0, "", plugin, 0, -1)
    pyfile.init_plugin()
    if pyfile.plugin.__type__ == "downloader":
        thread = DownloadThread(pyload.thread_manager)
        pyload.addon_manager.download_preparing(pyfile)
        pyfile.plugin.preprocessing(thread)
        pyfile.release()
        return False
    else:
        try:
            pyfile.plugin.config.set("dl_subfolders", True)
            pyfile.plugin.config.set("package_subfolder", True)
        except Exception:
            pass
        pyfile.plugin._initialize()
        pyfile.plugin._setup()
        pyload.addon_manager.download_preparing(pyfile)
        pyfile.plugin.process(pyfile)
        for folder, urls, name in pyfile.plugin.packages:
            for url in urls:
                _download(pyload, url, name, pkg_dir + "/" + folder)
        return True

def download(url: str, download_dir: str | Path, loglevel: int = logging.INFO) -> Path:
    """Download the file or folder at the given URL

    Args:
        url (str): URL to file or folder hosted on a supported site
        download_dir (str | Path): Directory to download file/folder to
        loglevel (int, optional): Log level of pyLoad (set to logging.DEBUG to enable
            debug mode). Defaults to logging.INFO.

    Returns:
        Path: Path to downloaded file/folder
    """
    download_dir = Path(download_dir)
    debug = loglevel == logging.DEBUG
    logger.setLevel(loglevel)
    with tempfile.TemporaryDirectory(".ez-pyload") as tmp:
        pyload = Core(tmp, "tmpdir", "storage", debug)
        is_dir = _download(pyload, url)
        src_path = next((Path(tmp) / "data" / "storage" / "unknown").glob("*"))
        name = src_path.name
        dst_path = download_dir / name
        # pyload messes with cwd again
        os.chdir(cwd)
        if is_dir:
            shutil.copytree(src_path, dst_path)
        else:
            shutil.copy(src_path, dst_path)
        pyload.terminate()
        return dst_path