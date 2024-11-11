import pygame as pg
import core

# presenter = core.Presenter()
# reactor = core.Reactor(presenter)

class GameGUI:
    def __init__(self, game: core.Game, fps=60, cell_size=50, pres=(100, 50), react=(100, 300)) -> None:
        pg.init()
        pg.display.set_caption("Kronach leuchtet - Reactor")
        self.game = game
        self.screen = pg.display.set_mode((1280, 720))
        self.clock = pg.time.Clock()
        self.running = False
        self.dt = 0
        self.fps = fps
        self.cell_size = cell_size
        self.pres = pres
        self.react = react
        self.font = pg.font.Font("digital-7.ttf", 100)
        
    def event_handler(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                i = int((event.pos[0] - self.react[0])/self.cell_size)
                j = int((event.pos[1] - self.react[1])/self.cell_size)
                if 0 <= i < 3 and 0 <= i < 3:
                    self.game.reactor.click(i * 3 + j)

    def update(self):
        self.screen.fill("gray")
        pres_colors, react_colors = self.game.colors()
        for i in range(3):
            for j in range(3):
                pg.draw.rect(self.screen, pres_colors[i][j], pg.Rect(self.pres[0]+i*self.cell_size, self.pres[1]+j*self.cell_size, self.cell_size, self.cell_size))
                pg.draw.rect(self.screen, react_colors[i][j], pg.Rect(self.react[0]+i*self.cell_size, self.react[1]+j*self.cell_size, self.cell_size, self.cell_size))
        text = self.font.render(str(self.game.high_score), True, "black", "gray")
        textRect = text.get_rect()
        textRect.center = (300, 300)
        self.screen.blit(text, textRect)
        pg.display.flip()

    @property
    def running(self):
        return self._running
    
    @running.setter
    def running(self, value: bool):
        self._running = value
        if value:
            self._keep_running()

    def _keep_running(self):
        while self.running:
            self.event_handler()
            self.update()
            self.dt = self.clock.tick(self.fps) / 1000

    def __enter__(self):
        return self
    
    def __exit__(self):
        self.close()

    def close(self):
        pg.quit()


game = core.Game()
gui = GameGUI(game)
gui.running = True