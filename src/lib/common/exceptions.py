class SelectorNotFoundError(Exception):
    """ Cannot find selector that was specified. """
    def __init__(self, selector):
        super().__init__(f"""Could not find a valid selector '{selector}'. Ensure that you have a folder named
                         '{selector}' in the selectors directory, and that it exports a valid Selector.""")

class AnalyserNotFoundError(Exception):
    """ Cannot find analyser that was specified. """
    def __init__(self, analyser):
        super().__init__(f"""Could not find a valid analyser '{analyser}'. Ensure that you have a folder named
                         '{analyser}' in the analysers directory, and that it exports a valid Analyser.""")

class WorkingDirectorNotFoundError(Exception):
    def __init__(self, workdir):
        super().__init__(f"""The working directory path that you specified, {workdir}, does not exist or is otherwise
                         corrupted.""")
