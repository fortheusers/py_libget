"""Object to hold and parse libget repos"""
import json

# Ignored list must be arranged so
# substrings don't accidentally get
# removed before the longer strings
VERSION_IGNORED = [
    "switch",
    "wiiu",
    "wii",  # After wiiu
    "3ds",
    "ds",  # After 3ds
    "vita",
    "gc",
    "gamecube",
    "ps5",
    "ps4",
    "ps3",
    "ps2",
    "psp",
    "psvita",
    "ps",
    "playstation5",
    "playstation4",
    "playstation3",
    "playstation2",
    "playstation",
    # Need this order
    "xbox360",
    "xb360",
    "xbox",
    "xb",
]


class parser(object):
    """Object to hold and parse libget repos"""

    def __init__(self):
        self.init()

    def init(self) -> None:
        """Reinitialize parser. `Returns a Dict mapping package names as Strings to package entries as Dicts`"""
        self.all = []
        self.advanced = []
        self.emus = []
        self.games = []
        self.loaders = []
        self.themes = []
        self.tools = []
        self.misc = []
        self.legacy = []

        self.map = {
            "advanced": self.advanced,
            "concept": self.misc,
            "emu": self.emus,
            "game": self.games,
            "loader": self.loaders,
            "theme": self.themes,
            "tool": self.tools,
            "misc": self.misc,
            "media": self.misc,
            "misc": self.misc,
            "legacy": self.legacy,
        }

        self.list_list = [
            self.all,
            self.advanced,
            self.emus,
            self.games,
            self.loaders,
            self.themes,
            self.tools,
            self.misc,
            self.legacy,
        ]

        self.package_lookup = {}

    def clear(self) -> dict:
        """Alias for parser.init(). `Returns a Dict mapping package names as Strings to package entries as Dicts`"""
        return self.init()

    def load_repo_file(self, repo_file: str) -> list:
        """Loads appstore json. `Returns a List of Dicts`"""
        if not repo_file:
            raise ValueError(f"Argument repo_file cannot be NoneType")
        self.clear()
        with open(repo_file, encoding="utf-8") as repojson:
            self.all = json.load(repojson)["packages"]
        for entry in self.all:
            try:
                self.map.get(entry["category"], self.map["misc"]).append(entry)
            except:
                pass
            self.package_lookup[entry["name"]] = entry
        print(f"Loaded {len(self.all)} appstore entries")
        return self.all

    def get_package_dict(self, name: str) -> dict:
        """Get entry for a given package name. `Returns a Dict, empty on failure.`"""
        return self.package_lookup.get(name, {})

    def clean_version(self, ver: str, name: str) -> str:
        """Clean a version. `Returns a String`"""
        ver = ver.lower().strip("v").split(" ")[0]
        for v in [*VERSION_IGNORED, name]:
            ver = ver.replace(v, "")
        return ver.strip("-")
