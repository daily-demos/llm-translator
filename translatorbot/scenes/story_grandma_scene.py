from scenes.scene import Scene
from threading import Thread

class StoryGrandmaScene(Scene):
	def __init__(self, **kwargs):
		print("StoryPageScene init")
		self.message = kwargs.get('message', None)
		self.sentence = self.message['translation']
		super().__init__(**kwargs)
		
	def prepare(self):
		print(f"👩‍💼 StoryStartScene prepare sentence: {self.sentence}")
		# don't need threads here because image
		# is effectively instant
		#self.scene_data['image'] = (self.grandma_writing)
		self.scene_data['audio'] = self.orchestrator.request_tts(self.sentence)
		print(f"👩‍💼 StoryStartScene prepare complete for: {self.sentence}")
		
	
	def perform(self):
		print(f"👩‍💼 StoryStartScene perform sentence: {self.sentence}")
		# Send caption when we start speaking the audio
		# and remove the 'response' object because it doesn't serialize nicely
		self.message.pop('response', None)
		self.orchestrator.image_setter.send_app_message(self.message)
		super().perform()