import requests
import json

# Should be a board > thread > post > content


boards_requests = "https://a.4cdn.org/boards.json"
archive_requests = "https://a.4cdn.org/po/archive.json"

#-- Various requests --#
# Boards
boards_response = requests.get(boards_requests)
boards_content = json.loads(boards_response.content)

# Archive
archive_response = requests.get(archive_requests)
archive_content = json.loads(archive_response.content)

# You should be to ask for a certain media type, text and then some filters

# Get boards
# for board in content["boards"]:
#     print(board["title"])

# Get archive
# Returns you a list of thread ID's which have to be later parsed
print(archive_content)


