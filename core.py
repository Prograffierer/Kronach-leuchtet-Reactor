import logging
import random
import time
from abc import ABC

MISTAKE = 0
CORRECT = 1
COMPLETED = 2
INVALID = -1

CELL_ALL_RIGHT = 9
CELL_MISTAKE = 10


class Game:
    def __init__(self) -> None:
        self.reset()
        self.high_score = 0
        self.color_code = RainbowTheme
    
    def reset(self):
        self.presenter = Presenter()
        self.reactor = Reactor(self.presenter, mistake_callback=self.mistake)
        self.presenter.new_series()

    def mistake(self):
        if self.presenter.series_len() - 1 > self.high_score:
            # -1 is because the last cell was wrong
            self.high_score = self.presenter.series_len() - 1
        self.reset()

    def colors(self):
        """
        Returning presenter_colors, reactor_colors
        """
        return self.color_code.convert(self.presenter.get_current_cell()), self.color_code.convert(self.reactor.get_current_cell())


class Presenter:
    """
    Ich würde vorschlagen, ein Objekt pro Spiel zu erstellen. Sobald ein Fehler gemacht wird, ist der dann auch wieder fertig. Gleiches gilt für die andere Klasse
    """

    def __init__(self, interval=.5, wait=.5) -> None:
        """
        @interval: Wie lange soll gewartet werden, bis das nächste Feld aufleuchtet (in einer Reihe von Feldern)?
        @wait: Wie lange soll nach dem Ende des letzten richtig angeglickten Felds der letzten Reihe mit der nächsten gewartet werden?
        """
        self.interval = interval
        self.wait = wait
        self.series = []
        self.clicked_cells = 0
        self.series_start = time.perf_counter()

    def check(self, new_cell):
        try:
            correct = self.series[self.clicked_cells] == new_cell
        except IndexError:
            logging.warning(f"Checking cell {new_cell} even after {self.clicked_cells} clicks and a series of {self.series}. Returning INVALID")
            return INVALID
        self.clicked_cells += 1
        if correct:
            if self.clicked_cells == len(self.series):
                print("Completed")
                return COMPLETED
            else:
                print("Correct")
                return CORRECT
        else:
            print("Mistake")
            return MISTAKE
        
    def new_series(self, wait=True):
        self.series_start = time.perf_counter() + self.wait * wait
        self.clicked_cells = 0
        new_cell = random.randint(0, 8)
        while len(self.series) > 0 and self.series[-1] == new_cell:
            new_cell = random.randint(0, 8)
        self.series.append(new_cell)

    def get_current_cell(self):
        series_time = time.perf_counter() - self.series_start
        if series_time < 0:
            return -1
        try:
            return self.series[int(series_time/self.interval)]
        except IndexError:
            return -1
        
    def series_len(self):
        return len(self.series)
        

class Reactor:
    def __init__(self, presenter: Presenter, wait_for_auto=0.3, stay_all_on=0.3, mistake_callback=lambda: None) -> None:
        self.presenter = presenter
        self.active_cell = -1
        self.stay_all_on = stay_all_on
        self.all_on_start = None
        self.mistake_callback = mistake_callback
        self.wait_for_auto = wait_for_auto
        self.next_auto = None
        self.auto_start = None
        
    def click(self, cell):
        if self.active_cell != cell:
            res = self.presenter.check(cell)
            if res:
                if res == INVALID:
                    return None
                if res == CORRECT:
                    self.active_cell = cell
                else:
                    self.active_cell = cell
                    self.next_auto = CELL_ALL_RIGHT
                    self.auto_start = time.perf_counter()
                    self.presenter.new_series()
                    self.all_on_start = time.perf_counter()
            else:
                self.all_on_start = time.perf_counter()
                self.active_cell = CELL_MISTAKE

    def get_current_cell(self):
        if self.next_auto is not None and time.perf_counter() - self.auto_start > self.wait_for_auto:
            self.active_cell = self.next_auto
            self.next_auto = None
            if self.active_cell in {CELL_ALL_RIGHT, CELL_MISTAKE}:
                self.all_on_start = time.perf_counter()
        if self.active_cell in {CELL_ALL_RIGHT, CELL_MISTAKE} and time.perf_counter() - self.all_on_start > self.stay_all_on:
            mistake = self.active_cell == CELL_MISTAKE
            self.active_cell = -1
            if mistake:
                self.mistake_callback()
        return self.active_cell


class ColorCode(ABC):
    colors = []
    all_right = "darkgreen"
    mistake = "red"
    black = "black"

    @classmethod
    def convert(cls, cell):
        if cell == -1:
            return [[cls.black for _ in range(3)] for _ in range(3)]
        elif cell == CELL_ALL_RIGHT:
            return [[cls.all_right for _ in range(3)] for _ in range(3)]
        elif cell == CELL_MISTAKE:
            return [[cls.mistake for _ in range(3)] for _ in range(3)]
        else:
            return [[cls.colors[i][j] if i*3 + j == cell else cls.black for j in range(3)] for i in range(3)]
        

class RainbowTheme(ColorCode):
    colors = [
        ["red", "orange", "yellow"],
        ["lightgreen", "darkgreen", "purple"],
        ["blue", "darkblue", "magenta"]
    ]
