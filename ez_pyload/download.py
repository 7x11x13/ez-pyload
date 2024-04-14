import logging
import os
import shutil
from pathlib import Path

cwd = os.getcwd() # pyload messes with cwd

from pyload.core import Core
from pyload.core.datatypes.pyfile import PyFile
from pyload.core.threads.download_thread import DownloadThread

from .patches import logger

os.chdir(cwd)

import tempfile


def _download(pyload: Core, url: str, pkg_name: str = "unknown", pkg_dir: str = "unknown") -> bool:
    urls = [url]
    data = pyload.plugin_manager.parse_urls(urls)
    url, plugin = data[0]
    pkg_id = pyload.files.add_package(pkg_name, pkg_dir)
    pyfile = PyFile(pyload.files, -1, url, url, 0, 0, "", plugin, pkg_id, -1)
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
                _download(
                    pyload, url, name, pkg_dir + os.sep + folder
                )  # pyload uses os.sep instead of / so this is necessary
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
    tmp = "."
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
        # don't care about corrupting data,
        # just need to release connections NOW
        # so we can clean up tempdir
        pyload.db.c.close()
        pyload.db.conn.close()
        return dst_path
