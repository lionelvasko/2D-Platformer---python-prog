class Data:
    def __init__(self, ui):
        self.ui = ui
        self._health = 20
        self.ui.create_hearts(self._health)
        self.unlocked_level = 0
        self.current_level = 0

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, value):
        self._health = value
        self.ui.create_hearts(value)
