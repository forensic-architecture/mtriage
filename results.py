import os
import json
import sys

def get_video_meta(video_id, keras_pretrained_path):
    """Fetch the video title, upload date, and view count from the meta.json file."""
    meta_file_path = os.path.join(keras_pretrained_path, 'data', video_id, 'meta.json')
    with open(meta_file_path, 'r') as meta_file:
        meta_data = json.load(meta_file)
    title = meta_data.get('title', 'N/A')
    upload_date = meta_data.get('upload_date', 'N/A')
    view_count = meta_data.get('view_count', 'N/A')
    return title, upload_date, view_count

def main(keras_pretrained_path):
    # Dictionary to store the results
    labels_dict = {}

    # Iterate through the folders inside the 'derived' directory
    for video_id in os.listdir(keras_pretrained_path):
        video_path = os.path.join(keras_pretrained_path, video_id)

        # Check if it's a directory (i.e., a video ID folder)
        if os.path.isdir(video_path):
            # Path to the preds.json file for the current video
            preds_file_path = os.path.join(video_path, 'preds.json')

            # Check if the preds.json file exists
            if os.path.exists(preds_file_path):
                with open(preds_file_path, 'r') as file:
                    content = file.read()

                    # Check if the file is empty
                    if content:
                        # Parse the JSON content
                        preds_data = json.loads(content)

                        # Iterate through the labels and their data
                        for label, data in preds_data.get('labels', {}).items():
                            frames = data.get('frames', [])
                            scores = data.get('scores', [])

                            # Compile the frames and their corresponding scores
                            frame_scores = [{"frame": frame, "score": score} for frame, score in zip(frames, scores)]

                            # Get video metadata
                            title, upload_date, view_count = get_video_meta(video_id, keras_pretrained_path)

                            # Append the video info to the label's list
                            if label not in labels_dict:
                                labels_dict[label] = []
                            labels_dict[label].append({
                                "video_id": video_id,
                                "video_title": title,
                                "upload_date": upload_date,
                                "view_count": view_count,
                                "frame_scores": frame_scores
                            })

    # Print the results
    for label, videos in labels_dict.items():
        print(f"Assigned Label: {label}")
        print(f"Total Number of Videos with the Label Found: {len(videos)}")
        print("Videos where label was found:")
        for video in videos:
            print(f"  Video Title: {video['video_title']} (ID: {video['video_id']})")
            print(f"  Upload Date: {video['upload_date']}")
            print(f"  View Count: {video['view_count']}")
            print("  Frames:")
            for frame_score in video['frame_scores']:
                print(f"    Frame: {frame_score['frame']}, Score: {frame_score['score']}")
            print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide the path to the Keras_Pretrained directory")
        sys.exit(1)
    keras_pretrained_path = sys.argv[1]
    main(keras_pretrained_path)
