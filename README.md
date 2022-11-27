# py_libget 0.0.3<a name="mark0"></a>

- [About](#mark1)
- [Dependencies](#mark2)
- [Installation](#mark3)
- [Usage](#mark4)
- [Objects](#mark5)
	- [repository](#mark6)
	- [package_manager](#mark7)
	- [parser](#mark8)
	- [webhandler](#mark9)
- [Changelog](#mark10)
	- [0.0.3](#mark11)
	- [0.0.2](#mark12)
	- [0.0.1](#mark13)
	- [0.0.0](#mark14)

---

# About<a name="mark1"></a>[^](#mark0)

Module for handling libget packages.

# Dependencies<a name="mark2"></a>[^](#mark0)

None

# Installation<a name="mark3"></a>[^](#mark0)

Available on pip - `pip install py_libget`

# Usage<a name="mark4"></a>[^](#mark0)

```python
from py_libget import repository

repo_name = "Switch"
repo_url = "https://switchbru.com/appstore/"
package_name = "appstore"

# Create repo object, by default repo loading is deferred
repo = repository(repo_name, repo_url, defer_load=False)

# Get package icon
package_icon_path = repo.get_icon(package_name)
print(package_icon_path)

# Get package screenshot
package_screenshot_path = repo.get_screenshot(package_name)
print(package_screenshot_path)

# Get the package dict from the lookup
package = repo.package_lookup.get(package_name)
if not package:
    raise LookupError(f'Failed to find {package_name} in package')

# Make dir to test with and set repo to install packages there
repo.set_install_path(YOUR TARGET INSTALL DIR)

# Initialize get folder
if not repo.check_if_get_init():
    repo.init_get()

# Install package
repo.install_package(package)
# repo.uninstall_package(package)
```
## Objects<a name="mark5"></a>[^](#mark0)

### repository<a name="mark6"></a>[^](#mark5)
**An object for interacting with all parts of a libget repository.**

```py
class repository(package_manager, parser, webhandler):
	def __init__(self, name: str, domain: str, defer_load: bool = True, force_cached: bool = False):
		...
	def check_if_get_init(self) -> bool:
		"""Check if the libget packages folder has been inited at target location. `Returns True if libget dir exists.`"""
	def clean_version(self, ver: str, name: str) -> str:
		"""Clean a version. `Returns a String`"""
	def clear(self) -> dict:
		"""Alias for parser.init(). `Returns a Dict mapping package names as Strings to package entries as Dicts`"""
	def download(self, url: str, file: str) -> str:
		"""Downloads a file at a given url to a given location. `Returns the file name as a String`"""
	def edit_info(self, name: str, key: str, value) -> None:
		"""Edit a value in an installed package's info values. `Returns None`"""
	def get_cached_json(self, name: str) -> str:
		"""Get a cached json file with a given name. `Returns the file name as a String`"""
	def get_icon(self, name: str, force: bool = False) -> str:
		"""Downloads icon for a given package if needed. The force keyword argument forces a redownload of the file. `Returns the icon file's path as a String`"""
	def get_json(self, name: str, url: str) -> str:
		"""Get a json file using etagging to limit unneeded bandwidth use. `Returns the file name as a String`"""
	def get_package(self, name: str) -> str:
		"""Downloads the current zip for a given package. `Returns the downloaded file's path as a String`"""
	def get_package_dict(self, name: str) -> dict:
		"""Get entry for a given package name. `Returns a Dict, empty on failure.`"""
	def get_package_entry(self, name: str) -> dict:
		"""Get the contents of an installed package's info.json file. `Returns a Dict, empty on failure.`"""
	def get_package_manifest(self, name: str) -> list:
		"""Returns a package's manifest. `Returns a List of the real file paths as Strings`"""
	def get_package_value(self, name: str, key: str) -> str | None:
		"""Get a value from an installed package's info.json file. `Returns the value (usually a String) or None on failure."""
	def get_package_version(self, name: str) -> str:
		"""Get the currently installed version of a package. `Returns a String`"""
	def get_packages(self) -> list:
		"""Get a list of currently installed packages. `Returns a List`"""
	def get_screenshot(self, name: str, force: bool = False) -> str:
		"""Downloads screenshot for a given package if needed. The force keyword argument forces a redownload of the file. `Returns the screenshot file's path as a String`"""
	def init(self) -> None:
		"""Reinitialize parser. `Returns a Dict mapping package names as Strings to package entries as Dicts`"""
	def init_get(self) -> None:
		"""Initializes the libget dir at the current install path. `Returns None.`"""
	def install_package(self, package: dict, handler: Callable = None) -> None:
		"""Installs a libget package, supply a callable handler to take a tuple containing a status and a message. A negative status is an error. Status is in the form of an integer from 0 to 100 during normal install progression. `Returns None`"""
	def load_cached_repo(self) -> list:
		"""Loads / reloads repo from cached file. `Returns the loaded repo as a List.`"""
	def load_repo(self) -> str:
		"""Loads / reloads repo from file. `Returns the loaded repo as a List.`"""
	def load_repo_file(self, repo_file: str) -> list:
		"""Loads appstore json. `Returns a List of Dicts`"""
	def reload(self) -> list:
		"""Reloads the list of installed packages. `Returns a List of packages installed.`"""
	def remove_store_entry(self, name: str) -> None:
		"""THIS DOES NOT REMOVE THE PACKAGE FILES Removes a package entry by deleting the package folder containing the manifest and info.json `Returns None`"""
	def set_install_path(self, path: str) -> list:
		"""Set this to a root of an sd card. `Returns a List of packages installed at the given path.`"""
	def uninstall_package(self, package: dict, handler: Callable = None) -> None:
		"""Uninstalls a libget package, supply a callable handler to take a tuple containing a status and a message. A negative status is an error. Status is in the form of an integer from 0 to 100 during normal install progression. `Returns None`"""
```
### package_manager<a name="mark7"></a>[^](#mark5)
**Object for managing libget package installation**

```py
class package_manager(object):
	def __init__(self, webhandler, libget_dir: str = '.libget'):
		...
	def check_if_get_init(self) -> bool:
		"""Check if the libget packages folder has been inited at target location. `Returns True if libget dir exists.`"""
	def edit_info(self, name: str, key: str, value) -> None:
		"""Edit a value in an installed package's info values. `Returns None`"""
	def get_package_entry(self, name: str) -> dict:
		"""Get the contents of an installed package's info.json file. `Returns a Dict, empty on failure.`"""
	def get_package_manifest(self, name: str) -> list:
		"""Returns a package's manifest. `Returns a List of the real file paths as Strings`"""
	def get_package_value(self, name: str, key: str) -> str | None:
		"""Get a value from an installed package's info.json file. `Returns the value (usually a String) or None on failure."""
	def get_package_version(self, name: str) -> str:
		"""Get the currently installed version of a package. `Returns a String`"""
	def get_packages(self) -> list:
		"""Get a list of currently installed packages. `Returns a List`"""
	def init_get(self) -> None:
		"""Initializes the libget dir at the current install path. `Returns None.`"""
	def install_package(self, package: dict, handler: Callable = None) -> None:
		"""Installs a libget package, supply a callable handler to take a tuple containing a status and a message. A negative status is an error. Status is in the form of an integer from 0 to 100 during normal install progression. `Returns None`"""
	def reload(self) -> list:
		"""Reloads the list of installed packages. `Returns a List of packages installed.`"""
	def remove_store_entry(self, name: str) -> None:
		"""THIS DOES NOT REMOVE THE PACKAGE FILES Removes a package entry by deleting the package folder containing the manifest and info.json `Returns None`"""
	def set_install_path(self, path: str) -> list:
		"""Set this to a root of an sd card. `Returns a List of packages installed at the given path.`"""
	def uninstall_package(self, package: dict, handler: Callable = None) -> None:
		"""Uninstalls a libget package, supply a callable handler to take a tuple containing a status and a message. A negative status is an error. Status is in the form of an integer from 0 to 100 during normal install progression. `Returns None`"""
```
### parser<a name="mark8"></a>[^](#mark5)
**Object to hold and parse libget repos**

```py
class parser(object):
	def __init__(self, ):
		...
	def clean_version(self, ver: str, name: str) -> str:
		"""Clean a version. `Returns a String`"""
	def clear(self) -> dict:
		"""Alias for parser.init(). `Returns a Dict mapping package names as Strings to package entries as Dicts`"""
	def get_package_dict(self, name: str) -> dict:
		"""Get entry for a given package name. `Returns a Dict, empty on failure.`"""
	def init(self) -> None:
		"""Reinitialize parser. `Returns a Dict mapping package names as Strings to package entries as Dicts`"""
	def load_repo_file(self, repo_file: str) -> list:
		"""Loads appstore json. `Returns a List of Dicts`"""
```
### webhandler<a name="mark9"></a>[^](#mark5)
**Object to handle libget icon, screenshot, and package zip downloads.**

```py
class webhandler(object):
	def __init__(self, domain: str):
		...
	def download(self, url: str, file: str) -> str:
		"""Downloads a file at a given url to a given location. `Returns the file name as a String`"""
	def get_cached_json(self, name: str) -> str:
		"""Get a cached json file with a given name. `Returns the file name as a String`"""
	def get_icon(self, name: str, force: bool = False) -> str:
		"""Downloads icon for a given package if needed. The force keyword argument forces a redownload of the file. `Returns the icon file's path as a String`"""
	def get_json(self, name: str, url: str) -> str:
		"""Get a json file using etagging to limit unneeded bandwidth use. `Returns the file name as a String`"""
	def get_package(self, name: str) -> str:
		"""Downloads the current zip for a given package. `Returns the downloaded file's path as a String`"""
	def get_screenshot(self, name: str, force: bool = False) -> str:
		"""Downloads screenshot for a given package if needed. The force keyword argument forces a redownload of the file. `Returns the screenshot file's path as a String`"""
```
# Changelog<a name="mark10"></a>[^](#mark0)

## 0.0.3<a name="mark11"></a>[^](#mark10)

Improve readme / add credits

## 0.0.2<a name="mark12"></a>[^](#mark10)

Fix readme.

## 0.0.1<a name="mark13"></a>[^](#mark10)

Cleanup, fix readme.

## 0.0.0<a name="mark14"></a>[^](#mark10)

Create Project



Generated with [py_simple_readme](https://github.com/AndrewSpangler/py_simple_readme)