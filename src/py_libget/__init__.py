from .version import __version__, version
from .package_manager import package_manager
from .parser import parser
from .webhandler import webhandler


class repository(package_manager, parser, webhandler):
    """An object for interacting with all parts of a libget repository."""

    def __init__(
        self,
        name: str,
        domain: str,
        defer_load: bool = True,
        force_cached: bool = False,
    ):
        self.name, self.domain = name, domain
        webhandler.__init__(self, domain)
        package_manager.__init__(self, self)
        parser.__init__(self)
        if not defer_load:
            if force_cached:
                self.load_cached_repo()
            else:
                self.load_repo()

    def load_repo(self) -> str:
        """Loads / reloads repo from file. `Returns the loaded repo as a List.`"""
        if not (
            repo := webhandler.get_json(self, self.name, self.domain + "repo.json")
        ):
            raise ValueError("Failed to load repo")
        return parser.load_repo_file(self, repo)

    def load_cached_repo(self) -> list:
        """Loads / reloads repo from cached file. `Returns the loaded repo as a List.`"""
        if not (repo := webhandler.get_cached_json(self, self.name)):
            raise ValueError("Failed to load cached repo")
        return parser.load_repo_file(self, repo)
