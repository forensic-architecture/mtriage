class SelectorNotFoundError(Exception):
    def __init__(self, selector):
        super().__init__(
            f"""Could not find a valid selector named '{selector}'. Ensure that you have a folder named '{selector}'
            in the selectors directory, and that it exports a valid Selector."""
        )


class AnalyserNotFoundError(Exception):
    def __init__(self, analyser):
        super().__init__(
            f"""Could not find a valid analyser named '{analyser}'. Ensure that you have a folder named '{analyser}'
            in the analysers directory, and that it exports a valid Analyser."""
        )


class WorkingDirectorNotFoundError(Exception):
    def __init__(self, workdir):
        super().__init__(
            f"""The working directory path that you specified, '{workdir}', does not exist or is otherwise corrupted."""
        )


class InvalidPhaseError(Exception):
    def __init__(self):
        super().__init__("The 'phase' argument must be either 'select' or 'analyse'.")


class ElementOperationFailedSkipError(Exception):
    def __init__(self, msg):
        super().__init__(f"{msg} - skipping element")


class ElementOperationFailedRetryError(Exception):
    def __init__(self, msg):
        super().__init__(f"{msg} - attempt retry")
