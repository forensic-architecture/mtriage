from lib.common.analyser import Analyser
from lib.common.get_module import get_module
import os
from shutil import copyfile, rmtree
from lib.common.etypes import Etype, cast_to_etype


class MetaAnalyser(Analyser):
    def get_in_etype(self):
        return self.children[0].get_in_etype()

    def get_out_etype(self):
        return self.children[-1].get_out_etype()

    def __init__(self, config, module, dir):
        super().__init__(config, module, dir)

        def createChild(module):
            child_name = module["name"]
            child_config = module["config"]

            # this is going to break everything?
            child_config["elements_in"] = ["thisisahack"]

            ChildAnalyser = get_module("analyser", child_name)
            if ChildAnalyser is None:
                # TODO: there should be a typed error here
                raise Exception(
                    f"The module you have specified, {child_name}, does not exist"
                )
            return ChildAnalyser(child_config, child_name, dir)

        self.children = [createChild(x) for x in config["children"]]

    def pre_analyse(self, config):
        for child in self.children:
            child.PHASE_KEY = "pre-analyse"
            child.pre_analyse(child.CONFIG)
            self._extract_logs_from(child)
            self.logger(f"Setup child analyser {child.NAME}")

    def analyse_element(self, element, config):

        src = None
        child_element = None
        for index, child in enumerate(self.children):
            child_element = self._derive_child_element(index, element, src, child)
            child.PHASE_KEY = "analyse"
            child.analyse_element(child_element, child.CONFIG)
            el_id = element["id"]
            self.logger(f"Analysed element {el_id} in {child.NAME}")
            src = child_element["dest"]
            self._extract_logs_from(child)
        self._finalise_element(config, child_element, element)

    def post_analyse(self, config, derived_dirs):
        for child in self.children:
            child.PHASE_KEY = "post-analyse"
            child.post_analyse(config, derived_dirs)
            self._extract_logs_from(child)
        delete_cache = config["delete_cache"]
        if delete_cache:
            for derived_dir in derived_dirs:
                cache = f"{derived_dir}/cache"
                self.logger("deleting cache: " + cache)
                rmtree(cache)

    def _derive_child_element(self, child_index, element, child_base, analyser):

        src = child_base if child_base != None else element["base"]
        etype = self.children[child_index].get_in_etype()

        out_element = cast_to_etype(src, etype)

        el_id = element["id"]
        out_element["id"] = el_id

        meta_dest = element["dest"]
        rpl = "/" + el_id
        derived_dir = meta_dest.replace(rpl, "")
        dest = f"{derived_dir}/cache/meta_{child_index}_{analyser.NAME}/{el_id}"
        out_element["dest"] = dest

        if not os.path.exists(dest):
            os.makedirs(dest)

        return out_element

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
