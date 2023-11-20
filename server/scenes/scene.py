from abc import abstractmethod
import threading
import os


class Scene:
    def __init__(self, **kwargs):
        # call this last in your scene subclass inits. It will
        # handle all the threading and data storage for you.
        # Your prepare and perform methods can pass data through
        # the scene_data dictionary

        # each subclass should use its prepare method to prep
        # an audio thread and image thread. You can join either
        # of those threads in the prepare method to block
        # starting this scene until they're ready, and/or join
        # them in the perform method before you call super().perform()
        # or just leave it alone to do one or both async
        self.orchestrator = kwargs.get('orchestrator', None)
        self.scene_data = {}
        self.audio_thread = None

        self.prepare_thread = threading.Thread(target=self.prepare)
        self.prepare_thread.start()

        pass

    # Speak the sentence. Returns None
    @abstractmethod
    def prepare(self):
        pass

    def play_audio(self):
        try:
            if self.audio_thread:
                self.audio_thread.join()
            if self.scene_data.get('audio', None):
                print("🖼️ playing audio")
                self.orchestrator.handle_audio(self.scene_data['audio'])
        except Exception as e:
            print(f"Exception in play_audio: {e}")

    def perform(self):
        self.prepare_thread.join()
        aud = threading.Thread(target=self.play_audio)
        aud.start()
        aud.join()
