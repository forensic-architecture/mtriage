from lib.common.analyser import Analyser


class DarknetAnalyser(Analyser):
    def get_elements(self, config):
        return self.media["youtube"]["derived"]["frames"].keys()

    def run_element(self, element, config):
        # TODO: this analyser is a stub currently.
        print(element)
