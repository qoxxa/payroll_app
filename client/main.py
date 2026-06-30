import tkinter as tk
from ui import PayrollAppUI

if __name__ == "__main__":
    root = tk.Tk()
    app = PayrollAppUI(root)
    root.mainloop()