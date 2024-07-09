import os
import tempfile
from flask import Flask, request, jsonify
import cv2
import torch
from ultralytics import YOLO

app = Flask(__name__)

# Load your trained model
model = YOLO('/home/mahedi/projects/personal project/new_technology/Football_player detection/best.pt')

@app.route('/detect', methods=['POST'])
def detect_objects():
    # Get the input video file from the request
    input_video = request.files.get('video')
    if not input_video:
        return jsonify({'error': 'No video file provided'}), 400

    # Create a temporary directory to store the processed video
    with tempfile.TemporaryDirectory() as temp_dir:
        input_video_path = os.path.join(temp_dir, 'input_video.mp4')
        output_video_path = os.path.join(temp_dir, 'video_with_detections.mp4')

        # Save the input video to the temporary directory
        input_video.save(input_video_path)

        # Open the video file
        cap = cv2.VideoCapture(input_video_path)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = None

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Perform object detection
            results = model(frame)

            # Extract bounding boxes and labels
            for result in results[0].boxes:
                x1, y1, x2, y2 = result.xyxy[0].tolist()
                conf = result.conf[0].item()
                cls = result.cls[0].item()
                label = f"{model.names[int(cls)]} {conf:.2f}"
                color = (0, 255, 0)

                # Draw bounding box
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)

                # Draw label
                cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

            # Initialize the video writer with the same frame size and FPS as input video
            if out is None:
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

            # Write the frame with detections to the output video
            out.write(frame)

        cap.release()
        out.release()

        # Return the processed video file
        return_data = {
            'message': 'Processed video',
            'video_path': output_video_path
        }
        return jsonify(return_data), 200

if __name__ == '__main__':
    app.run(debug=True)