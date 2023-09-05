from datetime import datetime, timedelta
# import sql_functions
import uuid
import cv2

class DetectionList():
    def __init__(self, campaign=0):
        self.detection_information = []
        self.active_ids = []
        self.current_element_idx = None
        self.campaign = campaign

    def get_active_ids(self):
        return self.active_ids

    def get_detection_list(self):
        return self.detection_information

    def update_detection(self, detection_id, bbox):
        self.current_element_idx = int(self.active_ids.index(detection_id))
        self.detection_information[self.current_element_idx].update_bbox_time(bbox)

    def add_new_detection(self, person):
        self.detection_information.append(person)
        self.current_element_idx = int(len(self.detection_information) - 1)
        self.active_ids.append(person.deep_sort_id)

    def save_new_detection(self):
        person_to_output = self.detection_information[self.current_element_idx]
        # deep_sort_id, bbox_top_left_x, bbox_top_left_y, bbox_bottom_right_x,
        # bbox_bottom_right_y, time_of_detection, store_id, classification
        uuid = str(person_to_output.uuid)
        bbox_top_left_x = float(person_to_output.current_bbox_cords[0])
        bbox_top_left_y = float(person_to_output.current_bbox_cords[1])
        bbox_bottom_right_x = float(person_to_output.current_bbox_cords[2])
        bbox_bottom_right_y = float(person_to_output.current_bbox_cords[3])
        detection_time = person_to_output.current_time
        print(f"Pedestrian number {uuid} detected at {detection_time}")
        # sql_functions.insert_all_pedestrian_detections_row((uuid, bbox_top_left_x, bbox_top_left_y,
        #                                                    bbox_bottom_right_x, bbox_bottom_right_y, detection_time))

    def save_pedestrian_overviews(self):
        for person_to_output in enumerate(self.detection_information):
            uuid = str(person_to_output.uuid)
            first_bbox_cords = str(person_to_output.first_bbox_cords)
            last_bbox_cords = str(person_to_output.current_bbox_cords)
            first_detection = person_to_output.first_detection_time
            last_detection = person_to_output.current_time
            elapsed_time = person_to_output.total_time_in_frame
            store_id = int(person_to_output.store_id)
            classification = int(person_to_output.classification)
            print(f'New detection successfully added for {uuid}!')
            # sql_functions.insert_pedestrian_summary_row((uuid, first_bbox_cords, last_bbox_cords,
            #                                             first_detection, last_detection,
            #                                             elapsed_time, store_id, classification,
            #                                             self.campaign))


    def show_pedestrian_stats(self, frame):
        cv2.putText(frame, f"Total Pedestrian Count: {len(self.detection_information)}", (5, 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 0, 255), 1, cv2.LINE_AA)
        return frame

    def print_pedestrian_stats(self):
        return len(self.detection_information)

class person():
    def __init__(self, person_id, classification, bbox_cords, store_id):
        self.deep_sort_id = person_id
        self.classification = classification
        self.first_bbox_cords = bbox_cords
        self.current_bbox_cords = self.first_bbox_cords
        self.first_detection_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.current_time = self.first_detection_time
        datetime_obj1 = datetime.strptime(self.first_detection_time, '%Y-%m-%d %H:%M:%S')
        datetime_obj2 = datetime.strptime(self.current_time, '%Y-%m-%d %H:%M:%S')
        self.total_time_in_frame = datetime_obj2 - datetime_obj1
        print(self.total_time_in_frame)
        self.store_id = store_id
        self.uuid = uuid.uuid4()

    def update_bbox_time(self, bbox_cords):
        self.current_bbox_cords = bbox_cords
        self.current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        datetime_obj1 = datetime.strptime(self.first_detection_time, '%Y-%m-%d %H:%M:%S')
        datetime_obj2 = datetime.strptime(self.current_time, '%Y-%m-%d %H:%M:%S')
        self.total_time_in_frame = datetime_obj2 - datetime_obj1



