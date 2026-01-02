import tkinter as tk
import random
import json
import os

# Adjustable draw interval (milliseconds)
DRAW_INTERVAL = 1000  # 10 seconds

# File to save/load game state
SAVE_FILE = "bingo_state.json"

# Labels for current and previous numbers
CURRENT_LABEL_TEXT = "Nu / Now / இப்போது"
PREVIOUS_LABEL_TEXT = "Før / Before / முதல் வந்த ⚠️"

# Grid highlight color for current number
CURRENT_BOX_COLOR = "#5DADE2"  # darker blue
CURRENT_FONT_COLOR = "black"

# Bottom label colors
CURRENT_LABEL_COLOR = "#ADD8E6"  # dark blue
PREVIOUS_LABEL_COLOR = "#FFA500"  # light orange

class BingoBoard:
    def __init__(self, root):
        self.root = root
        self.root.title("Automatic Bingo Number Board")

        # Fullscreen state
        self.fullscreen = True
        self.root.attributes("-fullscreen", self.fullscreen)

        # Numbers
        self.available_numbers = list(range(1, 91))
        self.selected_numbers = []
        self.buttons = {}
        self.current_number = None
        self.previous_number = None

        # Pause state
        self.paused = False
        self.auto_draw_job = None

        self.create_layout()
        self.load_state()
        self.auto_draw()

    def save_state(self):
        state = {
            "available_numbers": self.available_numbers,
            "selected_numbers": self.selected_numbers,
            "current_number": self.current_number,
            "previous_number": self.previous_number
        }
        with open(SAVE_FILE, "w") as f:
            json.dump(state, f)

    def load_state(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r") as f:
                    state = json.load(f)
                    self.available_numbers = state.get("available_numbers", self.available_numbers)
                    self.selected_numbers = state.get("selected_numbers", [])
                    self.current_number = state.get("current_number")
                    self.previous_number = state.get("previous_number")

                for n in range(1, 91):
                    btn = self.buttons[n]
                    if n == self.current_number:
                        btn.config(bg=CURRENT_BOX_COLOR, fg=CURRENT_FONT_COLOR, font=("Arial", 28, "bold"))
                    elif n in self.selected_numbers:
                        btn.config(bg="darkgrey", fg="black", font=("Arial", 24, "bold"))
                    else:
                        btn.config(bg="white", fg="black", font=("Arial", 24, "bold"))

                self.update_display()
            except Exception as e:
                print("Failed to load saved state:", e)

    def auto_draw(self):
        if self.paused:
            return

        if not self.available_numbers:
            self.update_display(final=True)
            return

        number = random.choice(self.available_numbers)
        self.available_numbers.remove(number)
        self.selected_numbers.append(number)

        for n in self.selected_numbers:
            if n != number:
                btn = self.buttons[n]
                btn.config(bg="darkgrey", fg="black", font=("Arial", 24, "bold"))

        btn = self.buttons[number]
        btn.config(bg=CURRENT_BOX_COLOR, fg=CURRENT_FONT_COLOR, font=("Arial", 28, "bold"))

        self.previous_number = self.current_number
        self.current_number = number

        self.update_display()
        self.save_state()
        self.auto_draw_job = self.root.after(DRAW_INTERVAL, self.auto_draw)

    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            if self.auto_draw_job:
                self.root.after_cancel(self.auto_draw_job)
            self.pause_button.config(text="Resume")
        else:
            self.pause_button.config(text="Pause")
            self.auto_draw()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def reset_game(self):
        if self.auto_draw_job:
            self.root.after_cancel(self.auto_draw_job)

        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)

        self.available_numbers = list(range(1, 91))
        self.selected_numbers = []
        self.current_number = None
        self.previous_number = None

        for n in range(1, 91):
            btn = self.buttons[n]
            btn.config(bg="white", fg="black", font=("Arial", 24, "bold"))

        self.update_display()
        self.paused = False
        self.pause_button.config(text="Pause")
        self.auto_draw()

    def update_display(self, final=False):
        current_text = f"{CURRENT_LABEL_TEXT}: {self.current_number}" if self.current_number else f"{CURRENT_LABEL_TEXT}: None"
        previous_text = f"{PREVIOUS_LABEL_TEXT}: {self.previous_number}" if self.previous_number else f"{PREVIOUS_LABEL_TEXT}: None"

        self.current_label.config(text=current_text, fg=CURRENT_LABEL_COLOR)
        self.previous_label.config(text=previous_text, fg=PREVIOUS_LABEL_COLOR)

        self.selected_text.config(state="normal")
        self.selected_text.delete("1.0", "end")

        numbers = self.selected_numbers
        numbers_per_row = 15
        lines = []
        for i in range(0, len(numbers), numbers_per_row):
            line = ", ".join(str(n) for n in numbers[i:i+numbers_per_row])
            lines.append(line)
        numbers_text = "\n".join(lines)

        if final:
            display_text = f"All numbers have been drawn!\n{numbers_text}"
        else:
            display_text = numbers_text

        self.selected_text.insert("end", display_text)
        self.selected_text.config(state="disabled")
        self.selected_text.see("end")

    def create_layout(self):
        main_frame = tk.Frame(self.root, bg="black")
        main_frame.pack(expand=True, fill="both")

        # Grid frame
        grid_frame = tk.Frame(main_frame, bg="black")
        grid_frame.pack(expand=True, fill="both", padx=20, pady=20)

        rows, cols = 9, 10
        number = 1
        for r in range(rows):
            grid_frame.rowconfigure(r, weight=1)
            for c in range(cols):
                grid_frame.columnconfigure(c, weight=1)
                btn = tk.Button(grid_frame, text=str(number), font=("Arial", 24, "bold"),
                                bg="white", fg="black", relief="raised", state="disabled")
                btn.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)
                self.buttons[number] = btn
                number += 1

        # Top frame: Current, Previous, Pause, Reset, Fullscreen
        top_frame = tk.Frame(main_frame, bg="gray20")
        top_frame.pack(fill="x", pady=(5,2))

        self.current_label = tk.Label(top_frame, text=f"{CURRENT_LABEL_TEXT}: None", font=("Arial", 20, "bold"),
                                      bg="gray20", anchor="w")
        self.current_label.pack(side="left", expand=True, padx=5)

        self.previous_label = tk.Label(top_frame, text=f"{PREVIOUS_LABEL_TEXT}: None", font=("Arial", 20, "bold"),
                                       bg="gray20", anchor="center")
        self.previous_label.pack(side="left", expand=True)

        self.pause_button = tk.Button(top_frame, text="Pause", font=("Arial", 16, "bold"),
                                      bg="orange", fg="white", command=self.toggle_pause)
        self.pause_button.pack(side="right", padx=5)

        self.reset_button = tk.Button(top_frame, text="Reset", font=("Arial", 16, "bold"),
                                      bg="red", fg="white", command=self.reset_game)
        self.reset_button.pack(side="right", padx=5)

        self.fullscreen_button = tk.Button(top_frame, text="⛶", font=("Arial", 16, "bold"),
                                           bg="blue", fg="white", command=self.toggle_fullscreen)
        self.fullscreen_button.pack(side="right", padx=5)

        # Text area for chosen numbers
        text_frame = tk.Frame(main_frame, bg="gray20")
        text_frame.pack(fill="x", pady=(2,5))

        self.selected_text = tk.Text(text_frame, height=6, font=("Arial", 20, "bold"),
                                     bg="gray20", fg="white", wrap="none")
        self.selected_text.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=self.selected_text.yview)
        scrollbar.pack(side="left", fill="y")
        self.selected_text.config(yscrollcommand=scrollbar.set)
        self.selected_text.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = BingoBoard(root)
    root.mainloop()
