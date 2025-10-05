from manim import *

class PolynomialLesson(Scene):
    def construct(self):
        # 1. Title
        title = Text('Graphing Polynomials', font_size=56, color=BLUE).to_edge(UP)
        self.play(Write(title), run_time=1.5)
        self.wait(1.5)

        # 2. Intro Text
        intro_text = Text('What are polynomials?', font_size=36, color=YELLOW)
        intro_text.shift(UP*1.5)
        self.play(FadeIn(intro_text), run_time=1.5)
        self.wait(2)

        # 3. Example 1 (Linear)
        eq_linear = Text('f(x) = x + 1', font_size=40, color=GREEN)
        self.play(Transform(intro_text, eq_linear), run_time=2)
        self.wait(1.5)
        desc_linear = Text('A straight line!', font_size=36, color=GREEN)
        self.play(Transform(intro_text, desc_linear), run_time=1.5)
        self.wait(1.5)

        # 4. Example 2 (Quadratic)
        eq_quadratic = Text('f(x) = x^2 - 4', font_size=40, color=RED)
        self.play(Transform(intro_text, eq_quadratic), run_time=2)
        self.wait(1.5)
        desc_quadratic = Text('A parabola!', font_size=36, color=RED)
        self.play(Transform(intro_text, desc_quadratic), run_time=1.5)
        self.wait(1.5)

        # 5. Example 3 (Cubic)
        eq_cubic = Text('f(x) = x^3 - x', font_size=40, color=YELLOW)
        self.play(Transform(intro_text, eq_cubic), run_time=2)
        self.wait(1.5)
        desc_cubic = Text('More turns and bends!', font_size=36, color=YELLOW)
        self.play(Transform(intro_text, desc_cubic), run_time=1.5)
        self.wait(1.5)

        # Fade out current text
        self.play(FadeOut(intro_text), run_time=1.5)
        self.wait(1)

        # 6. Summary/Conclusion
        summary_text = Text('Degree determines shape!', font_size=42, color=BLUE).shift(DOWN*0.5)
        self.play(Write(summary_text), run_time=2)
        self.wait(2)
        final_fade = Text('Keep exploring math!', font_size=32, color=GREEN).shift(DOWN*2)
        self.play(FadeIn(final_fade), run_time=1.5)
        self.wait(1)
        self.play(FadeOut(summary_text), FadeOut(final_fade), FadeOut(title), run_time=2)
        self.wait(0.5)