# Phase 2: Retrieve 

---

The bash file 2.retrieve.sh calls a python program [download.py](retrieve/download.py), which takes in the CSV file produced in Phase 1, that is, a CSV file listing all videos published during the selected date range and containing the search term in their title. It scrapes the YouTube API to download the listed videos and splice them into frames, which it stores in a results folder. 

## Input

Phase 1 produces a CSV file that includes an index number for each video, the date of its publication, and the corresponding YouTube url. The retrieve program uses this CSV file in order to download all these videos and store frames from these videos and store them.


## Output

Phase 2 generates a folder per video. The videos are downloaded in batches, which is currently predetermined as batches of 10. After the videos are downloaded, a second python program [get_frames.py](retrieve/get_frames.py) is called, which splices the video and stores its frames. 

At the moment, this is determined to download 1 frame per second (fps=1). Each frame is indexed and saved as a .jpg file in the corresponding folder, named by the ID of the YouTube video. After the frames are sampled, the video file is deleted.

In addition to a folder per video containing all sampled frames, Phase 2 produces a .json file per video containing its metadata.