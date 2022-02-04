"""
FEATURES:
    * play as much as you want unlike original wordle
    * toggle full screen mode with <F11>

TODO:
    [X] new_game not working, make it work
    [X] add a virtual keyboard
    [X] make the boxes border white if it contains a letter that has not been checked yet
    [X] highlight used letters on the virtual keyboard
    [ ] toast to show error messages
    [ ] an overlay window to ask if you wanna play another game
    [ ] after solving a puzzle a timer will start for 1 hour and you can't solve another puzzle unitl it ends
    [ ] add help menu
    [ ] add settings menu
    [ ] add a way to not pick the same random word again (store all the words already picked by the program)
    [ ] add a option to add a custom wordlist
    [ ] add a score keeping mechanism
    [ ] create a tkinter starting template or templates
    [ ] create a tkinter cookbook

tkinter cookbook ideas:
    * starting templates
    * good practices
    * toggle fullscreen mode
    * switching between multiple frames in a single toplevel window
    * sample scripts to make an executable using pyinstaller


"You're a dumbo"
"Go to Pre-KG and learn English"
"Wow, you're so bad"
"""
from tkinter import messagebox, ttk
from pathlib import Path

import tkinter as tk
import random
import string
import sys


WORD_LEN = 5
MAX_TRIES = 6
COLOR_BORDER_HIGHLIGHT = "#565758"
COLOR_BLANK = "#121213"
COLOR_INCORRECT = "#3a3a3c"
COLOR_HALF_CORRECT = "#b59f3b"
COLOR_CORRECT = "#538d4e"
BOX_SIZE = 55
PADDING = 3

try:
    BASE_PATH = Path(sys._MEIPASS)
except AttributeError:
    BASE_PATH = Path(".")

VALID_WORDS_WORDLIST = BASE_PATH / "wordlists/wordle-allowed-guesses.txt"
ANSWERS_WORDLIST = BASE_PATH / "wordlists/wordle-answers.txt"
APP_ICON = BASE_PATH / "assets/wordle_logo_32x32.ico"
BACKSPACE_ICON = BASE_PATH / "assets/backspace.png"
HELP_ICON = BASE_PATH / "assets/help.png"
SETTINGS_ICON = BASE_PATH / "assets/settings.png"
MANUAL_IMAGE = BASE_PATH / "assets/manual_image2.png"

ANSWERS = set(word.upper() for word in open(ANSWERS_WORDLIST).read().splitlines())
ALL_WORDS = set(word.upper() for word in open(VALID_WORDS_WORDLIST).read().splitlines()) | ANSWERS


class Manual(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        # sticky="ns" occupies extra space above and below but not on the sides
        self.grid(sticky="ns")

        # container = tk.Frame(self, bg=COLOR_BLANK)
        # container.grid()

        # f = tk.Frame(container, bg=COLOR_BLANK)
        # tk.Label(f, text="HOW TO PLAY")
        self.manual_image = tk.PhotoImage(file=MANUAL_IMAGE)
        tk.Label(self, image=self.manual_image).grid(sticky="nswe")


class Wordle(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        # sticky="ns" occupies extra space above and below but not on the sides
        self.grid(sticky="ns")

        self.master.title("Wordle - A Word Game")
        # self.master.state("zoomed")
        # self.master.resizable(False, False)
        self.master.iconbitmap(APP_ICON)
        # self.master.iconphoto(False, tk.PhotoImage(file="wordle_logo_32x32.png"))
        self.fullscreen = False

        self.master.bind("<F11>", self.fullscreen_toggle)
        self.master.bind("<Return>", self.check_word)
        self.master.bind("<BackSpace>", self.remove_letter)
        self.master.bind("<Key>", self.enter_letter)

        self.init_ui()
        self.new_game()

    def fullscreen_toggle(self, event=None):
        if self.fullscreen:
            self.master.wm_attributes("-fullscreen", False)
            self.fullscreen = False
        else:
            self.master.wm_attributes("-fullscreen", True)
            self.fullscreen = True

    def new_game(self):
        self.answer = random.choice(list(ANSWERS)).upper()
        self.words = [""] * 6
        self.correct_letters = set()
        self.half_correct_letter = set()
        self.incorrect_letters = set()

        # reset the labels and keyboard
        for i in range(MAX_TRIES):
            self.current_word = i
            self.update_labels()
        self.current_word = 0
        self.update_keyboard()

    def congratulate(self):
        title = ["Genius", "Magnificent", "Impressive", "Splendid", "Great", "Phew"][self.current_word]
        message = "Wanna Play Another Game?"
        if messagebox.askyesno(title, message):
            self.new_game()
        else:
            self.master.destroy()

    def humiliate(self):
        title = "Better Luck Next Time!"
        message = f"One More Game?\n(BTW the word was {self.answer}.)"
        if messagebox.askyesno(title, message):
            self.new_game()
        else:
            self.master.destroy()

    def init_ui(self):
        self.icons = {
            "settings": tk.PhotoImage(file=SETTINGS_ICON),
            "help": tk.PhotoImage(file=HELP_ICON),
            "backspace": tk.PhotoImage(file=BACKSPACE_ICON),
        }

        # ==> top bar ==>
        container = tk.Frame(self, bg=COLOR_BLANK, height=40)
        container.grid(sticky="we")
        container.grid_columnconfigure(1, weight=1)

        # help button
        tk.Button(
            container,
            image=self.icons["help"],
            bg=COLOR_BLANK,
            border=0,
            cursor="hand2",
        ).grid(row=0, column=0)

        # title
        tk.Label(
            container,
            text="WORDLE",
            fg="#d7dadc",
            bg=COLOR_BLANK,
            font=("Helvetica Neue", 28, "bold"),
        ).grid(row=0, column=1)

        # settings button
        tk.Button(
            container,
            image=self.icons["settings"],
            bg=COLOR_BLANK,
            border=0,
            cursor="hand2",
        ).grid(row=0, column=2)
        # <== top bar <==

        # separator
        ttk.Separator(self).grid(sticky="ew")
        tk.Frame(self, bg=COLOR_BLANK, height=40).grid()

        # ==> main game grid ==>
        # if there is extra space then give it to main game grid
        self.rowconfigure(3, weight=1)
        container = tk.Frame(self, bg=COLOR_BLANK)
        container.grid()

        self.labels = []
        for i in range(MAX_TRIES):
            row = []
            for j in range(WORD_LEN):
                cell = tk.Frame(
                    container,
                    width=BOX_SIZE,
                    height=BOX_SIZE,
                    highlightthickness=1,
                    highlightbackground=COLOR_INCORRECT,
                )
                cell.grid_propagate(0)
                cell.grid_rowconfigure(0, weight=1)
                cell.grid_columnconfigure(0, weight=1)
                cell.grid(row=i, column=j, padx=PADDING, pady=PADDING)
                t = tk.Label(
                    cell,
                    text="",
                    justify="center",
                    font=("Helvetica Neue", 24, "bold"),
                    bg=COLOR_BLANK,
                    fg="#d7dadc",
                    highlightthickness=1,
                    highlightbackground=COLOR_BLANK,
                )
                t.grid(sticky="nswe")
                row.append(t)
            self.labels.append(row)
        # <== main game grid <==

        # bottom empty separator
        tk.Frame(self, bg=COLOR_BLANK, height=40).grid()

        # ==> virtual keyboard ==>
        container = tk.Frame(self, bg=COLOR_BLANK)
        container.grid()

        # add all the alphabets
        self.keyboard_buttons = {}
        for i, keys in enumerate(["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]):
            row = tk.Frame(container, bg=COLOR_BLANK)
            row.grid(row=i, column=0)

            for j, c in enumerate(keys):
                if i == 2:  # leave one column for the ENTER button in the last row
                    j += 1

                cell = tk.Frame(
                    row,
                    width=40,
                    height=55,
                    highlightthickness=1,
                    highlightbackground=COLOR_INCORRECT,
                )
                cell.grid_propagate(0)
                cell.grid_rowconfigure(0, weight=1)
                cell.grid_columnconfigure(0, weight=1)
                cell.grid(row=0, column=j, padx=PADDING, pady=PADDING)
                btn = tk.Button(
                    cell,
                    text=c,
                    justify="center",
                    font=("Helvetica Neue", 13),
                    bg=COLOR_BLANK,
                    fg="#d7dadc",
                    cursor="hand2",
                    border=0,
                    command=lambda c=c: self.enter_letter(key=c),
                )
                btn.grid(sticky="nswe")
                self.keyboard_buttons[c] = btn

        # add the enter and delete buttons
        for col, text, func in ((0, "ENTER", self.check_word), (8, "", self.remove_letter)):
            cell = tk.Frame(
                row,
                width=75,
                height=55,
                highlightthickness=1,
                highlightbackground=COLOR_INCORRECT,
            )
            cell.grid_propagate(0)
            cell.grid_rowconfigure(0, weight=1)
            cell.grid_columnconfigure(0, weight=1)
            cell.grid(row=0, column=col, padx=PADDING, pady=PADDING)
            btn = tk.Button(
                cell,
                text=text,
                justify="center",
                font=("Helvetica Neue", 13),
                bg=COLOR_BLANK,
                fg="#d7dadc",
                cursor="hand2",
                border=0,
                command=func,
            )
            btn.grid(row=0, column=0, sticky="nswe")

        # set the image for delete button
        btn.configure(image=self.icons["backspace"])

        # <== virtual keyboard <==

    def update_keyboard(self):
        for key, btn in self.keyboard_buttons.items():
            if key in self.correct_letters:
                btn["bg"] = COLOR_CORRECT
            elif key in self.half_correct_letter:
                btn["bg"] = COLOR_HALF_CORRECT
            elif key in self.incorrect_letters:
                btn["bg"] = COLOR_INCORRECT
            else:
                btn["bg"] = COLOR_BLANK

    def update_labels(self, colors=None):
        word = self.words[self.current_word]
        for i, label in enumerate(self.labels[self.current_word]):
            try:
                letter = word[i]
            except IndexError:
                letter = ""

            label["text"] = letter
            if colors:
                label["bg"] = colors[i]
                label["highlightbackground"] = colors[i]
            else:
                label["bg"] = COLOR_BLANK
                label["highlightbackground"] = COLOR_BORDER_HIGHLIGHT if letter else COLOR_BLANK

    def check_word(self, event=None):
        print("checking word:", self.words[self.current_word])
        word = self.words[self.current_word]
        if len(word) < WORD_LEN:
            messagebox.showinfo("You're an Idiot.", "Not Enough Letters.")
            return

        if word not in ALL_WORDS:
            messagebox.showinfo("You're an Idiot.", "Word is not in wordlist.")
            return

        colors = []
        freq = {c: self.answer.count(c) for c in self.answer}
        for x, y in zip(word, self.answer):
            if x == y:
                colors.append(COLOR_CORRECT)
                self.correct_letters.add(x)
            elif freq.get(x, 0) > 0:
                colors.append(COLOR_HALF_CORRECT)
                self.half_correct_letter.add(x)
                freq[x] -= 1
            else:
                self.incorrect_letters.add(x)
                colors.append(COLOR_INCORRECT)
        self.update_labels(colors)
        self.update_keyboard()

        if word == self.answer:
            self.congratulate()

        self.current_word += 1
        if self.current_word >= MAX_TRIES:
            self.humiliate()

    def remove_letter(self, event=None):
        if self.words[self.current_word]:
            print(self.words[self.current_word][-1], "was deleted.")
            self.words[self.current_word] = self.words[self.current_word][:-1]
            self.update_labels()

    def enter_letter(self, event=None, key=None):
        key = key or event.keysym.upper()
        if key in string.ascii_uppercase:
            print(key, "was entered.")
            self.words[self.current_word] += key
            # prevent user from enterering excess letters
            self.words[self.current_word] = self.words[self.current_word][:WORD_LEN]
            self.update_labels()


if __name__ == "__main__":
    # initialize the app
    root = tk.Tk()
    root.configure(bg=COLOR_BLANK)
    app = Wordle(root, bg=COLOR_BLANK)

    # center the frame
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    # run the app
    app.mainloop()

"""
https://www.reddit.com/r/wordle/comments/s4tcw8/a_note_on_wordles_word_list/

wordle answers: https://gist.github.com/cfreshman/a03ef2cba789d8cf00c08f767e0fad7b
wordle allowed words: https://gist.github.com/cfreshman/cdcdf777450c5b5301e439061d29694c


"""
