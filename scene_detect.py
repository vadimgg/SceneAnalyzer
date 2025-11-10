import os
import cv2
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from scenedetect.frame_timecode import FrameTimecode


def detect_scenes(video_path, threshold=30.0):
    """Detect scenes using PySceneDetect."""
    print(f"🔍 Detecting scenes in '{video_path}' (threshold={threshold}) ...")
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))
    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)
    scene_list = scene_manager.get_scene_list()
    video_manager.release()

    print(f"✅ Detected {len(scene_list)} scenes.")
    return scene_list


def extract_scene_frames(video_path, scene_list, output_dir):
    """Extract 3 frames (start, middle, end) from each scene, including duration."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"🎞 Extracting 3 frames per scene...")

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    scene_data = []

    for i, (start, end) in enumerate(scene_list, start=1):
        start_frame = start.get_frames()
        end_frame = end.get_frames() - 1
        mid_frame = (start_frame + end_frame) // 2

        duration = round(end.get_seconds() - start.get_seconds(), 1)  # in seconds
        frames_to_capture = [start_frame, mid_frame, end_frame]
        frame_paths = []

        for j, frame_num in enumerate(frames_to_capture):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            if not ret:
                continue

            frame_file = os.path.join(output_dir, f"scene_{i:03d}_frame_{j+1}.jpg")
            cv2.imwrite(frame_file, frame)

            timestamp = FrameTimecode(frame_num, fps).get_timecode()
            frame_paths.append((frame_file, timestamp))

        # include duration here
        scene_data.append((i, frame_paths, duration))

    cap.release()
    return scene_data

