from lib.common.selector import Selector
from lib.common.etypes import Etype
import os
from shutil import copyfile


class LocalSelector(Selector):
    """ A simple selector for importing local files into mtriage.

    It recursively finds every file in a source_folder specified in the
    config (see example script 4.select_local.sh) and imports each file
    into its own element. The element ID is the file's name concatenated
    with its extension.

    n.b. the directory being imported must be located within the mtriage
    directory to be accessible inside the docker container (the media
    folder is recommended).
    """

    def index(self, config):
        if (
            ("force" in config)
            and (config["force"] is False)
            and os.path.exists(self.ELEMENT_MAP)
        ):
            self.logger("File already exists for index--not running again.")
            return None

        self.abs_src = f"/mtriage/{config['source_folder']}"

        if not os.path.exists(self.abs_src):
            raise Exception(
                "The 'source_folder' you specified for the 'local' selector does not exist."
            )
            return None

        return self._run(config)

    def __copyfile(self, base, src_path, name, extension, dest_path):
        if not os.path.exists(base):
            os.makedirs(base)
        copyfile(src_path, dest_path)
        self.logger("file copied: " + dest_path)

    def retrieve_element(self, element, config):
        base = element["base"]

        if self.is_aggregate():
            self.logger("retrieving element agg")
            for mock_el in self.results:
                self.__copyfile(
                    base, mock_el[2], mock_el[0], mock_el[1], f"{base}/{mock_el[0]}.{mock_el[1]}"
                )
        else:
            src_path = element["path"]
            name = element["name"]
            extension = element["extension"]
            dest_path = f"{base}/{name}.{extension}"
            self.__copyfile(base, src_path, name, extension)

    def is_aggregate(self):
        return "aggregate" in self.CONFIG and self.CONFIG["aggregate"]

    def _run(self, config):
        self.logger("Indexing local folder...")
        results = [["name", "extension", "path", "id"]]
        for root, dirs, files in os.walk(self.abs_src):
            self.logger(dirs)
            for file in files:
                f = file.split(".")
                results.append([f[0], f[1], os.path.join(root, file), f"{f[0]}{f[1]}"])
                self.logger("indexed file: " + os.path.join(root, file))
        if self.is_aggregate():
            self.results = results[1:]
            # NB: hacky way to just make retrieve element run once.
            return [
                ["id"],
                ["all_images"],
            ]
        return results
