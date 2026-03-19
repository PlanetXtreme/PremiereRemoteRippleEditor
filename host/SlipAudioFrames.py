import sys
import re
import tkinter as tk
from tkinter import simpledialog

def get_frames():
    root = tk.Tk()
    root.withdraw() # Hides the background window

    # Prompt user
    user_input = simpledialog.askstring("Slip Audio", "Enter frames to slip (e.g. 11 or -5):")
    
    if user_input is not None:
        # Strip everything except numbers and minus signs
        sanitized = re.sub(r'[^\d-]', '', user_input)
        
        if sanitized and sanitized != '-':
            print(sanitized)
        else:
            print("0")
    else:
        print("cancelled")

if __name__ == "__main__":
    get_frames()