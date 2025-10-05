from manim import *

class IonicCovalentBonds(Scene):
    def construct(self):
        # 1. Title and Intro
        title = Text('Ionic vs. Covalent Bonds', font_size=56, color=BLUE).to_edge(UP)
        self.play(Write(title), run_time=1.5)
        self.wait(1)

        intro_text = Text('Atoms form bonds to achieve stability.', font_size=36, color=YELLOW).shift(UP*0.5)
        self.play(FadeIn(intro_text), run_time=2)
        self.wait(2)

        # 2. Ionic Bonds: Electron Transfer
        self.play(FadeOut(intro_text, shift=DOWN))
        ionic_title = Text('1. Ionic Bonds: Electron Transfer', font_size=44, color=RED).to_edge(UP).shift(DOWN*0.5)
        self.play(Transform(title, ionic_title), run_time=1.5)

        # Sodium atom (donor)
        na_atom = Circle(radius=0.8, color=BLUE, fill_opacity=0.3).shift(LEFT*3)
        na_label = Text('Na', font_size=40, color=BLUE).move_to(na_atom)
        na_electron = Dot(radius=0.15, color=YELLOW).move_to(na_atom.get_right() + RIGHT*0.8) # Valence electron

        # Chlorine atom (acceptor)
        cl_atom = Circle(radius=0.8, color=GREEN, fill_opacity=0.3).shift(RIGHT*3)
        cl_label = Text('Cl', font_size=40, color=GREEN).move_to(cl_atom)
        
        # Display atoms and electron
        self.play(Create(na_atom), Write(na_label), Create(cl_atom), Write(cl_label), FadeIn(na_electron))
        self.wait(1.5)

        # Electron transfer animation
        arrow = Arrow(start=na_electron.get_center(), end=cl_atom.get_left(), color=RED)
        transfer_text = Text('Electron Transfer', font_size=30, color=RED).next_to(arrow, DOWN)
        self.play(MoveAlongPath(na_electron, ArcBetweenPoints(na_electron.get_center(), cl_atom.get_center())), Create(arrow), Write(transfer_text), run_time=2)
        self.remove(na_electron) # Remove the moving electron dot
        self.wait(0.5)

        # Form ions
        na_ion_label = Text('Na+', font_size=40, color=BLUE).move_to(na_atom)
        cl_ion_label = Text('Cl-', font_size=40, color=GREEN).move_to(cl_atom)
        
        self.play(Transform(na_label, na_ion_label), Transform(cl_label, cl_ion_label), FadeOut(arrow), FadeOut(transfer_text))
        self.wait(1)

        # Electrostatic attraction
        attraction_line = DashedLine(na_atom.get_right(), cl_atom.get_left(), color=RED)
        attraction_text = Text('Electrostatic Attraction', font_size=30, color=RED).next_to(attraction_line, DOWN)
        self.play(Create(attraction_line), Write(attraction_text))
        self.wait(2)
        
        # Cleanup ionic scene
        self.play(FadeOut(na_atom, na_label, cl_atom, cl_label, attraction_line, attraction_text))
        self.wait(0.5)

        # 3. Covalent Bonds: Electron Sharing
        covalent_title = Text('2. Covalent Bonds: Electron Sharing', font_size=44, color=GREEN).to_edge(UP).shift(DOWN*0.5)
        self.play(Transform(title, covalent_title), run_time=1.5)

        # Hydrogen atoms
        h1_atom = Circle(radius=0.8, color=YELLOW, fill_opacity=0.3).shift(LEFT*2)
        h1_label = Text('H', font_size=40, color=YELLOW).move_to(h1_atom)
        h2_atom = Circle(radius=0.8, color=YELLOW, fill_opacity=0.3).shift(RIGHT*2)
        h2_label = Text('H', font_size=40, color=YELLOW).move_to(h2_atom)

        h1_electron = Dot(radius=0.15, color=RED).move_to(h1_atom.get_right() + LEFT*0.2)
        h2_electron = Dot(radius=0.15, color=RED).move_to(h2_atom.get_left() + RIGHT*0.2)

        self.play(Create(h1_atom), Write(h1_label), Create(h2_atom), Write(h2_label), FadeIn(h1_electron), FadeIn(h2_electron))
        self.wait(1.5)

        # Electron sharing animation
        shared_electron1_target = h1_atom.get_right() + RIGHT*0.2
        shared_electron2_target = h2_atom.get_left() + LEFT*0.2
        
        self.play(h1_electron.animate.move_to(shared_electron1_target),
                  h2_electron.animate.move_to(shared_electron2_target), run_time=1.5)
        
        # Overlap atoms to show sharing region
        h1_atom_overlap = Circle(radius=0.8, color=YELLOW, fill_opacity=0.3).shift(LEFT*1.5)
        h2_atom_overlap = Circle(radius=0.8, color=YELLOW, fill_opacity=0.3).shift(RIGHT*1.5)
        
        self.play(Transform(h1_atom, h1_atom_overlap), Transform(h2_atom, h2_atom_overlap),
                  h1_label.animate.move_to(h1_atom_overlap), h2_label.animate.move_to(h2_atom_overlap), run_time=1.5)
        
        shared_electrons_group = VGroup(h1_electron, h2_electron).move_to(h1_atom.get_right() + RIGHT*0.5)
        
        sharing_text = Text('Shared Electrons', font_size=30, color=RED).next_to(shared_electrons_group, DOWN)
        self.play(FadeIn(sharing_text))
        self.wait(2)

        # Cleanup covalent scene
        self.play(FadeOut(h1_atom, h1_label, h2_atom, h2_label, shared_electrons_group, sharing_text))
        self.wait(0.5)

        # 4. Summary and Conclusion
        summary_title = Text('Summary: Transfer vs. Sharing', font_size=48, color=BLUE).to_edge(UP).shift(DOWN*0.5)
        self.play(Transform(title, summary_title), run_time=1.5)

        ionic_summary = Text('Ionic: Electron Transfer, Forms Ions', font_size=36, color=RED).shift(UP*1)
        covalent_summary = Text('Covalent: Electron Sharing, Forms Molecules', font_size=36, color=GREEN).shift(DOWN*1)

        self.play(Write(ionic_summary), run_time=1.5)
        self.play(Write(covalent_summary), run_time=1.5)
        self.wait(3)

        self.play(FadeOut(title, ionic_summary, covalent_summary))
        self.wait(0.5)