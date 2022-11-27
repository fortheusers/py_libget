import os, json, argparse
from .py_libget import repository


def parse_bundle(path: str) -> list:
    """Loads and parses a bundle file info a list of package names"""
    with open(path) as f:
        lines = [l.strip() for l in f.readlines()]
        return [l for l in lines if l and not l.startswith("#")]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="py_libget CLI - Interact with libget repositories and manage package installs. Runs Bundle -> Install -> Uninstall processes if multiple are specified."
    )
    parser.add_argument(
        "repository",
        type=str,
        help="URL of the libget repository.",
    )
    parser.add_argument(
        "install_path",
        nargs="?",
        default=os.getcwd(),
        type=str,
        help="Path to SD Card root or target dir. Defaults to current working dir if not specified.",
    )
    parser.add_argument(
        "-b",
        "--bundle",
        type=str,
        help="Path to bundle file. Bundles files are plaintext with one package name per line, comments are allowed by starting a line with a #. Will install / update all packages in the bundle",
    )
    parser.add_argument(
        "-i",
        "--install",
        nargs="+",
        help="List of package names to install / update, separated by spaces.",
    )
    parser.add_argument(
        "-u",
        "--uninstall",
        nargs="+",
        help="List of package names to uninstall, separated by spaces.",
    )
    parser.add_argument(
        "-sc",
        "--screenshot",
        nargs="+",
        help="Provide one or more package names separated by spaces (minimum 1), screenshots will be downloaded to cache. A map of the downloaded files will be printed on download completion.",
    )
    parser.add_argument(
        "-ic",
        "--icon",
        nargs="+",
        help="Provide one or more package names separated by spaces (minimum 1), icons will be downloaded to cache. A map of the downloaded files will be printed on download completion.",
    )

    args = parser.parse_args()

    repo = repository("CLI", args.repository, defer_load=False)
    repo.set_install_path(args.install_path)

    installed = []
    failed = []
    uninstalled = []
    uninstalled_failed = []
    screenshots_downloaded = {}
    icons_downloaded = {}

    if args.bundle:
        if not repo.check_if_get_init():
            repo.init_get()
        packages = parse_bundle(args.bundle)
        for p in packages:
            package = repo.package_lookup[p]
            if not package:
                print(f"Failed to find {p} in repo. Skipping.")
                failed.append(p)
                continue
            repo.install_package(package)
            installed.append(p)

    if args.install:
        if not repo.check_if_get_init():
            repo.init_get()
        for p in args.install:
            package = repo.package_lookup[p]
            if not package:
                print(f"Failed to find {p} in repo. Skipping.")
                failed.append(p)
                continue
            repo.install_package(package)
            installed.append(p)

    if args.uninstall:
        if not repo.check_if_get_init():
            repo.init_get()
        for p in args.uninstall:
            package = repo.package_lookup[p]
            if not p in repo.get_packages():
                print(f"{p} not installed. Skipping uninstall.")
                uninstalled_failed.append(p)
                continue
            repo.uninstall_package(package)
            uninstalled.append(p)

    if args.screenshot:
        for p in args.screenshot:
            screenshots_downloaded[p] = repo.get_screenshot(p)

    if args.icon:
        for p in args.icon:
            icons_downloaded[p] = repo.get_icon(p)

    print("Finished processing.")
    if installed:
        print("\nInstalled:")
        for p in installed:
            print(f"\t- {p}")
    if failed:
        print("\nFailed to install:")
        for p in installed:
            print(f"\t- {p}")
    if uninstalled:
        print("\nUninstalled:")
        for p in uninstalled:
            print(f"\t- {p}")
    if uninstalled_failed:
        print("\nFailed to uninstall:")
        for p in uninstalled_failed:
            print(f"\t- {p}")
    if screenshots_downloaded:
        print("\nScreenshots:")
        print(json.dumps(screenshots_downloaded, indent=4))
    if icons_downloaded:
        print("\nIcons:")
        print(json.dumps(icons_downloaded, indent=4))
