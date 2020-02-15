import json, requests, re, os
from html.parser import HTMLParser
from urllib.request import urlretrieve
from lib.common.selector import Selector
from lib.common.etypes import Etype


class fourchan(Selector):
    """ A selector that leverages the native 4chan API.

    https://github.com/4chan/4chan-API
    """

    def index(self, config):
        # results = []
        # board = config["board"]
        # max_posts = config["max_posts"]
        # #TODO: add thread id
        
        # req = f"https://a.4cdn.org/{board}/threads.json"

        # #-- Various requests --#
        # # Boards
        # content = json.loads(
        #     requests.get(req).content
        # )
        # # https://a.4cdn.org/po/thread/570368.json
        # post_count = 0
        # for page in content:
        #     if post_count < max_posts:
        #         post_count += 1
        #         print(post_count)
        #         for threads in page["threads"]:
        #             thread_id = threads["no"]
        #             req = f"https://a.4cdn.org/{board}/thread/{thread_id}.json"
        #             thread_content = json.loads(requests.get(req).content)["posts"] # thread content is a list of posts
        #             for post in thread_content:
        #                 post_row = []

        #                 post_row.append(str(post['no']))
        #                 post_row.append(str(post['time']))
                        
        #                 # Comment
        #                 try: comment = re.sub('<[^<]+?>', '', post['com']) # TODO: regex removes _some_ HTML. A better solution is required
        #                 except KeyError: comment = "..."
        #                 post_row.append(comment)

        #                 # Filename
        #                 try: filename = post['filename']
        #                 except KeyError: filename = ""

        #                 if filename != "":
        #                     time_id = post['tim']
        #                     extension = post['ext']
        #                     full_file = f"{filename}{extension}"
        #                     post_row.append(full_file)
        #                     file_url = f"https://i.4cdn.org/{board}/{time_id}{extension}"
        #                     post_row.append(file_url)
        #                 elif filename == "":
        #                     post_row.append("")
        #                     post_row.append("")
                        
        #                 results.append(post_row)

        # return results     
        fake_return = [
            [4813283183218, "14342", "testc", "foo", "testurl"]
        ]
        fake_return.insert(0, ["id", "datetime", "comment", "filename", "fileurl"])

        return fake_return
    
    def retrieve_element(self, element, config):
        dest = element["base"]
    #     dest = element["base"]
        # filename = element["filename"]
        # out_path = os.path.join(dest, fileurl)
        # url = element["fileurl"]

        # urlretrieve(url, out_path)
        
        # img_data = requests.get(fileurl).content
        # # TODO: streaming the file
        # with open(out_path, 'wb') as handler:
        #     handler.write(img_data)