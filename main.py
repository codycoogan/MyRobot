import speech_recognition as sr
import pygame
from gtts import gTTS
from RPLCD.gpio import CharLCD
from RPi import GPIO
import requests
import openai
import os
import time
# import busio

openai.api_key = os.getenv("OPEN_API_KEY")


class SpeechConverter:
	
	def __init__(self):
		print(sr.Microphone().list_microphone_names())
		pygame.mixer.init()
		self.lcd = CharLCD(cols=16, rows=2, pin_rs=14, pin_e=15, 
		pins_data=[8,7,1,12], numbering_mode=GPIO.BCM)
		# 18,23,24,25, 8,7,1,12
		self.lcd.clear()
		
		self.messages = []
		self.mic_index = self.get_mic_index()
		
		
	#	self.r = sr.Recognizer()
		#self.mic = sr.Microphone(device_index=self.get_mic_index)
	
	def write_to_lcd(self, words):
		if words:
			print(words)
			self.lcd.clear()
		if len(words) > 32:
			iterations = len(words) -16 + 1
			for i in range(iterations):
				self.lcd.clear()
				self.lcd.write_string(words[i:16+i])
				time.sleep(0.25)
		else:
			self.lcd.write_string(words)
			
	def ask_chat(self, query):
		self.messages.append({"role": "user", "content": query})
		response = openai.ChatCompletion.create(
			model="gpt-3.5-turbo",
			messages=self.messages
			)
		
		print(response['choices'][0])
		message = response['choices'][0]["message"]
		self.messages.append(message)
		return message["content"]
	
	def get_mic_index(self):
		return next((i for i, x in enumerate(sr.Microphone().list_microphone_names()) if "USB PnP Sound Device" in x))
		
	def listen_for_command(self):
		r = sr.Recognizer()
		with sr.Microphone(device_index=self.mic_index) as mic:
			
			self.write_to_lcd("Just chillin...  -_-")
			
			r.adjust_for_ambient_noise(mic)
			audio = r.listen(mic)
		try:
			self.write_to_lcd("Recognizing...")
			query = r.recognize_google(audio, language='en-in')
			self.write_to_lcd(f"User said: {query}\n")
			
			if query and query.lower().strip() in ["hey kramer", "yo kramer"]:
				self.take_command()
				
		except Exception as e:
			print(e)
			self.write_to_lcd("Say that again please...")
			return "None"
		return query
		
	def take_command(self):
		r = sr.Recognizer()
		with sr.Microphone(device_index=self.mic_index) as mic:
			
			self.write_to_lcd("what's up??")
			
			r.adjust_for_ambient_noise(mic)
			audio = r.listen(mic)
		try:
			self.write_to_lcd("Recognizing...")
			query = r.recognize_google(audio, language='en-in')
			self.write_to_lcd(f"{query}\n")
			
			if query:
				# GPT it
				resp = self.ask_chat(query)
				
				# play it
				tts = gTTS(resp)
				
				tts.save("audio.mp3")
		
				pygame.mixer.music.load("audio.mp3")
				pygame.mixer.music.play()
				
				self.write_to_lcd(resp)
				while pygame.mixer.music.get_busy():
					continue 
				
		except Exception as e:
			print(e)
			self.write_to_lcd("Say that again please...")
			return "None"
		return query
					
					
sc = SpeechConverter()
#sc.ask_chat("whats weather in portland")
# sc.write_to_lcd("hi my name is cody and im a famous programmer. how are you today? can i get a woof woof")
while True:
	print(sc.listen_for_command())
