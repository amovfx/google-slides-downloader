import os
import pyaudio
import wave
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
import threading
import cv2


def list_image_files(folder_path):
    image_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp")
    image_files = []

    for file in sorted(os.listdir(folder_path)):
        if file.lower().endswith(image_extensions):
            image_files.append(os.path.join(folder_path, file))

    return image_files


def display_image(image_path, window, image_label):
    # Open the image using PIL
    img = Image.open(image_path)

    # Create a PhotoImage object from the PIL image
    photo = ImageTk.PhotoImage(img)

    # Update the existing label with the new image
    image_label.config(image=photo)
    image_label.image = photo  # Keep a reference to avoid garbage collection

    # Set the window size to match the image size
    window.geometry(f"{img.width}x{img.height+200}")

    # Center the window on the screen
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - img.width) // 2
    y = (screen_height - img.height) // 2
    window.geometry(f"+{x}+{y}")


class AudioRecorder:
    def __init__(self):
        self.audio_stream = None
        self.audio_frames = []
        self.is_recording = False
        self.audio_thread = None

    def start_recording(self):
        self.is_recording = True
        self.audio_frames = []

        p = pyaudio.PyAudio()
        self.audio_stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=1024,
        )

        self.audio_thread = threading.Thread(target=self.record_audio)
        self.audio_thread.start()

    def stop_recording(self, audio_file_path):
        self.is_recording = False

        if self.audio_thread:
            self.audio_thread.join()

        if self.audio_stream:
            try:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
            except:
                print("Error closing audio stream")

        try:
            with wave.open(audio_file_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
                wf.setframerate(44100)
                wf.writeframes(b"".join(self.audio_frames))
        except Exception as e:
            print(f"Error saving audio file: {e}")

        print(f"Audio saved: {audio_file_path}")

    def record_audio(self):
        while self.is_recording:
            self.audio_frames.append(self.audio_stream.read(1024))


class VideoRecorder:
    def __init__(self):
        self.video_capture = None
        self.video_writer = None
        self.is_recording = False
        self.video_thread = None

    def start_recording(self, video_file_path):
        self.is_recording = True

        self.video_capture = cv2.VideoCapture(0)
        if not self.video_capture.isOpened():
            print("Error: Could not open camera.")
            return

        frame_width = int(self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = 30.0

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.video_writer = cv2.VideoWriter(
            video_file_path, fourcc, fps, (frame_width, frame_height)
        )

        self.video_thread = threading.Thread(target=self.record_video)
        self.video_thread.start()

    def stop_recording(self):
        self.is_recording = False

        if self.video_thread:
            self.video_thread.join()

        if self.video_capture:
            self.video_capture.release()
        if self.video_writer:
            self.video_writer.release()
        cv2.destroyAllWindows()

    def record_video(self):
        while self.is_recording:
            ret, frame = self.video_capture.read()
            if ret:
                self.video_writer.write(frame)
            else:
                print("Error: Failed to capture video frame.")
                break


class Recorder:
    def __init__(self):
        self.audio_recorder = AudioRecorder()
        self.video_recorder = VideoRecorder()

    def start_recording(self, image_path):
        video_file_path = image_path.rsplit(".", 1)[0] + "_video.mp4"
        self.audio_recorder.start_recording()
        self.video_recorder.start_recording(video_file_path)

    def stop_recording(self, image_path):
        audio_file_path = image_path.rsplit(".", 1)[0] + "_audio.wav"
        self.audio_recorder.stop_recording(audio_file_path)
        self.video_recorder.stop_recording()


def main():
    # folder_path = input("Enter the path to the image folder: ")
    image_files = list_image_files(
        "/Users/andrew/Documents/Adobe/Premiere Pro/24.0/saga/01_Intro/S.A.A.G.A"
    )

    window = tk.Tk()
    window.title("Image Display and Recording")

    # Create a label for the image
    # Create a frame to hold the image
    image_frame = tk.Frame(window)
    image_frame.pack(fill=tk.BOTH, expand=True)

    # Create a label for the image inside the frame
    image_label = tk.Label(image_frame)
    image_label.pack(fill=tk.BOTH, expand=True)

    # Create a label for instructions at the bottom of the window
    instruction_label = tk.Label(window, text="Press space to start recording", pady=10)
    instruction_label.pack(side=tk.BOTTOM)

    current_image_index = 0
    recording = False

    recorder = Recorder()

    def toggle_recording(event):
        nonlocal recording, current_image_index
        if not recording:
            # Start recording
            recorder.start_recording(image_files[current_image_index])
            recording = True
            instruction_label.config(text="Press space to stop recording")
        else:
            # Stop recording
            recorder.stop_recording(image_files[current_image_index])
            recording = False
            current_image_index += 1
            if current_image_index < len(image_files):
                display_image(image_files[current_image_index], window, image_label)
                instruction_label.config(text="Press space to start recording")
            else:
                window.quit()

    window.bind("<space>", toggle_recording)

    # Display the first image
    display_image(image_files[current_image_index], window, image_label)

    def on_closing():
        nonlocal recording
        if recording:
            recorder.stop_recording(image_files[current_image_index])
        window.quit()

    window.protocol("WM_DELETE_WINDOW", on_closing)

    try:
        window.mainloop()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("All images processed.")
        try:
            window.destroy()
        except:
            pass


if __name__ == "__main__":
    main()
