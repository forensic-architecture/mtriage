import twint
from lib.common.selector import Selector
from lib.common.etypes import Etype


class TwitterSelector(Selector):
    """ A selector for scraping tweets.

    It leverages 'twint' - https://github.com/twintproject/twint - under
    the hood.
    """

    def index(self, config):
        return None

    def retrieve_element(self, element, config):
        pass
