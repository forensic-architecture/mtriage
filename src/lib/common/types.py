from typing import Dict, NewType

# A dictionary where the key is the filename, and the value is the bytes to store.
ElementContents = NewType('ElementContents', Dict[str, bytes])
