from manim import *

class Lesson(Scene):
    def construct(self):
        # Segment 1: Introduction to Factoring Polynomials
        title = Text("Factoring Polynomials", font_size=54, color=BLUE)
        self.play(Write(title))
        self.wait(2)

        intro_text = Text("Breaking down complex expressions.", font_size=32).next_to(title, DOWN, buff=0.8)
        self.play(FadeIn(intro_text))
        self.wait(3)

        poly_example = Text("Example: x^2 + 5x + 6", font_size=40).shift(UP*0.5)
        factored_example = Text("Factored: (x+2)(x+3)", font_size=40).shift(DOWN*0.5)
        self.play(FadeOut(title, intro_text), FadeIn(poly_example))
        self.wait(1.5)
        self.play(Transform(poly_example, factored_example))
        self.wait(2)

        # Segment 2: Perfect Squares/Cubes
        self.play(FadeOut(poly_example))

        perfect_sq_title = Text("Perfect Squares and Cubes", font_size=48, color=GREEN)
        self.play(Write(perfect_sq_title))
        self.wait(2)

        sq_formula = Text("(a+b)^2 = a^2 + 2ab + b^2", font_size=36).next_to(perfect_sq_title, DOWN, buff=0.7)
        cube_formula = Text("(a+b)^3 = a^3 + 3a^2b + 3ab^2 + b^3", font_size=36).next_to(sq_formula, DOWN, buff=0.5)

        self.play(FadeIn(sq_formula))
        self.wait(3)
        self.play(FadeIn(cube_formula))
        self.wait(6)

        # Segment 3: Synthetic Division
        self.play(FadeOut(perfect_sq_title, sq_formula, cube_formula))

        synth_div_title = Text("Synthetic Division", font_size=48, color=ORANGE)
        self.play(Write(synth_div_title))
        self.wait(2)

        div_problem = Text("Divide: (x^3 - 6x^2 + 11x - 6) / (x-1)", font_size=32).next_to(synth_div_title, DOWN, buff=0.7)
        self.play(FadeIn(div_problem))
        self.wait(2)

        div_setup = Text("1 | 1  -6  11  -6", font_size=36).next_to(div_problem, DOWN, buff=0.5)
        div_result = Text("Result: 1x^2 - 5x + 6, Remainder: 0", font_size=32).next_to(div_setup, DOWN, buff=0.5)

        self.play(FadeIn(div_setup))
        self.wait(3)
        self.play(FadeIn(div_result))
        self.wait(4)

        # Segment 4: Conclusion
        self.play(FadeOut(synth_div_title, div_problem, div_setup, div_result))

        conclusion_text = Text("Powerful tools for polynomial analysis!", font_size=36, color=WHITE)
        self.play(Write(conclusion_text))
        self.wait(4)
        self.play(FadeOut(conclusion_text))
        self.wait(2)
