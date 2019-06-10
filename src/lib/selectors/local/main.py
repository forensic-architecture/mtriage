from lib.common.selector import Selector
import pandas as pd
import os
from shutil import copyfile


class LocalSelector(Selector):
    """ A simple selector for importing local files into mtriage.

    It recursively finds every file in a source_folder specified in the
    config (see example script 4.select_local.sh) and imports each file
    into its own element. The element ID is the file's name concatenated
    with its extension.

    n.b. the directory being imported must be located within the mtriage
    directory to be accessible inside the docker container (the temp
    folder is recommended).
    """

    def index(self, config):

        if not os.path.exists(self.ELEMENT_MAP):
            df = self._run(config, self.DIR)
            return df
        else:
            self.logger("File already exists for index--not running again.")
            return None

    def retrieve_element(self, element, config):

        dest = element["dest"]
        src_path = element["path"]
        name = element["name"]

        extension = element["extension"]
        if not os.path.exists(dest):
            os.makedirs(dest)
        dest_path = f"{dest}/{name}.{extension}"
        copyfile(src_path, dest_path)
        self.logger("retrieved file: " + dest_path)

    def _run(self, config, output_path):
        results = []
        src = config["source_folder"]
        os.listdir(src)
        for root, dirs, files in os.walk(src):
            for file in files:
                f = file.split(".")
                results.append(
                    {
                        "name": f[0],
                        "extension": f[1],
                        "path": os.path.join(root, file),
                        "element_id": f"{f[0]}{f[1]}",
                    }
                )
                self.logger("indexed file: " + os.path.join(root, file))
        return pd.DataFrame(results)
