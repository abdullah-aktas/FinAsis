# VRManager: FinQuest için VR modunun temel mantığı
class VRManager:
    def __init__(self):
        self.enabled = False

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def status(self):
        return "VR Açık" if self.enabled else "VR Kapalı"
