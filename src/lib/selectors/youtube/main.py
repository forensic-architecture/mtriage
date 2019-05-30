import youtube_dl
import json
import os
from lib.common.selector import Selector
from .select import selector_run
from .retrieve import id_from_url, vid_exists, get_meta_path


class YoutubeSelector(Selector):
    def index(self, config):
        if not os.path.exists(self.SELECT_MAP):
            df, logs = selector_run(config, self.FOLDER)
            self.index_complete(df, logs)
        else:
            self.index_complete(
                None, ["File already exists for index--not running again."]
            )

    def setup_retrieve(self):
        self.ydl = youtube_dl.YoutubeDL(
            {
                "outtmpl": f"{self.RETRIEVE_FOLDER}/%(id)s/%(id)s.mp4",
                "format": "worstvideo[ext=mp4]",
            }
        )

    def retrieve_row(self, row):
        url = row.url
        ydl = self.ydl
        LOGS = []
        with ydl:
            vid_id = id_from_url(url)
            vid_does_exist = vid_exists(vid_id, self.RETRIEVE_FOLDER)

            if vid_does_exist:
                LOGS.append(f"{vid_id} has already been downloaded.")
                self.retrieve_row_complete(False, LOGS)
                return
            try:
                result = ydl.extract_info(url)
                #  save meta as a precaution
                with open(get_meta_path(vid_id, self.RETRIEVE_FOLDER), "w+") as fp:
                    json.dump(result, fp)
                LOGS.append(f"{vid_id}: video and meta downloaded successfully.")
                self.retrieve_row_complete(True, LOGS)

            except youtube_dl.utils.DownloadError:
                LOGS.append(
                    f"Something went wrong downloading {vid_id}. It may have been deleted."
                )
                self.retrieve_row_complete(False, LOGS)
