from manim import *

class GraphingPolynomialsVideo(Scene):
    def construct(self):
        # --- Scene 1: Title and Introduction ---
        title = Text('Graphing Polynomials', font_size=56, color=BLUE)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        intro_text = Text(
            'Understanding the Shapes of Functions',
            font_size=32, color=WHITE
        )
        intro_text.next_to(title, DOWN, buff=0.5)
        self.play(FadeIn(intro_text, shift=UP))
        self.wait(1.5)

        self.play(FadeOut(intro_text, shift=DOWN))
        self.wait(0.5)

        # --- Scene 2: Setting up Axes and First Graph (Quadratic) ---
        axes = Axes(
            x_range=[-3.5, 3.5, 1],
            y_range=[-8, 8, 2],
            x_length=7,
            y_length=6,
            axis_config={'color': WHITE, 'include_tip': True}
        )
        axes.scale(0.8).shift(DOWN*0.5)
        axes_labels = axes.get_axis_labels(x_label='x', y_label='y')

        quadratic_eq_text = MathTex('f(x) = x^2', font_size=40, color=YELLOW)
        quadratic_eq_text.to_edge(UP).shift(DOWN*0.8)

        graph_quadratic = axes.plot(lambda x: x**2, color=YELLOW, x_range=[-2.5, 2.5])

        self.play(Create(axes), Write(axes_labels), run_time=2)
        self.play(Write(quadratic_eq_text))
        self.play(Create(graph_quadratic), run_time=2)
        self.wait(2.5)

        # --- Scene 3: Morph to Cubic Function ---
        cubic_eq_text = MathTex('f(x) = x^3 - 2x', font_size=40, color=GREEN)
        cubic_eq_text.to_edge(UP).shift(DOWN*0.8)

        graph_cubic = axes.plot(lambda x: x**3 - 2*x, color=GREEN, x_range=[-2.2, 2.2])

        self.play(Transform(quadratic_eq_text, cubic_eq_text))
        self.play(Transform(graph_quadratic, graph_cubic), run_time=2.5)
        self.wait(2.5)

        # --- Scene 4: Morph to Quartic Function ---
        quartic_eq_text = MathTex('f(x) = x^4 - 3x^2', font_size=40, color=RED)
        quartic_eq_text.to_edge(UP).shift(DOWN*0.8)

        graph_quartic = axes.plot(lambda x: x**4 - 3*x**2, color=RED, x_range=[-2.2, 2.2])

        self.play(Transform(quadratic_eq_text, quartic_eq_text))
        self.play(Transform(graph_quadratic, graph_quartic), run_time=2.5)
        self.wait(3)

        # --- Scene 5: Summary and Conclusion ---
        self.play(
            FadeOut(graph_quadratic),
            FadeOut(quadratic_eq_text),
            FadeOut(axes_labels),
            FadeOut(axes),
            run_time=1.5
        )

        summary_text = Text(
            'The degree of a polynomial\ndetermines its fundamental shape!',
            font_size=38, color=YELLOW
        )
        summary_text.next_to(title, DOWN, buff=1)
        self.play(Write(summary_text))
        self.wait(3.5)

        self.play(
            FadeOut(summary_text),
            FadeOut(title),
            run_time=1.5
        )