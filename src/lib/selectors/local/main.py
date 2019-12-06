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
        self.logger(config["force"])
        if ("force" in config) and (config["force"] is False) and os.path.exists(self.ELEMENT_MAP):
            self.logger("File already exists for index--not running again.")
            return None

        self.abs_src = f"/mtriage/{config['source_folder']}"

        if not os.path.exists(self.abs_src):
            raise Exception("The 'source_folder' you specified for the 'local' selector does not exist.")
            return None

        # return self._run(config)

    def retrieve_element(self, element, config):
        base = element["base"]
        src_path = element["path"]
        name = element["name"]

        extension = element["extension"]
        if not os.path.exists(base):
            os.makedirs(base)
        dest_path = f"{base}/{name}.{extension}"
        copyfile(src_path, dest_path)
        self.logger("retrieved file: " + dest_path)

    def _run(self, config):
        results = [["name", "extension", "path", "id"]]
        for root, dirs, files in os.walk(self.abs_src):
            self.logger(dirs)
            for file in files:
                f = file.split(".")
                results.append([f[0], f[1], os.path.join(root, file), f"{f[0]}{f[1]}"])
                self.logger("indexed file: " + os.path.join(root, file))
        return results
