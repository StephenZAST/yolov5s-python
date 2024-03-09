import torch
import numpy as np
import cv2
import time
from PIL import Image
import requests
from io import BytesIO
import os

class ObjectDetection:
    # init : Cette méthode initialise le modèle YOLOv5 et détermine si le GPU est disponible pour l’exécution du modèle.
    def __init__(self):
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        self.classes = self.model.names
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # score_frame : Cette méthode prend une image en entrée, la passe au modèle et renvoie les labels et les coordonnées des objets détectés.
    def score_frame(self, frame):
        self.model.to(self.device)
        frame = [frame]
        results = self.model(frame)
        labels, cord = results.xyxyn[0][:, -1], results.xyxyn[0][:, :-1]
        return labels, cord

    # class_to_label : Cette méthode convertit les indices de classe en labels de classe.
    def class_to_label(self, x):
        return self.classes[int(x)]

    # plot_boxes : Cette méthode dessine des rectangles autour des objets détectés dans l’image et ajoute des labels de classe à ces rectangles.
    def plot_boxes(self, results, frame):
        labels, cord = results
        n = len(labels)
        x_shape, y_shape = frame.shape[1], frame.shape[0]
        for i in range(n):
            row = cord[i]
            if row[4] >= 0.2:
                x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(row[2]*x_shape), int(row[3]*y_shape)
                bgr = (0, 255, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), bgr, 2)
                cv2.putText(frame, self.class_to_label(labels[i]), (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.9, bgr, 2)
        return frame

    # process_input : Cette méthode détermine si l’entrée est une URL ou un chemin local, et si elle pointe vers une image ou une vidéo. En fonction de cela, elle appelle la méthode appropriée pour traiter l’entrée.
    def process_input(self, input):
        if input.startswith('http'):
            # Si c'est une URL
            if input.lower().endswith(('.png', '.jpg', '.jpeg')):
                # Si c'est une image
                return self.detect_image_from_url(input)
            else:
                # Si c'est une vidéo
                return self.detect_streaming_video(input)
        else:
            # Si c'est un chemin local
            if input.lower().endswith(('.png', '.jpg', '.jpeg')):
                # Si c'est une image
                img = Image.open(input)
                return self.detect_image(img)
            else:
                # Si c'est une vidéo
                return self.detect_video(input)

    # process_folder : Cette méthode analyse tous les fichiers d’un dossier donné. Si le fichier est une image, elle l’analyse.
    def process_folder(self, folder_path):
        # Vérifier si le chemin est un dossier
        if os.path.isdir(folder_path):
            # Parcourir tous les fichiers dans le dossier
            for filename in os.listdir(folder_path):
                # Construire le chemin complet du fichier
                file_path = os.path.join(folder_path, filename)
                # Vérifier si le fichier est une image
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                    # Si c'est une image, l'analyser
                    img = Image.open(file_path)
                    self.detect_image(img)
        else:
            print(f"{folder_path} n'est pas un dossier valide.")

    # detect_image : Cette méthode prend une image en entrée, la passe au modèle pour la détection d’objets, affiche les résultats et renvoie les coordonnées des boîtes englobantes des objets détectés.
    def detect_image(self, img):
        # détection
        results = self.model(img)

        # Affichage des résultats
        results.print()
        results.show()

        # Retourner les résultats
        return results.xyxy[0]  # xyxy est un attribut de results qui contient les coordonnées des boîtes englobantes

    # detect_image_from_url : Cette méthode tente de charger une image à partir d’une URL donnée et de la passer au modèle pour la détection d’objets.
    def detect_image_from_url(self, image_url):
        try:
            # Essayer de charger l'image depuis l'URL
            response = requests.get(image_url)
            img = Image.open(BytesIO(response.content))
            return self.detect_image(img)
        except Exception as e:
            print(f"Erreur lors du chargement de l'image depuis l'URL {image_url}: {e}")

    def detect_video(self, video_path):
        try:
            # Essayer de charger la vidéo
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"Impossible d'ouvrir la vidéo à partir du chemin {video_path}")
                return

            while(cap.isOpened()):
                ret, frame = cap.read()
                if not ret:
                    break

                # Convertir l'image en PIL Image
                img = Image.fromarray(frame)

                self.detect_image(img)

            cap.release()
            cv2.destroyAllWindows()
        except Exception as e:
            print(f"Erreur lors du chargement de la vidéo depuis le chemin {video_path}: {e}")

    def detect_streaming_video(self, video_url):
        try:
            # Essayer de charger la vidéo en streaming
            cap = cv2.VideoCapture(video_url)
            if not cap.isOpened():
                print(f"Impossible d'ouvrir la vidéo en streaming à partir de l'URL {video_url}")
                return

            while(cap.isOpened()):
                ret, frame = cap.read()
                if not ret:
                    break

                # Convertir l'image en PIL Image
                img = Image.fromarray(frame)

                self.detect_image(img)

            cap.release()
            cv2.destroyAllWindows()
        except Exception as e:
            print(f"Erreur lors du chargement de la vidéo en streaming depuis l'URL {video_url}: {e}")

    def __call__(self, video_path):
        cap = cv2.VideoCapture(video_path)
        cv2.namedWindow("Output", cv2.WINDOW_NORMAL)

        while cap.isOpened():
            start_time = time.perf_counter()
            ret, frame = cap.read()
            if not ret:
                break
            results = self.score_frame(frame)
            frame = self.plot_boxes(results, frame)
            end_time = time.perf_counter()
            fps = 1 / np.round(end_time - start_time, 3)
            cv2.putText(frame, f'FPS: {int(fps)}', (20,70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2)
            cv2.imshow("Output", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
    
    def detect_webcam(self):
        try:
            # Essayer de charger la vidéo de la webcam
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("Impossible d'ouvrir la webcam")
                return

            cv2.namedWindow("Output", cv2.WINDOW_NORMAL)

            while cap.isOpened():
                start_time = time.perf_counter()
                ret, frame = cap.read()
                if not ret:
                    break

                results = self.score_frame(frame)
                frame = self.plot_boxes(results, frame)
                end_time = time.perf_counter()
                fps = 1 / np.round(end_time - start_time, 3)
                cv2.putText(frame, f'FPS: {int(fps)}', (70,70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 255), 2)
                cv2.imshow("Output", frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()
        except Exception as e:
            print(f"Erreur lors de l'utilisation de la webcam: {e}")




# quelque command manuel

# --------------------------------------------------------------------------------------
# detection = ObjectDetection()
# detection.process_input('C:\\Users\\HP OMEN\\Downloads\\yollo\\fruit.jpg')  image local
# ---------------------------------------------------------------------------------------
# detection = ObjectDetection()
# detection.detect_streaming_video('http://example.com/video.mp4')  detection par url video

# ---------------------------------------------------------------------------------------
# detection = ObjectDetection()
# detection.detect_image_from_url('http://example.com/image.jpg')  detection par url image

# ---------------------------------------------------------------------------------------
# detection = ObjectDetection()
# detection('C:\\chemin\\vers\\votre\\video.mp4')   detection par video local

# ---------------------------------------------------------------------------------------
# detection = ObjectDetection()
# detection.process_folder('C:\\chemin\\vers\\votre\\dossier')   detection apartir de dossier
# ------------------------------------------------------------------------------------------
# detection = ObjectDetection()
# detection('C:\\chemin\\vers\\votre\\video.mp4')
# detection.process_folder('C:\\chemin\\vers\\votre\\dossier')   exemple de multi detection successif



