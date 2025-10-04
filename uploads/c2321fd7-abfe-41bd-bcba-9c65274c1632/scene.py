from manim import *

class TitleScene(Scene):
    def construct(self):
        title = Text("Vynavin Vinod Address: Brampton, ON| Email: vin")
        self.play(Write(title))
        self.wait(1)
