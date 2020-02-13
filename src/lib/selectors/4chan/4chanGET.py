import requests, json, time, os

# Should be a board > thread > post > content

# parameters:
"""
--search-term
--pages?
--age
--replies
--structured or dump files (files go into a structured folder hierarchy)
"""

MIN_REPLIES = 1

base_dir = "/Users/james/4chanscraping"

board_choice = "pol"

req = f"https://a.4cdn.org/{board_choice}/threads.json"

#-- Various requests --#
# Boards
content = json.loads(
    requests.get(req).content
)
# https://a.4cdn.org/po/thread/570368.json
for page in content:
    for threads in page["threads"]:
        if threads["replies"] >= MIN_REPLIES:
            thread_id = threads["no"]
            req = f"https://a.4cdn.org/{board_choice}/thread/{thread_id}.json"
            thread_content = json.loads(requests.get(req).content)["posts"]
            # thread content is a list of posts
            for content in thread_content:
                # now operate on a post

                try:
                    filename = content['filename']
                except KeyError:
                    print("No file for that ")
                else:
                    content_id = content['no']
                    time_id = content['tim']
                    comment = content['com'] #strip HTML from this
                    extension = content['ext']
                    full_file = f"{filename}{extension}"
                    # https://i.4cdn.org/[board]/[4chan image ID].[file extension]
                    file_url = f"https://i.4cdn.org/{board_choice}/{time_id}{extension}"
                    img_data = requests.get(file_url).content
                    out_path = os.path.join(base_dir, full_file)
                    with open(out_path, 'wb') as handler:
                        handler.write(img_data)
                    time.sleep(1)