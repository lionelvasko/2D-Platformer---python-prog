from level import Level
from pytmx.util_pygame import load_pygame
from support import *
from data import Data
from ui import UI
from overworld import Overworld
import traceback


class Game:
    """
    The main class for the game.

    Attributes:
        ui_frames: A dictionary containing the UI frames.
        bg_music: A pygame.mixer.Sound object for the background music.
        font: A pygame.font.Font object for the game's font.
        audio_files: A dictionary containing the audio files.
        overworld_frames: A dictionary containing the overworld frames.
        level_frames: A dictionary containing the level frames.
        display_surface: A pygame.Surface object for the game's display.
        clock: A pygame.time.Clock object for controlling the game's framerate.
        ui: A UI object for the game's user interface.
        data: A Data object for the game's data.

    Methods:
        import_assets(): Imports the game's assets.
        switch_stage(stage_name): Switches the game's stage.
        run(): Runs the game's main loop.
    """

    def __init__(self):
        """Initialize the game."""
        self.ui_frames = None
        self.bg_music = None
        self.font = None
        self.audio_files = None
        self.overworld_frames = None
        self.level_frames = None
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('2D Platformer - Python Project')
        self.clock = pygame.time.Clock()
        self.import_assets()

        # User interface and data (hp, level, etc.)
        self.ui = UI(self.font, self.ui_frames)
        self.data = Data(self.ui)

        # Loading all the levels
        self.tmx_maps = {
            0: load_pygame(join('..', 'assets', 'levels', '0.tmx')),
            1: load_pygame(join('..', 'assets', 'levels', '1.tmx')),
            2: load_pygame(join('..', 'assets', 'levels', '2.tmx')),
            3: load_pygame(join('..', 'assets', 'levels', '3.tmx')),
            4: load_pygame(join('..', 'assets', 'levels', '4.tmx')),
            5: load_pygame(join('..', 'assets', 'levels', '5.tmx')),
        }
        self.bg_music = pygame.mixer.Sound(join('..', 'audio', 'muzsik.mp3'))
        self.bg_music.set_volume(0.08)
        self.tmx_overworld = load_pygame(join('..', 'assets', 'overworld', 'overworld.tmx'))
        self.current_stage = Overworld(self.tmx_overworld, self.data, self.overworld_frames, self.switch_stage)
        self.bg_music.play(-1)

    def switch_stage(self, target, unlock=0):
        """Switch between levels and overworld."""
        if target == 'level':
            self.current_stage = Level(self.tmx_maps[self.data.current_level], self.level_frames, self.audio_files,
                                       self.data, self.switch_stage)

        else:  # overworld
            if unlock > 0:
                self.data.unlocked_level = unlock
            else:
                self.data.health -= 1
            self.current_stage = Overworld(self.tmx_overworld, self.data, self.overworld_frames, self.switch_stage)

    def import_assets(self):
        """Import sprites and images."""
        self.level_frames = {
            'flag': import_folder('..', 'graphics', 'level', 'flag'),
            'floor_spike': import_folder('..', 'graphics', 'enemies', 'floor_spikes'),
            'palms': import_sub_folders('..', 'graphics', 'level', 'palms'),
            'candle': import_folder('..', 'graphics', 'level', 'candle'),
            'window': import_folder('..', 'graphics', 'level', 'window'),
            'big_chain': import_folder('..', 'graphics', 'level', 'big_chains'),
            'small_chain': import_folder('..', 'graphics', 'level', 'small_chains'),
            'candle_light': import_folder('..', 'graphics', 'level', 'candle light'),
            'player': import_sub_folders('..', 'graphics', 'player'),
            'saw': import_folder('..', 'graphics', 'enemies', 'saw', 'animation'),
            'saw_chain': import_image('..', 'graphics', 'enemies', 'saw', 'saw_chain'),
            'helicopter': import_folder('..', 'graphics', 'level', 'helicopter'),
            'boat': import_folder('..', 'graphics', 'objects', 'boat'),
            'spike': import_image('..', 'graphics', 'enemies', 'spike_ball', 'Spiked Ball'),
            'spike_chain': import_image('..', 'graphics', 'enemies', 'spike_ball', 'spiked_chain'),
            'tooth': import_folder('..', 'graphics', 'enemies', 'tooth', 'run'),
            'canon': import_sub_folders('..', 'graphics', 'enemies', 'canon'),
            'pearl': import_image('..', 'graphics', 'enemies', 'bullets', 'pearl'),
            'particle': import_folder('..', 'graphics', 'effects', 'particle'),
            'water_top': import_folder('..', 'graphics', 'level', 'water', 'top'),
            'water_body': import_image('..', 'graphics', 'level', 'water', 'body'),
            'bg_tiles': import_folder_dict('..', 'graphics', 'level', 'bg', 'tiles'),
            'cloud_small': import_folder('..', 'graphics', 'level', 'clouds', 'small'),
            'cloud_large': import_image('..', 'graphics', 'level', 'clouds', 'large_cloud'),
        }
        self.font = pygame.font.Font(join('..', 'graphics', 'ui', 'runescape_uf.ttf'), 40)
        self.ui_frames = {
            'heart': import_folder('..', 'graphics', 'ui', 'heart'),
        }
        self.overworld_frames = {
            'palms': import_folder('..', 'graphics', 'overworld', 'palm'),
            'water': import_folder('..', 'graphics', 'overworld', 'water'),
            'path': import_folder_dict('..', 'graphics', 'overworld', 'path'),
            'icon': import_sub_folders('..', 'graphics', 'overworld', 'icon'),
        }

        self.audio_files = {
            'jump': pygame.mixer.Sound(join('..', 'audio', 'jump.wav')),
            'damage': pygame.mixer.Sound(join('..', 'audio', 'damage.wav')),
            'pearl': pygame.mixer.Sound(join('..', 'audio', 'pearl.wav')),
        }

    def check_game_over(self):
        """Check if the player is dead."""
        if self.data.health <= 0:
            self.data.health = 20
            self.data.coins = 0
            self.data.unlocked_level = 0
            self.data.current_level = 0
            self.switch_stage('overworld')

    def run(self):
        """Main game loop."""
        while True:
            dt = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.check_game_over()
            self.current_stage.run(dt)
            self.ui.update(dt)

            pygame.display.update()


if __name__ == '__main__':
    try:
        game = Game()
        game.run()
    except Exception as e:
        with open('error_log.txt', 'w') as file:
            file.write(str(e))
            file.write(traceback.format_exc())
        print("An error occurred. Please open 'error_log.txt' for more details.")
