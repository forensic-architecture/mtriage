from lib.common.analyser import Analyser
from lib.common.analyser import paths_to_components
from lib.common.get_module import get_module
import os
from shutil import copyfile, rmtree


class MetaAnalyser(Analyser):
    def pre_analyse(self, config):

        self.child_analysers = []
        whitelist = self.CONFIG["elements_in"]

        child_module = config["children"]
        for module in child_module:
            child_name = module["name"]
            child_config = module["config"]
            ChildAnalyser = get_module("analyser", child_name)
            if ChildAnalyser is None:
                raise Exception(
                    f"The module you have specified, {child_name}, does not exist"
                )
            child_analyser = ChildAnalyser(child_config, child_name, self.BASE_DIR)
            child_analyser.PHASE_KEY = "pre-analyse"
            child_analyser.pre_analyse(child_config)
            self._extract_logs_from(child_analyser)
            self.child_analysers.append(child_analyser)
            self.logger(f"Setup child analyser {child_name}")

    def analyse_element(self, element, config):
        src = None
        child_element = None
        for index, child_analyser in enumerate(self.child_analysers):
            child_element = self._derive_child_element(
                index, element, src, child_analyser
            )
            child_analyser.PHASE_KEY = "analyse"
            child_analyser.analyse_element(child_element, child_analyser.CONFIG)
            el_id = element["id"]
            self.logger(f"Analysed element {el_id} in {child_analyser.NAME}")
            src = child_element["dest"]
            self._extract_logs_from(child_analyser)
        self._finalise_element(config, child_element, element)

    def post_analyse(self, config, derived_dirs):
        for child_analyser in self.child_analysers:
            child_analyser.PHASE_KEY = "post-analyse"
            child_analyser.post_analyse(config, derived_dirs)
            self._extract_logs_from(child_analyser)
        delete_cache = config["delete_cache"]
        if delete_cache:
            for derived_dir in derived_dirs:
                cache = f"{derived_dir}/cache"
                self.logger("deleting cache: " + cache)
                rmtree(cache)

    def _derive_child_element(self, child_index, element, child_src, analyser):
        derived_dir = element["derived_dir"]
        el_id = element["id"]
        dest = f"{derived_dir}/cache/meta_{child_index}_{analyser.NAME}/{el_id}"
        if not os.path.exists(dest):
            os.makedirs(dest)
        src = child_src if child_src != None else element["src"]
        return {"id": el_id, "derived_dir": derived_dir, "src": src, "dest": dest}

    def _finalise_element(self, config, last_child_element, element):

        el_id = element["id"]
        self.logger(f"Finalising element {el_id}")

        dest = element["dest"]
        src = last_child_element["dest"]

        for root, dirs, files in os.walk(src):
            for file in files:
                f_src = os.path.join(root, file)
                f_dest = os.path.join(dest, file)
                copyfile(f_src, f_dest)

    def _extract_logs_from(self, child):
        self._MTModule__LOGS = self._MTModule__LOGS + child._MTModule__LOGS
        child._MTModule__LOGS.clear()
