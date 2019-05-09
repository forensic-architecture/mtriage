# Phase 1: Search 

---

The bash file 1.index.sh calls a python program [search.py](index/search.py), which takes in the arguments provided by the user, that is, a range of dates and a search term. It then
crawls through the YouTube API adding metadata for each video meeting such criteria to the CSV file. 

The CSV output file contains the following five fields: 

	-- idx  (index number for video)     
	-- url  (YouTube url)
	-- title (title for video containing search term)
	-- desc (description from YouTube metadata)
	-- published (date of publication for video)

In addition to this, the search generates a txt log file detailing the number of positive results from the crawl, the running time, and any errors. 