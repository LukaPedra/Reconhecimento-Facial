import face_recognition
import cv2
import os, sys
import numpy as np
import math
from threading import Thread
from serial import Serial
from time import sleep
from datetime import datetime






def face_confidence(face_distance, face_match_threshold=0.75):
	range = (1.0 - face_match_threshold)
	linear_val = (1.0 - face_distance) / (range * 2.0)
	if face_distance > face_match_threshold:
		return str(round(linear_val * 100, 2)) + "%"
	else:
		value = (linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))) * 100
		return str(round(value, 2)) + "%"

  
class FaceRecognition:
	nome = ""
	achou = None
	buscaCara = False
	face_locations = []
	face_encodings = []
	face_names = []
	known_face_encodings = []
	inicio = None
	known_face_names = []
	process_current_frame = True
	recognition_counter = 0
	recognition_threshold = 30  # Adjust this value based on your frame rate and the desired time delay

	
	def __init__(self):
		self.encode_faces()
		
	def encode_faces(self):
		for file in os.listdir("faces"):
			if file[0] == '.':
				continue
			print(f'Encoding {file}')
			face_image = face_recognition.load_image_file(f'faces/{file}')
			face_encoding = face_recognition.face_encodings(face_image)[0]
			self.known_face_names.append(file)
			self.known_face_encodings.append(face_encoding)
		print(self.known_face_names) 
	def get_achou(self):
		return self.achou
	def find_face(self,nome):
		self.nome = nome
		self.buscaCara = True
		self.achou = None
		self.inicio = datetime.now()
	def run_recognition(self):
		videocapture = cv2.VideoCapture(1)
		if not videocapture.isOpened():
			sys.exit('Video source not found')
		while True:
			ret, frame = videocapture.read()
			if self.buscaCara == True:
				
				if self.process_current_frame:
					small_frame = cv2.resize(frame,(0,0),fx=0.25,fy=0.25)
					rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
					
					#ache todas as caras no frame
					self.face_locations = face_recognition.face_locations(rgb_small_frame)
					self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)
					self.face_names = []
					for face_encoding in self.face_encodings:
						matches = face_recognition.compare_faces(self.known_face_encodings,face_encoding)
						name = 'Unknown'
						confidence = 'Unknown'
						
						face_distances = face_recognition.face_distance(self.known_face_encodings,face_encoding)
						best_match_index = np.argmin(face_distances)
						
						if matches[best_match_index]:
							name = self.known_face_names[best_match_index]
							confidence = face_confidence(face_distances[best_match_index])
							self.recognition_counter += 1
							if self.recognition_counter >= self.recognition_threshold:
								if name == self.nome:
            
									self.achou = True
									self.buscaCara = False
								self.buscaCara = False
								self.recognition_counter = 0
								
						else:
							self.recognition_counter += 1
							if self.recognition_counter >= self.recognition_threshold:
								self.recognition_counter = 0
						self.face_names.append(f'{name}({confidence})')
						
				self.process_current_frame = not self.process_current_frame
				for (top,right, bottom, left), name in zip(self.face_locations,self.face_names):
					top *= 4
					right *= 4
					bottom *= 4
					left *= 4
					
					cv2.rectangle(frame,(left,top),(right,bottom), (0,0,255),2)
					cv2.rectangle(frame,(left,bottom - 35),(right,bottom), (0,0,255),-1)
					cv2.putText(frame,name,(left + 6, bottom - 6),cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,255,255),1)
				aux = datetime.now() - self.inicio
				if aux.total_seconds() > 10:
					self.buscaCara = False
					self.achou = False

			cv2.imshow('Face recognition',frame)
			if cv2.waitKey(1) == ord('q'):
				break
		videocapture.release()
		cv2.destroyAllWindows()


