import sys
import pygame
import webbrowser
import torch
from transformers import pipeline

# ---------------- Configuration ----------------
SCREEN_W, SCREEN_H, FPS = 800, 700, 30   # window size

COL_BG      = (230, 240, 250)
COL_HEADER  = (30, 144, 255)
COL_TEXT    = (40, 40, 40)
COL_BTN     = (70, 130, 180)
COL_HOVER   = (100, 160, 210)
COL_WHITE   = (255, 255, 255)
COL_CHAT_BG = COL_WHITE
COL_BORDER  = (200, 200, 200)

MAX_LINES   = 12
CHAT_MARGIN = 20
CHAT_TOP    = 70
CHAT_BOTTOM = SCREEN_H - 140
CHAT_WIDTH  = SCREEN_W - CHAT_MARGIN * 2

HS_URL    = "https://www.indeed.com/jobs?q=high+school+student&l=&radius=35"
COL_URL   = "https://www.indeed.com/jobs?q=college+student&l=&radius=25"

JOB_SEARCH_TIPS = [
    "Use specific keywords: e.g. “cashier”, “tutor”.",
    "Filter by salary or distance when possible.",
    "Read company reviews before applying.",
    "Apply early—new postings appear daily.",
    "Tailor your resume/cover note to each job.",
    "Follow up politely if you don’t hear back in a week."
]
RESUME_TEMPLATE = [
    "YOUR NAME",
    "Address · Email · Phone",
    "",
    "OBJECTIVE: One-sentence summary of what you want.",
    "",
    "EDUCATION",
    "School Name, Graduation Date",
    "Relevant coursework or honors",
    "",
    "EXPERIENCE",
    "Role, Organization, Dates",
    "• Bullet-point duties & achievements",
    "",
    "SKILLS",
    "• List relevant skills (e.g. MS Office, Python)"
]
INTERVIEW_TIPS = [
    "Research the company before you go.",
    "Dress neatly; arrive 10 minutes early.",
    "Bring extra copies of your resume.",
    "Practice answers to common questions.",
    "Ask thoughtful questions at the end.",
    "Send a thank-you email afterward."
]

# Build retrieval context
KB_TEXT = (
    "Job Search Tips:\n- " + "\n- ".join(JOB_SEARCH_TIPS) +
    "\n\nResume Template:\n" + "\n".join(RESUME_TEMPLATE) +
    "\n\nInterview Tips:\n- " + "\n- ".join(INTERVIEW_TIPS)
)
SYSTEM_PROMPT = (
    "You are a direct, expert career coach for high-school and college students.\n"
    "Use ONLY the knowledge below to answer the user’s question with actionable advice.\n"
    "Do NOT repeat the user’s words or make things up.\n\n"
    + KB_TEXT +
    "\n\nUser question:"
)

# ---------------- Local model setup ----------------
print("Loading FLAN-T5-Base (first run downloads ~250 MB)…")
device = 0 if torch.cuda.is_available() else -1
assistant = pipeline(
    "text2text-generation",
    model="google/flan-t5-base",
    device=device
)
print("Model ready.")

def smart_assist_response(query: str) -> str:
    prompt = SYSTEM_PROMPT + " " + query + "\nAnswer:"
    out = assistant(prompt, max_length=200)[0]["generated_text"]
    if "Answer:" in out:
        out = out.split("Answer:")[-1]
    return out.strip()

# ---------------- Text Wrapping ----------------
def wrap_text(text: str, font: pygame.font.Font, max_width: int):
    words = text.split(" ")
    lines = []
    current = ""
    for w in words:
        test = current + (" " if current else "") + w
        if font.size(test)[0] <= max_width:
            current = test
        else:
            lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines

# ---------------- UI Button ----------------
class Button:
    def __init__(self, rect, text, cb):
        self.rect  = pygame.Rect(rect)
        self.text  = text
        self.cb    = cb
        self.hover = False

    def draw(self, surf, font):
        col = COL_HOVER if self.hover else COL_BTN
        pygame.draw.rect(surf, col, self.rect, border_radius=6)
        img = font.render(self.text, True, COL_WHITE)
        surf.blit(img, img.get_rect(center=self.rect.center))

    def update(self, mp, click):
        self.hover = self.rect.collidepoint(mp)
        if self.hover and click:
            self.cb()

# ---------------- Main App ----------------
class NextStepApp:
    def __init__(self):
        pygame.init()
        self.screen    = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Next Step")
        self.clock     = pygame.time.Clock()
        self.f_header  = pygame.font.SysFont(None, 36, bold=True)
        self.f_button  = pygame.font.SysFont(None, 26, bold=True)
        self.f_text    = pygame.font.SysFont(None, 20)

        self.state        = "menu"
        self.buttons      = []
        self.chat_history = []
        self.user_input   = ""
        self.build_menu()

    def build_menu(self):
        self.state   = "menu"
        self.buttons = []
        opts = [
            ("High School Jobs", lambda: webbrowser.open(HS_URL)),
            ("College Jobs",     lambda: webbrowser.open(COL_URL)),
            ("Job Search Tips",  lambda: self.goto("tips")),
            ("Resume Builder",   lambda: self.goto("resume")),
            ("Interview Tips",   lambda: self.goto("interview")),
            ("Smart Assist",     lambda: self.goto("assist")),
            ("Quit",             self.quit_app),
        ]
        for i, (lbl, cb) in enumerate(opts):
            rect = ((SCREEN_W - 300)//2, 120 + i*60, 300, 50)
            self.buttons.append(Button(rect, lbl, cb))

    def goto(self, screen):
        self.state = screen
        self.buttons = [Button((20, SCREEN_H-60, 100, 40), "Back", self.build_menu)]
        if screen == "assist":
            self.chat_history = []
            self.user_input   = ""

    def quit_app(self):
        pygame.quit()
        sys.exit()

    def handle_events(self):
        mp, click = pygame.mouse.get_pos(), False
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.quit_app()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                click = True

            if self.state == "assist" and e.type == pygame.KEYDOWN:
                if e.key == pygame.K_BACKSPACE:
                    self.user_input = self.user_input[:-1]
                elif e.key == pygame.K_RETURN:
                    q = self.user_input.strip()
                    if q:
                        self.chat_history.append(("You", q))
                        self.user_input = ""
                        ans = smart_assist_response(q)
                        self.chat_history.append(("Coach", ans))
                else:
                    if len(self.user_input) < 200 and e.unicode.isprintable():
                        self.user_input += e.unicode

        for b in self.buttons:
            b.update(mp, click)

    def draw(self):
        self.screen.fill(COL_BG)
        pygame.draw.rect(self.screen, COL_HEADER, (0, 0, SCREEN_W, 60))
        titles = {
            "menu":      "Next Step",
            "tips":      "Job Search Tips",
            "resume":    "Resume Builder",
            "interview": "Interview Tips",
            "assist":    "Smart Assist"
        }
        hdr = self.f_header.render(titles[self.state], True, COL_WHITE)
        self.screen.blit(hdr, hdr.get_rect(center=(SCREEN_W//2, 30)))

        if self.state != "assist":
            # draw other screens (menu, tips, resume, interview)
            if self.state == "menu":
                for b in self.buttons:
                    b.draw(self.screen, self.f_button)
            elif self.state == "tips":
                y = 80
                for tip in JOB_SEARCH_TIPS:
                    surf = self.f_text.render("• " + tip, True, COL_TEXT)
                    self.screen.blit(surf, (30, y)); y += 24
                for b in self.buttons:
                    b.draw(self.screen, self.f_button)
            elif self.state == "resume":
                y = 80
                for line in RESUME_TEMPLATE:
                    surf = self.f_text.render(line, True, COL_TEXT)
                    self.screen.blit(surf, (30, y)); y += 20
                for b in self.buttons:
                    b.draw(self.screen, self.f_button)
            elif self.state == "interview":
                y = 80
                for tip in INTERVIEW_TIPS:
                    surf = self.f_text.render("• " + tip, True, COL_TEXT)
                    self.screen.blit(surf, (30, y)); y += 24
                for b in self.buttons:
                    b.draw(self.screen, self.f_button)

        else:
            # draw chat box
            box = pygame.Rect(CHAT_MARGIN, CHAT_TOP, CHAT_WIDTH, CHAT_BOTTOM - CHAT_TOP)
            pygame.draw.rect(self.screen, COL_CHAT_BG, box)
            pygame.draw.rect(self.screen, COL_BORDER, box, 2)

            # render wrapped chat history
            y = CHAT_TOP + 5
            for speaker, msg in self.chat_history[-MAX_LINES:]:
                prefix = f"{speaker}: "
                lines = wrap_text(msg, self.f_text, CHAT_WIDTH - 10 - self.f_text.size(prefix)[0])
                for i, line in enumerate(lines):
                    text = (prefix + line) if i == 0 else (" " * len(prefix) + line)
                    surf = self.f_text.render(text, True, COL_TEXT)
                    self.screen.blit(surf, (CHAT_MARGIN + 5, y))
                    y += surf.get_height() + 2
                y += 4  # spacing

            # input prompt
            prompt_y = CHAT_BOTTOM + 10
            self.screen.blit(
                self.f_text.render("Ask your career question & ↵:", True, COL_TEXT),
                (CHAT_MARGIN, prompt_y)
            )
            inp = pygame.Rect(CHAT_MARGIN, prompt_y + 25, CHAT_WIDTH, 40)
            pygame.draw.rect(self.screen, COL_CHAT_BG, inp)
            pygame.draw.rect(self.screen, COL_BORDER, inp, 2)
            self.screen.blit(
                self.f_text.render(self.user_input, True, COL_TEXT),
                (inp.x + 5, inp.y + 5)
            )

            for b in self.buttons:
                b.draw(self.screen, self.f_button)

        pygame.display.flip()

    def run(self):
        while True:
            self.clock.tick(FPS)
            self.handle_events()
            self.draw()

if __name__ == "__main__":
    NextStepApp().run()
