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


class InvalidAnalyserConfigError(Exception):
    def __init__(self, msg):
        super().__init__(f"Invalid analyser config - {msg}")


class InvalidSelectorConfigError(Exception):
    def __init__(self, msg):
        super().__init__(f"Invalid selector config - {msg}")


class InvalidConfigError(Exception):
    def __init__(self, msg):
        super().__init__(f"Invalid config - {msg}")


class ElementShouldSkipError(Exception):
    def __init__(self, msg):
        super().__init__(f"{msg} - skipping element")


class ElementShouldRetryError(Exception):
    def __init__(self, msg):
        super().__init__(f"{msg} - attempt retry")


class SelectorIndexError(Exception):
    def __init__(self, msg):
        super().__init__(f"Selector index failed - {msg}")


class ImproperLoggedPhaseError(Exception):
    def __init__(self, fname):
        super().__init__(
            f"""The method '{fname}' does not belong to a class that inherits from MTModule. The
                        logged_phase decorator can only be applied to methods on such a class."""
        )


class BatchedPhaseArgNotList(Exception):
    def __init__(self, fname):
        super().__init__(
            f"""The method '{fname}' cannot be batched. The 'batched_logged_phase' decorator can only be applied to a function that takes a generator as its first and only argument. """
        )


class MTriageStorageCorruptedError(Exception):
    def __init__(self, fname):
        super().__init__(
            "MTriage encountered an unexpected file structure in selectors or analysers. Ensure you specified the correct working directory."
        )


class EtypeCastError(Exception):
    def __init__(self, msg):
        super().__init__(f"Could not cast etype: {msg}")


class InvalidElementsIn(Exception):
    def __init__(self, comp, msg):
        super().__init__(f"The elements_in '{comp}' is not valid. {msg}")


class InvalidAnalyserElements(Exception):
    pass
