from scenes.scene import Scene
from threading import Thread

class TranslatorScene(Scene):
	def __init__(self, **kwargs):
		print("StoryPageScene init")
		self.message = kwargs.get('message', None)
		self.sentence = self.message['translation']
		
		super().__init__(**kwargs)
		
	def prepare(self):
		print(f"👩‍💼 TranslatorScene prepare sentence: {self.sentence}")
		# don't need threads here because image
		# is effectively instant
		#self.scene_data['image'] = (self.grandma_writing)
		self.scene_data['audio'] = self.orchestrator.request_tts(self.message)
		
		print(f"👩‍💼 TranslatorScene prepare complete for: {self.sentence} in {self.message['translation_language']}")
		
	
	def perform(self):
		print(f"👩‍💼 TranslatorScene perform sentence: {self.sentence} in {self.message['translation_language']}")
		# Send caption when we start speaking the audio
		# and remove the 'response' object because it doesn't serialize nicely
		self.message.pop('response', None)
		self.orchestrator.image_setter.send_app_message(self.message)
		super().perform()