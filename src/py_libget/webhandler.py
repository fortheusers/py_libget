"""Object to handle libget icon, screenshot, and package zip downloads."""
import json
import os
import shutil
import sys
import urllib.request

opener = urllib.request.build_opener()
opener.addheaders = [("User-agent", "Mozilla/5.0")]
urllib.request.install_opener(opener)

DOWNLOADSFOLDER = "downloads"
CACHEFOLDER = os.path.abspath("./cache")
ETAGFILE = os.path.abspath("./cache/json/etags.json")
os.makedirs("./cache/json", exist_ok=True)


def _get_etagged_file(url: str, file: str) -> str:
    """Supply the url of a json file from an api that supports etagging and path to \
    download to. If the url has been accessed in the past an attempt will be made to \
    check if the cached file is up to date. Useful for avoiding api overuse and \
    for minimizing server bandwidth consumption. `Returns the path of the downloaded \
    file as a String`"""
    req = urllib.request.Request(url)
    etag = _get_etag(file)

    if etag:
        req.add_header("If-None-Match", "{}".format(etag))
    try:
        # Download file
        with urllib.request.urlopen(req) as response, open(file, "wb+") as out_file:
            shutil.copyfileobj(response, out_file)
            # Get new etag from headers and save
            newetag = response.info().get("ETag")
            _set_etag(file, newetag)
        print(f"File {file} - Updated")
    except urllib.error.URLError as e:
        if e.reason == "Not Modified":
            # 304 error, what we want to see if nothing has been updated
            print(f"File {file} - {e.reason}")
        else:
            print(f"Download error - {file} - {e.reason}")
            raise e
    return os.path.abspath(file)


def _init_etags() -> None:
    """
    Initializes an etag json file in the cache folder.
    This is called by _set_etag and _get_etag when needed.

    `Returns None`
    """
    if not os.path.isfile(ETAGFILE):
        print("No ETag file, initializing")
        with open(ETAGFILE, "w+", encoding="utf-8") as f:
            json.dump({}, f, indent=4)


def _set_etag(path: str, etag: str) -> None:
    """
    Saves an etag for a given file path
    path is the file path associated with the etag
    etag is a value obtained from the header of a downloaded file.

    `Returns None`
    """
    # read etags, update, and write
    _init_etags()
    with open(ETAGFILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.update({path: etag})
    with open(ETAGFILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def _get_etag(path: str) -> str:
    """
    Path is a previously downloaded etagged file.

    `Returns last etag as a String or None if not found`
    """
    _init_etags()
    with open(ETAGFILE, "r", encoding="utf-8") as f:
        return json.load(f).get(path)


def _get_json(name: str, url: str) -> str:
    """
    Download a json file from a given api endpoint if needed.
    Uses etagging prevent unnecesarry redownloads.

    `Returns the file path as a String`
    """
    try:
        return _get_etagged_file(url, os.path.join("cache/json", name + ".json"))
    except Exception as e:
        print(f"Failed to get etagged json for {name} from {url}")
        raise e


def _get_cached_json(name: str) -> str:
    """
    Get a previously downloaded json file from the cache.

    `Returns the file path as a String`
    """
    return os.path.join("cache/json", name + ".json")


class webhandler:
    """Object to handle libget icon, screenshot, and package zip downloads."""

    def __init__(self, domain: str):
        self.domain = domain
        self.icons, self.screenshots = {}, {}

    def download(self, url: str, file: str) -> str:
        """
        Downloads a file at a given url to a given location.

        `Returns the file name as a String`
        """
        try:
            urllib.request.urlretrieve(url, file)
            return os.path.abspath(file)
        except Exception as e:
            print(f"Failed to download file at {url} to {file} - {e}")
            raise e

    def get_json(self, name: str, url: str) -> str:
        """
        Get a json file using etagging to limit unneeded bandwidth use.

        `Returns the file name as a String`
        """
        return _get_json(name, url)

    def get_cached_json(self, name: str) -> str:
        """
        Get a cached json file with a given name.

        `Returns the file name as a String`
        """
        return _get_cached_json(name)

    def _get_image(self, name: str, image_type: str, force: bool = False) -> str:
        """
        Downloads or gets cached image for a given package and image type.
        The force keyword argument forces a redownload of the file.

        `Returns the path to the downloaded file as a String`
        """
        path = os.path.join(
            os.path.join(sys.path[0], CACHEFOLDER), name.replace(":", "_")
        )
        os.makedirs(path, exist_ok=True)
        if os.path.isfile((image_path := os.path.join(path, image_type))) and not force:
            return image_path
        else:
            try:
                return self.download(
                    self.domain + f"packages/{name}/{image_type}", image_path
                )
            except Exception as e:
                print(f"Failed to download {image_type} for {name} - {e}")
                return None

    def get_icon(self, name: str, force: bool = False) -> str:
        """
        Downloads icon for a given package if needed.
        The force keyword argument forces a redownload of the file.

        `Returns the icon file's path as a String`
        """
        if not name in self.icons:
            self.icons[name] = self._get_image(name, "icon.png", force=force)
        return self.icons[name]

    def get_screenshot(self, name: str, force: bool = False) -> str:
        """
        Downloads screenshot for a given package if needed.
        The force keyword argument forces a redownload of the file.

        `Returns the screenshot file's path as a String`
        """
        if not name in self.screenshots:
            self.screenshots[name] = self._get_image(name, "screen.png", force=force)
        return self.screenshots[name]

    def get_package(self, name: str) -> str:
        """
        Downloads the current zip for a given package.

        `Returns the downloaded file's path as a String`
        """
        try:
            downloads = os.path.join(sys.path[0], DOWNLOADSFOLDER)
            os.makedirs(downloads, exist_ok=True)
            packagefile = os.path.join(downloads, f"{name}.zip")
            return self.download(self.domain + f"zips/{name}.zip", packagefile)
        except Exception as e:
            print(f"Error getting package zip for {name} - {e}")
