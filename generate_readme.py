#!/usr/bin/env python
import os, sys, json, tomllib

basic_usage = """from py_libget import repository

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
repo.set_install_path(YOUR TARGET INSTALL DIR, MUST ALREADY EXIST)

# Initialize get folder
if not repo.check_if_get_init():
    repo.init_get()

# Install package
repo.install_package(package)
# repo.uninstall_package(package)"""


cli_usage = """usage: python -m py_libget [-h] [-b BUNDLE] [-i INSTALL [INSTALL ...]]
                   [-u UNINSTALL [UNINSTALL ...]]
                   [-sc SCREENSHOT [SCREENSHOT ...]] [-ic ICON [ICON ...]]
                   repository [install_path]

py_libget CLI - Interact with libget repositories and manage package
installs. Runs Bundle -> Install -> Uninstall processes if multiple are
specified.

positional arguments:
  repository            URL of the libget repository.
  install_path          Path to SD Card root or target dir. Defaults to
                        current working dir if not specified.

options:
  -h, --help            show this help message and exit
  -b BUNDLE, --bundle BUNDLE
                        Path to bundle file. Bundles files are plaintext
                        with one package name per line, comments are
                        allowed by starting a line with a #. Will install
                        / update all packages in the bundle
  -i INSTALL [INSTALL ...], --install INSTALL [INSTALL ...]
                        List of package names to install / update,
                        separated by spaces.
  -u UNINSTALL [UNINSTALL ...], --uninstall UNINSTALL [UNINSTALL ...]
                        List of package names to uninstall, separated by
                        spaces.
  -sc SCREENSHOT [SCREENSHOT ...], --screenshot SCREENSHOT [SCREENSHOT ...]
                        Provide one or more package names separated by
                        spaces (minimum 1), screenshots will be downloaded
                        to cache. A map of the downloaded files will be
                        printed on download completion.
  -ic ICON [ICON ...], --icon ICON [ICON ...]
                        Provide one or more package names separated by
                        spaces (minimum 1), icons will be downloaded to
                        cache. A map of the downloaded files will be
                        printed on download completion.
"""

cli_example = """
For example:

To install the "appstore" and "vgedit" package from the 4TU Switch repository to an SD card located at D:/:

`python -m py_libget https://www.switchbru.com/appstore/ -i appstore vgedit D:/`
"""


thanks = "Special thanks to vgmoose and the 4TU team for the libget standard. https://gitlab.com/4TU/libget"


about = """This module was created to simplify testing and development with libget based repository systems.

py_libget maintains a cache of previously downloaded icons, screenshots and repo jsons and uses an etagging system to minimize redownloads and save bandwidth.
The install / uninstall process should be thread-safe as long as you don't install duplicates of the same package at the same time and don't install and uninstall the same package at the same time.
The install method takes a callback that allows it to update frontends (GUIs, Flask apps, etc) from the backend thread.

It also includes a command line mode for use in scripting, the command line mode has a `--bundle` option that allows you to batch install a list of packages or generate a zip that can be extracted to an SD card.
There are also a number of other features, see `python -m py_libget -help` for more details on command line usage.
"""

try:
    from py_simple_readme import readme_generator
    from src.py_libget import repository, package_manager, parser, webhandler, version

    IGNORED_METHODS = []
    with open(os.path.join(os.path.dirname(__file__), "./pyproject.toml"), "rb") as f:
        config = tomllib.load(f)
    with open(os.path.join(os.path.dirname(__file__), "./changelog.json")) as f:
        changelog = json.load(f)
    name = config["project"]["name"]
    description = config["project"]["description"]
    author = config["project"]["authors"][0]["name"]
    # dependencies = config["project"]["dependencies"]
    installation_message = f"""Available on pip - `pip install {name}`"""
    gen = readme_generator(title=f"{name} {version}", ignored=IGNORED_METHODS)
    gen.set_slogan(description)
    gen.set_changelog({k: changelog[k] for k in reversed(changelog.keys())})
    gen.add_heading_1("About", add_toc=True)
    gen.add_paragraph(about)
    gen.add_heading_1("Dependencies", add_toc=True)
    gen.add_paragraph("None")
    gen.add_heading_1("Installation", add_toc=True)
    gen.add_paragraph(installation_message)
    gen.add_heading_1("Usage", add_toc=True)
    gen.increase_toc_depth()
    gen.add_heading_2("Command Line Usage", add_toc=True)
    gen.add_code_block(cli_usage, lang="")
    gen.add_paragraph(cli_example)
    gen.add_heading_2("Module Usage", add_toc=True)
    gen.add_code_block(basic_usage)
    gen.increase_toc_depth()
    gen.add_heading_3("Objects", add_toc=True)
    gen.handle_class_list([repository, package_manager, parser, webhandler])
    gen.decrease_toc_depth()
    gen.decrease_toc_depth()
    gen.add_heading("Credits / Thanks", add_toc=True)
    gen.add_paragraph(thanks)
    with open(os.path.join(os.path.dirname(__file__), "README.md"), "w+") as f:
        f.write(gen.assemble())
except Exception as e:
    raise e
    sys.exit(1)
sys.exit(os.EX_OK)
