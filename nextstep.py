import pygame
import sys
import webbrowser

# -------------------- Initialization --------------------

pygame.init()
pygame.font.init()

# -------------------- Configuration --------------------

SCREEN_WIDTH  = 640
SCREEN_HEIGHT = 480
FPS           = 30

# Colors (R, G, B)
BG_COLOR        = (230, 240, 250)   # very light blue background
HEADER_COLOR    = (30, 144, 255)    # dodger blue header
HEADER_TEXT     = (255, 255, 255)   # white for header text
BUTTON_COLOR    = (70, 130, 180)    # steel blue buttons
BUTTON_HOVER    = (100, 160, 210)   # lighter steel blue on hover
TEXT_COLOR      = (40, 40, 40)      # dark gray text for screen content
BUTTON_TEXT     = (255, 255, 255)   # white text on buttons

# Fonts
FONT_HEADER    = pygame.font.SysFont(None, 36, bold=True)
FONT_BUTTON    = pygame.font.SysFont(None, 26, bold=True)
FONT_CONTENT   = pygame.font.SysFont(None, 22)

# URLs for “Find Jobs”
HS_URL      = (
    "https://www.indeed.com/jobs?"
    "q=high+school+student&l=&radius=35&from=searchOnDesktopSerp"
)
COLLEGE_URL = (
    "https://www.indeed.com/jobs?"
    "q=college+student&l=&radius=25&from=searchOnDesktopSerp"
)

# -------------------- Helper Classes & Functions --------------------

class Button:
    """A simple rectangular button with hover effect."""
    def __init__(self, rect, text, callback):
        self.rect     = pygame.Rect(rect)
        self.text     = text
        self.callback = callback
        self.hovered  = False

    def draw(self, screen):
        color = BUTTON_HOVER if self.hovered else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect, border_radius=7)
        txt_surf = FONT_BUTTON.render(self.text, True, BUTTON_TEXT)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        screen.blit(txt_surf, txt_rect)

    def update(self, mouse_pos, mouse_click):
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.hovered and mouse_click:
            self.callback()


def draw_header(screen, title):
    """Draw a header bar with the given title text."""
    pygame.draw.rect(screen, HEADER_COLOR, (0, 0, SCREEN_WIDTH, 60))
    txt_surf = FONT_HEADER.render(title, True, HEADER_TEXT)
    txt_rect = txt_surf.get_rect(center=(SCREEN_WIDTH // 2, 30))
    screen.blit(txt_surf, txt_rect)


def draw_text_lines(screen, lines, start_x, start_y, line_spacing=5):
    """Render a list of strings in a column starting at (start_x, start_y)."""
    y = start_y
    for line in lines:
        surf = FONT_CONTENT.render(line, True, TEXT_COLOR)
        screen.blit(surf, (start_x, y))
        y += FONT_CONTENT.get_height() + line_spacing


# -------------------- Main App Class --------------------

class TeenJobFinderApp:
    def __init__(self):
        self.screen         = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Teen Job Finder")
        self.clock          = pygame.time.Clock()
        self.current_screen = "menu"   # "menu", "job_type", "job_tips", "build_resume", "interview_tips"
        self.buttons        = []
        self.build_menu()

    # --------------- Screen Builders ---------------

    def build_menu(self):
        """Construct the main menu buttons."""
        self.current_screen = "menu"
        self.buttons = []

        btn_w, btn_h = 240, 50
        spacing = 15
        start_y = 140

        labels_and_callbacks = [
            ("Find Jobs",          self.goto_job_type),
            ("Job Search Tips",    self.goto_job_tips),
            ("Build Resume",       self.goto_build_resume),
            ("Interview Tips",     self.goto_interview_tips),
            ("Exit",               self.exit_app),
        ]

        for i, (label, cb) in enumerate(labels_and_callbacks):
            x = (SCREEN_WIDTH - btn_w) // 2
            y = start_y + i * (btn_h + spacing)
            self.buttons.append(Button((x, y, btn_w, btn_h), label, cb))

    def build_job_type(self):
        """Construct the 'High School / College' choice buttons."""
        self.current_screen = "job_type"
        self.buttons = []

        btn_w, btn_h = 300, 50
        spacing = 20
        start_y = 120

        # HS button
        x = (SCREEN_WIDTH - btn_w) // 2
        y = start_y
        self.buttons.append(Button((x, y, btn_w, btn_h), "High School Student", self.open_hs_link))

        # College button
        y += btn_h + spacing
        self.buttons.append(Button((x, y, btn_w, btn_h), "College Student", self.open_college_link))

        # Back button bottom-left
        self.buttons.append(Button((20, SCREEN_HEIGHT - 60, 100, 40), "Back", self.build_menu))

    def build_job_tips(self):
        """Construct the 'Job Search Tips' screen (static text)."""
        self.current_screen = "job_tips"
        self.buttons = [Button((20, SCREEN_HEIGHT - 60, 100, 40), "Back", self.build_menu)]

    def build_build_resume(self):
        """Stub for Build Resume—just a placeholder screen for now."""
        self.current_screen = "build_resume"
        self.buttons = [Button((20, SCREEN_HEIGHT - 60, 100, 40), "Back", self.build_menu)]

    def build_interview_tips(self):
        """Stub for Interview Tips—just a placeholder screen for now."""
        self.current_screen = "interview_tips"
        self.buttons = [Button((20, SCREEN_HEIGHT - 60, 100, 40), "Back", self.build_menu)]

    # --------------- Callbacks ---------------

    def goto_job_type(self):
        """Switch to the job-type selection screen."""
        self.build_job_type()

    def open_hs_link(self):
        """Open Indeed link for High School Student, then return to menu."""
        webbrowser.open(HS_URL)
        self.build_menu()

    def open_college_link(self):
        """Open Indeed link for College Student, then return to menu."""
        webbrowser.open(COLLEGE_URL)
        self.build_menu()

    def goto_job_tips(self):
        """Switch to the 'Job Search Tips' screen."""
        self.build_job_tips()

    def goto_build_resume(self):
        """Switch to the (stub) Build Resume screen."""
        self.build_build_resume()

    def goto_interview_tips(self):
        """Switch to the (stub) Interview Tips screen."""
        self.build_interview_tips()

    def exit_app(self):
        pygame.quit()
        sys.exit()

    # --------------- Main Loop ---------------

    def run(self):
        while True:
            self.clock.tick(FPS)
            self.handle_events()
            self.draw()

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit_app()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_click = True

        # Update button hover/click states
        for btn in self.buttons:
            btn.update(mouse_pos, mouse_click)

    def draw(self):
        self.screen.fill(BG_COLOR)

        if self.current_screen == "menu":
            self.draw_menu()
        elif self.current_screen == "job_type":
            self.draw_job_type()
        elif self.current_screen == "job_tips":
            self.draw_job_tips()
        elif self.current_screen == "build_resume":
            self.draw_build_resume()
        elif self.current_screen == "interview_tips":
            self.draw_interview_tips()

        pygame.display.flip()

    # --------------- Drawing Each Screen ---------------

    def draw_menu(self):
        """Draw the main menu with header + buttons."""
        draw_header(self.screen, "Teen Job Finder")
        for btn in self.buttons:
            btn.draw(self.screen)

    def draw_job_type(self):
        """Draw the High School / College choice screen."""
        draw_header(self.screen, "Select Student Type")
        # Instruction
        instruct = "Choose your status to find relevant jobs"
        txt_surf = FONT_CONTENT.render(instruct, True, TEXT_COLOR)
        self.screen.blit(txt_surf, ((SCREEN_WIDTH - txt_surf.get_width()) // 2, 80))

        for btn in self.buttons:
            btn.draw(self.screen)

    def draw_job_tips(self):
        """Draw the static 'Job Search Tips' text and Back button."""
        draw_header(self.screen, "Job Search Tips")
        tips = [
            "• Use specific keywords (e.g., “cashier”, “math tutor”)",
            "• Filter by distance or salary if the site allows it",
            "• Read employer reviews before applying",
            "• Tailor your resume to highlight relevant skills",
            "• Check job boards daily—new postings appear often",
            "• Prepare a short cover note if possible",
        ]
        draw_text_lines(self.screen, tips, start_x=40, start_y=100, line_spacing=10)

        for btn in self.buttons:
            btn.draw(self.screen)

    def draw_build_resume(self):
        """Placeholder for a future Resume Builder feature."""
        draw_header(self.screen, "Build Resume")
        note = "Coming soon: an in-app resume builder."
        txt_surf = FONT_CONTENT.render(note, True, TEXT_COLOR)
        self.screen.blit(txt_surf, ((SCREEN_WIDTH - txt_surf.get_width()) // 2, 160))

        for btn in self.buttons:
            btn.draw(self.screen)

    def draw_interview_tips(self):
        """Placeholder for a future Interview Tips feature."""
        draw_header(self.screen, "Interview Tips")
        tips = [
            "• Dress professionally and arrive early",
            "• Practice common interview questions",
            "• Research the company beforehand",
            "• Bring copies of your resume",
            "• Maintain eye contact and good posture",
        ]
        draw_text_lines(self.screen, tips, start_x=40, start_y=100, line_spacing=10)

        for btn in self.buttons:
            btn.draw(self.screen)


# -------------------- Run the Application --------------------

if __name__ == "__main__":
    app = TeenJobFinderApp()
    app.run()