import cv2
from moviepy.editor import AudioFileClip, VideoFileClip


def merge_audio_and_video(video, audio, filename):
    clip = VideoFileClip(video)
    audioclip = AudioFileClip(audio)

    min_duration = min(clip.duration, audioclip.duration)
    clip = clip.subclip(0, min_duration)
    audioclip = audioclip.subclip(0, min_duration)
    videoclip = clip.set_audio(audioclip)
    videoclip.write_videofile(filename, codec="libx264")


def create_video_clip_from_images(duration, data, filename, fps=10):
    frame_paths = []

    for _, dt in enumerate(data):
        st = round(dt["start"], 1)
        end = round(dt["end"], 1)

        end = round(end - 0.1, 1)

        num_frames = int(round((end - st), 1) * fps) + 1
        frames = [dt["filename"]] * num_frames
        frame_paths.extend(frames)

    frame_paths[: duration * fps]

    fourcc = cv2.VideoWriter_fourcc(*"MP4V")
    out = cv2.VideoWriter(filename, fourcc, fps, (512, 512))

    for image in frame_paths:
        img = cv2.imread(image)
        out.write(img)

    out.release()
    print(f"Number of frames {len(frame_paths)}")
