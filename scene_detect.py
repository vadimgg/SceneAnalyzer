import os
from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector
from scenedetect.frame_timecode import FrameTimecode

def detect_scenes(video_path, threshold=30.0):
    """Detect scenes in a video."""
    print(f"🔍 Detecting scenes in '{video_path}' (threshold={threshold}) ...")

    video = open_video(video_path)
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))
    scene_manager.detect_scenes(video)
    scenes = scene_manager.get_scene_list()

    print(f"✅ Detected {len(scenes)} scenes.")
    return scenes


def extract_scene_frames(video_path, scenes, output_dir):
    """Extract 3 frames (start, middle, end) for each detected scene."""
    import cv2
    import math

    os.makedirs(output_dir, exist_ok=True)
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)

    scene_data = []
    for i, (start_time, end_time) in enumerate(scenes, start=1):
        start_frame = int(start_time.get_frames())
        end_frame = int(end_time.get_frames())
        duration_frames = end_frame - start_frame

        if duration_frames <= 0:
            continue

        # Get frame numbers for start, middle, and end (avoid last frame)
        positions = [
            start_frame + int(duration_frames * 0.05),  # slightly into scene
            start_frame + int(duration_frames * 0.5),
            start_frame + int(duration_frames * 0.95),
        ]

        scene_images = []
        for j, frame_num in enumerate(positions, start=1):
            video.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            success, frame = video.read()
            if not success:
                continue
            frame_path = os.path.join(output_dir, f"scene_{i:03d}_{j}.jpg")
            cv2.imwrite(frame_path, frame)
            scene_images.append(frame_path)

        scene_data.append({
            "num": i,
            "start": str(start_time),
            "end": str(end_time),
            "duration": round((end_time - start_time).get_seconds(), 2),
            "images": scene_images
        })

    video.release()
    return scene_data

