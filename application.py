from flask import Flask, Response, render_template
from flask_bootstrap import Bootstrap
import cv2
import base64
import json
import time
from ultralytics import YOLO
from people import person, DetectionList
import config

app = Flask(__name__)
bootstrap = Bootstrap(app)

# Initialize video capture (replace '0' with your video source)
cap = cv2.VideoCapture(0)
model = YOLO('yolov8n.pt')

# set the current campaign
campaign = config.campaign

# instantial detection list
pedestrian_list = DetectionList(campaign=campaign)

# set store id
store_id = config.store_id

# get cutoff line
sidewalk_cutoff = config.sidewalk_cutoff_line

def is_close_to_camera(bbox, cutoff_line):
    lower_bbox_limit = bbox[-1]
    return True if lower_bbox_limit > cutoff_line else False

def draw_bbox(frame, bbox, deep_sort_id):
    annotated_frame = frame.copy()
    top_left_cords = (int(bbox[0]), int(bbox[1]))
    bottom_right_cords = (int(bbox[2]), int(bbox[3]))
    cv2.rectangle(annotated_frame, top_left_cords, bottom_right_cords, (0,0,255), 2)
    cv2.putText(annotated_frame, f"ID Number: {deep_sort_id}", (int(bbox[0]), int(bbox[1])-20), cv2.FONT_HERSHEY_SIMPLEX,
                1, (0,0,255), 2, cv2.LINE_AA)
    return annotated_frame

def generate_messages():
    while True:
        success, frame = cap.read()
        if not success:
            break

        results = model.track(frame, classes=0, persist=True, conf=0.3, iou=0.5)
        annotated_frame = frame.copy()
        people_in_frame = 0
        for result in results:
            for i in range(len(result)):
                try:
                    deep_sort_id = result.boxes.numpy().id[i]
                    classification = result.boxes.numpy().cls[i]
                    confidence_score = result.boxes.numpy().conf[i]
                    bbox_cords = result.boxes.numpy().xyxy[i]
                except:
                    continue

                if is_close_to_camera(bbox_cords, sidewalk_cutoff):
                    people_in_frame += 1
                    annotated_frame = draw_bbox(frame, bbox_cords, deep_sort_id)
                    #print('deep sort id: ', deep_sort_id)
                    #print('bbox_cords: ', bbox_cords)
                    if deep_sort_id in pedestrian_list.get_active_ids():
                        pedestrian_list.update_detection(deep_sort_id, result.boxes.numpy().xyxy[i])
                        pedestrian_list.save_new_detection()
                    else:
                        new_person = person(deep_sort_id, classification, bbox_cords, store_id)
                        pedestrian_list.add_new_detection(new_person)
                        pedestrian_list.save_new_detection()


        # draw cut-off line for 'close' detections (i.e. don't want to track people on opposite sidewalk)
        cv2.line(annotated_frame, (0, sidewalk_cutoff), (640, sidewalk_cutoff), (0, 0, 255), 2)

        # Display the annotated frame
        annotated_frame = pedestrian_list.show_pedestrian_stats(annotated_frame)

        # Convert the frame to base64-encoded string
        _, buffer = cv2.imencode('.jpg', annotated_frame)

        frame_base64 = base64.b64encode(buffer).decode()


        # Create a dictionary with video data and other information
        data = {
            'videoFrame': frame_base64,
            'timestamp': time.time(),
            'inFrameCount': str(people_in_frame),
            'totalCount': str(pedestrian_list.print_pedestrian_stats())
            # Add other data fields as needed
        }

        # Serialize the dictionary to JSON
        json_data = json.dumps(data)

        # Yield the JSON data as an SSE event
        yield f"data: {json_data}\n\n"

@app.route('/sse')
def sse():
    return Response(generate_messages(), content_type='text/event-stream')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)