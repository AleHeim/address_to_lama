import requests
import json
from translate import Translator
from multiprocessing import Process, Queue
import cv2
from ultralytics import YOLO

#headers = {
#    'Content-Type': 'application/json',
#	'charset': 'utf-8'
#}

def process_prompt(prompt):
    print(prompt)
    data = '{   "model": "llama3.2",   "prompt":"' + f'{prompt}' + '"  }'
    responses = []

    # Формат ('протокол://ip:port/путь', data=json данные) 
    response = requests.post('http://172.17.0.3:11434/api/generate', data=data )

    print(f'response STATUS CODE {response.status_code}')

    # Обработка ответа
    for line in response.iter_lines():
        response_json = json.loads(line)
        try:
            responses.append(response_json["response"])
        except:
            pass
            
    output = ''

    for word in responses:
        output += word

    # Перевод и вывод
    #translator = Translator(from_lang="en", to_lang="ru")
    #output = translator.translate(output)
    print(output)

#initial_prompt = 'I will send you coordinates in the format (x, y), where the minimum value is 0 and the maximum is 1. You need to determine where the object is, on the left (x<0.4), on the right (x>0.6) or in the middle (0.4<x <0.6)'
def prompt_to_lama(queue):
    prompt = 'Imagine that you comment battle of car robots, I will send you where robots are and you should comment it'
    process_prompt(prompt)
    while True:
        if not queue.empty():
            prompt = queue.get()
            process_prompt(prompt)


def cam_track(queue, device_id):
    model = YOLO('weights/best.pt')
    cap = cv2.VideoCapture(device_id)
    if not cap.isOpened():
        print(f"Failed to open device {device_id}")
        return
    while cap.isOpened():
        # robot_ids = { 1: [], 2: []}
        ret, frame = cap.read()
        if not ret:
            break
        results = model.predict(frame, verbose=False)
        for r in results:
            if len(r.boxes)>0:
                prompt = []
                for i, box in enumerate(r.boxes):
                    x, y = box.xywhn[0][0], box.xywhn[0][1]
                    if(x<0.4):
                        loc = 'left'
                    elif(x>0.6):
                        loc = 'right'
                    else:
                        loc = 'middle'

                    prompt.append(f'Robot: {i}; located: {loc}')
                    #print(prompt)
                    queue.put(prompt)

def main(cam):
    queue = Queue()
    process1 = Process(target=cam_track, args=(queue, cam))
    process2 = Process(target=prompt_to_lama, args=(queue,))

    process1.start()
    process2.start()

    process1.join()
    process2.join()

cam = 'http://192.168.1.43:8081' # ТУТ ПОСТАВИТЬ адрес до камеры

#prompt_to_lama(initial_prompt)
if __name__ == "__main__":
    main(cam)


