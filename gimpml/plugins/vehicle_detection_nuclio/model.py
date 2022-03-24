import base64

import cv2
import requests

CLASS_COLORS = {
    'person': (6, 150, 104),
    'bicycle': (144, 234, 102),
    'car': (34, 79, 62),
    'motorcycle': (28, 224, 178),
    'bus': (147, 224, 240),
    'train': (49, 89, 185),
    'truck': (213, 208, 250),
}


class VehicleDetection:
    def __init__(self):
        self.url = 'http://localhost:8070/api/function_invocations'
        self.headers = {
            'x-nuclio-function-name': 'vehicle-tracking',
            'x-nuclio-function-namespace': 'nuclio',
        }
        self.data = {
            'first_frame': False,
            'last_frame': False,
        }

    def encode_image(self, im_file):
        with open(im_file, 'rb') as f:
            im_bytes = f.read()
            im_b64 = base64.b64encode(im_bytes).decode('utf8')

        return im_b64

    def postprocess(self, im_file, shapes):
        img = cv2.imread(im_file)

        for shape in shapes:
            if shape['type'] == 'rectangle':
                bbox = shape['points']
                cv2.rectangle(
                    img,
                    (round(bbox[0]), round(bbox[1])),
                    (round(bbox[2]), round(bbox[3])),
                    CLASS_COLORS[shape['label']],
                    thickness=2,
                )
                cv2.putText(
                    img,
                    shape['label'],
                    (round(bbox[0]), round(bbox[1])),
                    cv2.FONT_HERSHEY_PLAIN,
                    fontScale=2,
                    color=CLASS_COLORS[shape['label']],
                    thickness=2,
                )

        return img

    def __call__(self, im_file):
        self.data['image'] = self.encode_image(im_file)
        response = requests.post(
            self.url,
            headers=self.headers,
            json=self.data,
        )
        img = self.postprocess(im_file, response.json())
        return img
