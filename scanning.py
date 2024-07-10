import tkinter as tk
from tkinter import Label, Text, ttk
import cv2
import pytesseract
from PIL import Image, ImageTk
import time

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class VideoTextExtractorApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Video Text Extractor")
        self.root.geometry("800x600")
        self.cap = None
        self.frame_count = 0
        self.extracted_text = ""
        self.camera_index = 0
        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        self.camera_label = tk.Label(self.root, text="Select Camera:")
        self.camera_label.grid(row=0, column=0, pady=10, padx=10)

        self.camera_selection = ttk.Combobox(self.root, values=["Front Camera", "Back Camera"])
        self.camera_selection.current(0)
        self.camera_selection.grid(row=0, column=1, pady=10, padx=10)

        self.start_button = tk.Button(self.root, text="Start Scanning", command=self.start_scanning, bg='lightblue')
        self.start_button.grid(row=1, column=0, pady=10, padx=10)

        self.stop_button = tk.Button(self.root, text="Stop Scanning", command=self.stop_scanning, bg='lightblue')
        self.stop_button.grid(row=1, column=1, pady=10, padx=10)

        self.text_output = Text(self.root, wrap='word', height=10)
        self.text_output.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")

        self.video_label = tk.Label(self.root)
        self.video_label.grid(row=3, column=0, pady=5, padx=5, columnspan=2)

        self.digits_label = tk.Label(self.root, text="", wraplength=780, anchor="w", justify="left")
        self.digits_label.grid(row=4, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")

        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def start_scanning(self):
        if self.cap is not None:
            self.text_output.insert(tk.END, "Already scanning...\n")
            return

        self.camera_index = 0 if self.camera_selection.get() == "Front Camera" else 1

        self.text_output.insert(tk.END, "Starting scanning...\n")
        self.cap = cv2.VideoCapture(self.camera_index)
        self.frame_count = 0
        self.extracted_text = ""
        self.scan_video()

    def stop_scanning(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            self.text_output.insert(tk.END, "Scanning stopped.\n")

    def on_closing(self):
        self.stop_scanning()
        self.root.destroy()

    def resize_frame(self, frame, width, height):
        resized_frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
        return resized_frame

    def show_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = Image.fromarray(frame)
        frame = ImageTk.PhotoImage(frame)
        self.video_label.configure(image=frame)
        self.video_label.image = frame

    def extract_text_from_image(self, image):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray_image, config='--psm 6 outputbase digits')
        return text

    def scan_video(self):
        if self.cap is None:
            return

        ret, frame = self.cap.read()
        if not ret:
            self.stop_scanning()
            return

        self.frame_count += 1
        if self.frame_count % 50 == 0:
            start_time = time.time()
            frame = self.resize_frame(frame, 500, 200)
            text = self.extract_text_from_image(frame)
            self.extracted_text += text.replace('\n', ' ') + ' '
            end_time = time.time()
            elapsed_time = end_time - start_time
            self.text_output.insert(tk.END, f"Text: {text} (Time: {elapsed_time:.2f} sec)\n")
            self.digits_label.config(text=self.extracted_text)
            self.show_frame(frame)
            self.root.update_idletasks()

        self.root.after(10, self.scan_video)

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoTextExtractorApp(root)
    root.resizable(0, 0)
    root.mainloop()
