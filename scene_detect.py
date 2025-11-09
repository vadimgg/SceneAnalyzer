import os
import cv2
from scenedetect import SceneManager, open_video
from scenedetect.detectors import ContentDetector


def detect_scenes(video_path: str, threshold: float = 30.0):
    """Detect scenes using PySceneDetect."""
    print(f"🔍 Detecting scenes in '{video_path}' (threshold={threshold}) ...")
    video = open_video(video_path)
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))
    scene_manager.detect_scenes(video)
    scene_list = scene_manager.get_scene_list()
    print(f"✅ Detected {len(scene_list)} scenes.")
    return scene_list


def extract_scene_frames(video_path: str, scene_list, output_dir: str):
    """Extract one representative frame (center) per scene."""
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    scene_data = []

    for i, (start, end) in enumerate(scene_list, start=1):
        start_sec = start.get_seconds()
        end_sec = end.get_seconds()
        mid_sec = (start_sec + end_sec) / 2.0
        frame_idx = int(mid_sec * fps)

        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret:
            continue

        img_path = os.path.join(output_dir, f"scene-{i:03d}.jpg")
        cv2.imwrite(img_path, frame)
        duration = round(end_sec - start_sec, 1)
        scene_data.append({
            "num": i,
            "start": str(start),
            "duration": duration,
            "image": img_path,
        })

    cap.release()
    return scene_data


