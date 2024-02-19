import tkinter as tk

# Create a new instance of Tkinter
window = tk.Tk()

# Set the window title
window.title("My GUI")

# Set the window size
window.geometry("400x300")

# Add a label to the window
label = tk.Label(window, text="Hello, World!")
label.pack()


# Start the Tkinter event loop
window.mainloop()