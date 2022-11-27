import os, sys, tempfile
from src import repository


def test():
    print("Running test")
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
        raise LookupError(f"Failed to find {package_name} in package")
    # Make dir to test with and set repo to install packages there
    repo.set_install_path(tempfile.TemporaryDirectory().name)
    repo.init_get()
    repo.install_package(package)
    repo.uninstall_package(package)


if __name__ == "__main__":
    try:
        test()
        sys.exit(os.EX_OK)
    except Exception as e:
        print(f"Encountered error running test - {e}")
        sys.exit(1)
