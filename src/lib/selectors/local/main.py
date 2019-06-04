from lib.common.selector import Selector
import pandas as pd
import os
from shutil import copyfile


class LocalSelector(Selector):
    def index(self, config):
        if not os.path.exists(self.SELECT_MAP):
            df = self._run(config, self.FOLDER)
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
                        "element_id": f[0],
                    }
                )
                self.logger("indexed file: " + os.path.join(root, file))
        return pd.DataFrame(results)
