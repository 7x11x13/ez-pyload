import argparse
import logging
from ez_pyload.download import download

def main():
    parser = argparse.ArgumentParser(
        prog="ez-pyload",
        description="Download a file/folder from a filehosting website",
    )
    parser.add_argument("url", help="URL of file/folder to download")
    parser.add_argument("dir",
                        help="Directory to download file to. Defaults to current directory",
                        default=".", nargs="?")
    args = parser.parse_args()
    path = download(args.url, args.dir)
    print("Downloaded", str(path))

if __name__ == "__main__":
    main()