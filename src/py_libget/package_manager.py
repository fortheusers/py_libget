"""Object for managing libget package installation"""
import json
import os
import shutil
import sys
from typing import Callable
from zipfile import ZipFile

# Name of package info file
PACKAGE_INFO = "info.json"
# Name of pagkade manifest file
PACKAGE_MANIFEST = "manifest.install"
# The prefix used to designate each line in the manifest
MANIFEST_PREFIX = "U: "


class package_manager:
    """Object for managing libget package installation"""

    status_map = {
        -1: ValueError,
        -2: TypeError,
        -3: FileNotFoundError,
        -4: Exception,
    }
    inverse_status_map = {v: k for k, v in status_map.items()}

    def __init__(self, webhandler, libget_dir: str = ".libget"):
        self.base_install_path = None
        self.packages = None
        self.libget_dir = libget_dir
        self.webhandler = webhandler

    def set_install_path(self, path: str) -> list:
        """
        Set this to a root of an sd card.

        `Returns a List of packages installed at the given path.`
        """
        self.base_install_path = path
        self.packages = None
        return self.get_packages() if path else []

    def reload(self) -> list:
        """
        Reloads the list of installed packages.

        `Returns a List of packages installed.`
        """
        return self.set_install_path(self.base_install_path)

    def check_if_get_init(self) -> bool:
        """
        Check if the libget packages folder has been inited at target location.

        `Returns True if libget dir exists.`
        """
        if self.base_install_path:
            try:
                return os.path.isdir(
                    os.path.join(self.base_install_path, self.libget_dir)
                )
            except:
                pass
        return False

    def init_get(self) -> None:
        """
        Initializes the libget dir at the current install path.

        `Returns None.`
        """
        if not self.base_install_path:
            raise ValueError("Install path not set or invalid")
        if self.check_if_get_init():
            raise FileExistsError("Libget dir already inited")
        os.makedirs(os.path.join(self.base_install_path, self.libget_dir))

    def _handle(self, status: int, message: str, handler=None) -> None:
        """
        Handles installing / uninstalling progress.
        Raises appropriate error on negative status.

        `Returns None`
        """
        if handler:
            handler((status, message))
        if status < 0:  # Error
            raise self.status_map[status](message)
        else:
            print("{:<4} | {}".format(str(status) + "%", message))

    def install_package(self, package: dict, handler: Callable = None) -> None:
        """
        Installs a libget package, supply a callable handler to take a tuple
        containing a status and a message. A negative status is an error. Status is
        in the form of an integer from 0 to 100 during normal install progression.

        `Returns None`
        """

        try:
            if not isinstance(package, dict):
                self._handle(-2, "Invalid package specifier provided.", handler)
            if not package:
                self._handle(
                    -1, "No repo entry data passed to libget handler.", handler
                )
            if not self.base_install_path:
                self._handle(-1, "Install path not set or invalid.", handler)
            if not (name := package.get("name")):
                self._handle(-1, "Name not found in package data.", handler)
            if not (version := package.get("version")):
                self._handle(-1, "Version not found in package data.", handler)
            if not self.check_if_get_init():
                self._handle(-3, "Get folder not initiated.", handler)
            # Uninstall if already installed
            if name in self.get_packages():
                self._handle(
                    10, "Package already installed, removing for upgrade.", handler
                )
                if not self.uninstall_package(package):
                    self._handle(
                        -1, "Uninstall failed. Not continuing with install.", handler
                    )
            else:
                self._handle(
                    20, "Package not previously installed, proceeding...", handler
                )
            self._handle(30, f"Beginning install for package {name}", handler)
            packagesdir = os.path.join(self.base_install_path, self.libget_dir)
            # Append package folder to packages directory
            os.makedirs((packagedir := os.path.join(packagesdir, name)), exist_ok=True)
            if not (package_zip := self.webhandler.get_package(name)):
                self._handle(-3, f"Failed to download zip for package {name}", handler)
            self._handle(40, "Downloaded package zip", handler)
            with ZipFile(package_zip) as z:
                namelist = z.namelist()
                if not PACKAGE_MANIFEST in namelist:
                    self._handle(
                        -3, f"Failed to find {PACKAGE_MANIFEST} in zip", handler
                    )
                self._handle(50, "Found package manifest", handler)
                if not PACKAGE_INFO in namelist:
                    self._handle(-3, f"Failed to find {PACKAGE_INFO} in zip")
                self._handle(60, "Found package info", handler)
                # Extract everything but the manifest and the info file
                extract_manifest = []
                for filename in z.namelist():
                    if not filename in [PACKAGE_MANIFEST, PACKAGE_INFO]:
                        z.extract(filename, path=self.base_install_path)
                        extract_manifest.append(filename)
                self._handle(
                    70,
                    "Extracted: {}".format(json.dumps(extract_manifest, indent=4)),
                    handler,
                )
                z.extract(PACKAGE_MANIFEST, path=packagedir)
                self._handle(80, "Wrote package manifest.", handler)
                z.extract(PACKAGE_INFO, path=packagedir)
                self._handle(90, "Wrote package info.", handler)
            os.remove(package_zip)
            self._handle(95, "Cleaned up.", handler)
            self._handle(
                100, f"Installed {package['title']} version {version}", handler
            )
        except Exception as e:
            ex_code = self.inverse_status_map.get(type(e), -4)
            try:
                # Handle but override exception raise
                # Re-raise exception below instead for
                # more verbose exception details
                self._handle(ex_code, f"Error in install process - {e}", handler)
            except:
                pass
            raise e
        self.reload()

    def uninstall_package(self, package: dict, handler: Callable = None) -> None:
        """
        Uninstalls a libget package, supply a callable handler to take a tuple
        containing a status and a message. A negative status is an error. Status is
        in the form of an integer from 0 to 100 during normal install progression.

        `Returns None`
        """
        if not self.base_install_path:
            self._handle(-1, "Install path not set or invalid", handler)
        if not package:
            self._handle(-1, "No repo entry data passed to libget handler.", handler)
        if not self.check_if_get_init():
            self._handle(-3, "Get folder not initiated.", handler)

        name = package["name"]
        print(f"Uninstalling {name}")
        if not self.get_package_entry(name):
            self._handle(
                -3, "Could not find package in currently selected location.", handler
            )
        manifest = self.get_package_manifest(name)
        # Go through the previous ziplist in reverse, ensuring folders get removed
        # Folders will not be removed if files not contained in the manifest remain
        for path in reversed(manifest):
            file = os.path.join(self.base_install_path, path)
            if os.path.isfile(file):
                os.remove(file)
                print(f"removed {file}")
            elif os.path.isdir(file):
                if not os.listdir(file):
                    os.rmdir(file)
                    print(f"removed empty directory {file}")
        self.remove_store_entry(name)

        print(f"Uninstalled package {name}")

        self.reload()
        return True

    def remove_store_entry(self, name: str) -> None:
        """
        THIS DOES NOT REMOVE THE PACKAGE FILES
        Removes a package entry by deleting the package
        folder containing the manifest and info.json

        `Returns None`
        """
        if not self.base_install_path:
            raise ValueError("Install path not set or invalid")
        packagedir = os.path.join(self.base_install_path, self.libget_dir, name)
        try:
            shutil.rmtree(packagedir, ignore_errors=True)
            print(f"Removed libget entry for {name}")
        except Exception as e:
            print(f"Error removing libget entry for {name} - {e}")

    def get_package_entry(self, name: str) -> dict:
        """
        Get the contents of an installed package's info.json file.

        `Returns a Dict, empty on failure.`
        """
        if not self.base_install_path:
            return {}
        pkg = os.path.join(self.base_install_path, self.libget_dir, name, PACKAGE_INFO)
        try:
            with open(pkg, encoding="utf-8") as infojson:
                return json.load(infojson)
        except FileNotFoundError:
            return {}
        except Exception as e:
            print(f"Error loading package info for {name} - {e}")
            raise e

    def get_package_value(self, name: str, key: str) -> str | None:
        """
        Get a value from an installed package's info.json file.

        `Returns the value (usually a String) or None on failure.
        """
        if not self.base_install_path:
            return
        return self.get_package_entry(name).get(key)

    def get_package_version(self, name: str) -> str:
        """
        Get the currently installed version of a package.

        `Returns a String`
        """
        return self.get_package_value(name, "version")

    def get_package_manifest(self, name: str) -> list:
        """
        Returns a package's manifest.

        `Returns a List of the real file paths as Strings`
        """
        if not self.base_install_path:
            raise ValueError("Install path not set or invalid")
        manifestfile = os.path.join(
            self.base_install_path, self.libget_dir, name, PACKAGE_MANIFEST
        )
        if not os.path.isfile(manifestfile):
            raise FileExistsError("Failed to find manifest file")
        mf = []
        # open the manifest, append the current base path to each line
        with open(manifestfile, "r") as maf:
            for fileline in maf:
                fl = fileline.replace(MANIFEST_PREFIX, "")
                fl = fl.strip().replace("\n", "")
                mf.append(os.path.join(os.path.realpath(self.base_install_path), fl))
        return mf

    def get_packages(self) -> list:
        """
        Get a list of currently installed packages.

        `Returns a List`
        """
        if not self.base_install_path:
            raise ValueError("Install path not set or invalid")
        pack_dir = os.path.join(self.base_install_path, self.libget_dir)
        self.packages = []
        if os.path.isdir(pack_dir):
            for possible_package in os.listdir(pack_dir):
                package_json = os.path.join(pack_dir, possible_package, PACKAGE_INFO)
                if os.path.exists(package_json) and not os.path.isdir(package_json):
                    self.packages.append(possible_package)
        return self.packages

    def edit_info(self, name: str, key: str, value) -> None:
        """
        Edit a value in an installed package's info values.

        `Returns None`
        """
        if not self.base_install_path:
            raise ValueError("Install path not set or invalid")
        pkg = os.path.join(self.base_install_path, self.libget_dir, name, PACKAGE_INFO)
        with open(pkg, encoding="utf-8") as f:
            info = json.load(f)
        info[key] = value
        with open(pkg, "w", encoding="utf-8") as f:
            json.dump(info, f)
