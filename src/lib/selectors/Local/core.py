import os
from pathlib import Path
from shutil import copyfile
from lib.common.selector import Selector
from lib.common.etypes import Etype, Index
from lib.common.exceptions import SelectorIndexError


BASE = Path("/mtriage")


class Local(Selector):
    """A simple selector for importing local files into mtriage.

    It recursively finds every file in a source_folder specified in the config
    (see example script 4.select_local.sh) and imports each file into its own
    element. The element ID is the file's name concatenated with its extension.

    n.b. the directory being imported must be located within the mtriage
    directory on the mtriage host to be accessible inside the docker container
    (the media folder is recommended).
    """

    out_etype = Etype.Any

    def __init__(self, *args):
        super().__init__(*args)

    def is_aggregate(self):
        return "aggregate" in self.config and self.config["aggregate"]

    def index(self, config):
        src = Path(config["source"])
        abs_src = BASE / src
        if not os.path.exists(abs_src):
            raise SelectorIndexError(
                f"The 'source' folder {src} could not be found. Ensure it is in the same directory asmtriage."
            )
        return self._index(abs_src)

    def _index(self, abs_src):
        self.logger("Indexing local folder...")
        results = [["id", "path"]]
        excluded = self.config.get("exclude", [])
        for root, _, files in os.walk(abs_src):
            main = Path(abs_src)
            root = Path(root)
            for file in files:
                if file == ".mtbatch" or file in excluded:
                    continue
                fp = root / file
                elid = root.name if (root.name != main.name) else fp.stem
                results.append([elid, fp])
                self.logger(f"indexed file {fp} as: {elid}")
        if self.is_aggregate():
            # `self.results` used in `retrieve_element` for paths.
            self.results = results[1:]
            # NB: hacky way to just make `retrieve_element` run just once.:
            return Index([["id"], ["IS_AGGREGATE"]])
        return Index(results)

    def retrieve_element(self, element, config):
        if self.is_aggregate():
            og_folder = Path(config["source"])
            return Etype.Any(og_folder.name, paths=[x[1] for x in self.results])
        else:
            return Etype.Any(element.id, paths=[element.path])


module = Local
