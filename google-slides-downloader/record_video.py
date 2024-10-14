import cv2
import time
import threading


def record_video(output_file, duration=10, fps=30.0):
    """
    Record video from the FaceTime camera.

    :param output_file: str, path to save the output video file
    :param duration: int, duration of the recording in seconds (default: 10)
    :param fps: float, frames per second for the output video (default: 30.0)
    """
    # Initialize the video capture
    cap = cv2.VideoCapture(
        0
    )  # 0 is usually the default camera (FaceTime camera on Mac)

    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    # Get the frame width and height
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_file, fourcc, fps, (frame_width, frame_height))

    # Set the end time for recording
    end_time = time.time() + duration

    print(f"Recording video for {duration} seconds...")

    # Start recording
    while time.time() < end_time:
        ret, frame = cap.read()
        if ret:
            # Write the frame to the output file
            out.write(frame)

            # Display the frame (optional)
            cv2.imshow("Recording", frame)

            # Press 'q' to quit early
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        else:
            print("Error: Failed to capture frame.")
            break

    # Release everything when done
    cap.release()
    out.release()
    cv2.destroyAllWindows()

    print(f"Video saved as {output_file}")


# Example usage
if __name__ == "__main__":
    output_file = "facetime_recording.mp4"
    record_video(output_file, duration=10)
