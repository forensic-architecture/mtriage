from lib.common.analyser import Analyser

class DarknetAnalyser(Analyser):
    def run(self, media):
        # TODO: this analyser is a stub currently.
        print(list(media["youtube"]["derived"]["frames"].keys()))


