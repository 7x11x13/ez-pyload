# ez-pyload

Wrapper for [pyLoad](https://github.com/pyload/pyload) so it can be used in your Python projects without starting a webserver like pyLoad normally does.

## Why?
I've been trying to find a library or CLI app which is able to download from many different filehosting sites for a long while now. The only free downloaders I have been able to find with support for many filehosting sites are jDownloader2 and pyLoad, neither of which seem to have a CLI interface or developer friendly API/documentation, and both of which seem to run a webserver just to be able to download some files. This library (hopefully) fixes this problem.

## Installation

`$ python3 -m pip install ez-pyload`

## Using as a library

ez-pyload comes with a single function: `download(url: str, download_dir: str | Path, loglevel: int = logging.INFO) -> Path)`
This function will download the file/folder at `url` to the directory `download_dir`. If loglevel is set to `logging.DEBUG`, debug mode will be enabled.

### Example

```py
from ez_pyload import download

path = download("https://drive.google.com/file/d/xxxxxxxxxxxxxxxxxxx-xxxxxxxx/view?usp=drive_link", ".")
print("Downloaded file:", path)
```

## Using as a CLI app
After installing, you may use `pydl [url] [path]` to download a file/folder at url to the given path (defaults to current working directory)
