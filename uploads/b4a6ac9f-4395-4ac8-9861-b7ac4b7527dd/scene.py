from manim import *

class TitleScene(Scene):
    def construct(self):
        title = Text("Students should be guided through how to answer any 2 questi")
        self.play(Write(title))
        self.wait(1)
