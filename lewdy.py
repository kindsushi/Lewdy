#AUTHOR: Kindsushi-(GITHUB), see license line 344, feel free to modify anything you want, code might be messy as fuck but it works, I tried to make it pretty as I could, but is definetly not simpler.
#you might modify and do anything you want with this program, the only thing you SHOULD do is to credit me as well in your final modification as it is protected by the repo.

#PROGRAM: Lewdy
#VERSION: 1.00.0 / Format: x.update.hotfix /

#thank you for trying Lewdy and for contributing to the code! :) - KS
import os
import requests
import customtkinter as ctk
from PIL import Image, ImageTk, ImageFile
from io import BytesIO
import threading
import random
import webbrowser
import json
from customtkinter import CTkImage
import tkinter as tk
from tkinter import filedialog

ImageFile.LOAD_TRUNCATED_IMAGES = True

APP_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(APP_DIR, "logo.ico")
LOGO_PATH = os.path.join(APP_DIR, "logo.png")

API_KEY = "m8FkKh8qUo-qW6P1PdXNmiAifOTvyZD-PiovqSPNQb" # I actually use 2 API keys from NIGHT API, here and line 227, It did not work with just one, but it worked with two different keys, idk weird, you can get yours too.
BASE_URL = "https://api.night-api.com/images/nsfw"

TYPES = [
    "Anal", "Ass", "Boobs", "Gonewild", "Hanal", "Hass", "Hboobs", "Hentai",
    "Hkitsune", "Hmidriff", "Hneko", "Hthigh", "Neko", "Paizuri", "Pgif",  #NIGTH API defines these types in their format of images or gifs, I don't give a fuck about these because I made it random lol
    "Pussy", "Tentacle", "Thigh", "Yaoi"                                   #But might be useful for you if you want to get a specific type of image.
]

POSITION_FILE = "window_position.json"

def save_window_position(x, y):
    with open(POSITION_FILE, "w") as f:
        json.dump({"x": x, "y": y}, f)

def load_window_position():
    if os.path.exists(POSITION_FILE):
        with open(POSITION_FILE, "r") as f:
            try:
                pos = json.load(f)
                return pos.get("x", 100), pos.get("y", 100)
            except:
                return 100, 100
    return 100, 100

def resize_image_proportionally(img, max_size=(700, 500)):
    img_ratio = img.width / img.height
    max_width, max_height = max_size
    max_ratio = max_width / max_height

    if img.width <= max_width and img.height <= max_height:
        return img

    if img_ratio > max_ratio:
        new_width = max_width
        new_height = int(max_width / img_ratio)
    else:
        new_height = max_height
        new_width = int(max_height * img_ratio)

    return img.resize((new_width, new_height), Image.Resampling.LANCZOS) # CAREFUL MODIFYING, UPSCALES AND MAKES EVERYTHING PRETTY

class LewdyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Lewdy Viewer")

        try:
            self.iconbitmap(ICON_PATH)
        except Exception as e:
            print(f"Program couldn't reach icon {e}")  # you gonna see exceptions like this all over the program, might be useful as this returns are printed on your terminal and shows where some errors came from.

        x, y = load_window_position()
        self.geometry(f"700x500+{x}+{y}")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.last_saved_position = (x, y)
        self.bind("<Configure>", self.track_window_position) 

        self.current_gif_frame = 0
        self.gif_animation_job = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=10)
        self.grid_rowconfigure(2, weight=1)

        self.image_label = ctk.CTkLabel(self, text="Click ''Random'' to start", anchor="center")
        self.image_label.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)

        self.random_button = ctk.CTkButton(
            self, text="Random", command=self.start_random_thread,
            fg_color="#cc45d1", hover_color="#b03fb5",
            corner_radius=20, font=("Arial", 14, "bold"), text_color="black"
        )
        self.random_button.grid(row=2, column=0, pady=10)

        self.info_button = ctk.CTkButton(
            self, text="ℹ", width=25, height=25, command=self.open_info_window,
            fg_color="#cc45d1", hover_color="#b03fb5",
            corner_radius=0, font=("Arial", 14, "bold"), text_color="black"
        )
        self.info_button.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

        self.download_button = ctk.CTkButton(
            self, text="⬇", width=25, height=25, command=self.download_image,
            fg_color="#cc45d1", hover_color="#b03fb5",
            corner_radius=0, font=("Arial", 14, "bold"), text_color="black"
        )
        self.download_button.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

    def show_toast(self, message, duration=1500):
        toast = ctk.CTkLabel(self, text=message, font=("Arial", 14),
                             fg_color="#2b2b2b", text_color="white",
                             corner_radius=10)
        toast.place(relx=0.5, rely=0.05, anchor="n")
        toast.attributes = {"alpha": 0.0}

        def fade_in(step=0):
            alpha = step / 10
            if alpha <= 1.0:
                toast.attributes["alpha"] = alpha
                toast.configure(text_color=f"#{int(255*alpha):02x}{int(255*alpha):02x}{int(255*alpha):02x}")
                toast.after(20, lambda: fade_in(step + 1))
            else:
                toast.after(duration, fade_out)

        def fade_out(step=10):
            alpha = step / 10
            if alpha >= 0.0:
                toast.attributes["alpha"] = alpha
                toast.configure(text_color=f"#{int(255*alpha):02x}{int(255*alpha):02x}{int(255*alpha):02x}")
                toast.after(20, lambda: fade_out(step - 1))
            else:
                toast.destroy()

        fade_in()

    def download_image(self):
        try:
            if hasattr(self, "tk_image") and self.tk_image._light_image:
                
                if hasattr(self, "frames") and self.frames and self.gif_animation_job:
                    file_path = filedialog.asksaveasfilename(
                        defaultextension=".gif",
                        filetypes=[("GIF files", "*.gif"), ("All files", "*.*")],
                        title="Save GIF as"
                    )

                    if file_path:
                        self.frames[0].save(
                            file_path,
                            save_all=True,
                            append_images=self.frames[1:],
                            duration=100,
                            loop=0
                        )
                        self.show_toast("File saved")
                    else:
                        print("Cancelled save")
                else:
                    
                    image = self.tk_image._light_image
                    file_path = filedialog.asksaveasfilename(
                        defaultextension=".png",
                        filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg *.jpeg"), ("All files", "*.*")],
                        title="Save Image as"
                    )

                    if file_path:
                        image.save(file_path)
                        self.show_toast("File saved")
                    else:
                        print("Cancelled save")
            else:
                print("No image shown to save")
        except Exception as e:
            print(f"Error saving the file {e}")
            
    def minimize_all(self):
        self.iconify()

    def track_window_position(self, event):
        try:
            geo = self.geometry()
            if "+" in geo:
                size, x, y = geo.split("+")
                x, y = int(x), int(y)
                if (x, y) != self.last_saved_position:
                    save_window_position(x, y)
                    self.last_saved_position = (x, y)
        except:
            pass

    def on_closing(self):
        geo = self.geometry()
        if "+" in geo:
            size, x, y = geo.split("+")
            save_window_position(int(x), int(y))
        self.destroy()

    def start_random_thread(self):
        self.random_button.configure(state="disabled", text="Loading...")
        random_type = random.choice(TYPES)
        threading.Thread(target=lambda: self.load_image(random_type), daemon=True).start()

    def animate_gif(self, frames, delay):
        frame = frames[self.current_gif_frame]
        self.tk_image = CTkImage(light_image=frame, size=frame.size)
        self.image_label.configure(image=self.tk_image, text="")
        self.current_gif_frame = (self.current_gif_frame + 1) % len(frames)
        self.gif_animation_job = self.after(delay, lambda: self.animate_gif(frames, delay))

    def stop_animation(self):
        if self.gif_animation_job is not None:
            self.after_cancel(self.gif_animation_job)
            self.gif_animation_job = None

    def load_image(self, img_type):
        self.stop_animation()
        headers = {"authorization": "XO31t0rU20-irsJF8zx3guix9fMjyDB-2M84J66YfP"} #API KEY N2 -------------- is not my format, I copied exactly like NIGHT API docs are shown.

        try:
            url = f"{BASE_URL}?type={img_type.lower()}"
            response = requests.get(url, headers=headers)
            data = response.json()

            if response.status_code == 200 and "url" in data["content"]:
                image_url = data["content"]["url"]
                extension = os.path.splitext(image_url)[1].lower()

                if extension == ".webm":
                    self.after(0, lambda: self.image_label.configure(text="Format not compatible.", image=None)) #I don't think .webm images are included in NIGHTAPI database,
                    return                                                                                       # but sometimes it frozen and I thought It could be this, it didn't froze anymore lol.

                img_data = requests.get(image_url).content
                img = Image.open(BytesIO(img_data))

                if extension == ".gif" and getattr(img, "is_animated", False):
                    self.frames = []
                    try:
                        for frame_index in range(0, img.n_frames):
                            img.seek(frame_index)
                            frame = img.convert("RGBA")
                            resized = resize_image_proportionally(frame)
                            self.frames.append(resized)
                    except Exception as gif_error:
                        print(f"Error processing gif: {gif_error}")
                    self.current_gif_frame = 0
                    delay = img.info.get("duration", 100)
                    self.after(0, lambda: self.animate_gif(self.frames, delay))
                else:
                    img = resize_image_proportionally(img)
                    self.tk_image = CTkImage(light_image=img, size=img.size)
                    self.after(0, lambda: self.image_label.configure(image=self.tk_image, text=""))
            else:
                self.after(0, lambda: self.image_label.configure(text="API Response error, see NIGHT-API key/s.", image=None)) #If you see this in the program, it's probably because of any API_KEY.

        except Exception as e:
            self.after(0, lambda: self.image_label.configure(text=f"Error: {e}", image=None))

        self.after(0, lambda: self.random_button.configure(state="normal", text="Random"))

    def open_info_window(self):
        info_window = ctk.CTkToplevel(self)
        info_window.title("Info")
        info_window.geometry("300x260")
        info_window.resizable(False, False)
        info_window.transient(self)
        info_window.grab_set()
        info_window.lift()
        info_window.attributes("-topmost", True)
        info_window.attributes("-alpha", 0.0)

        def fade_in(step=0):
            alpha = step / 20
            if alpha <= 1:
                info_window.attributes("-alpha", alpha)
                self.after(10, lambda: fade_in(step + 1))

        def fade_out():
            def step_out(step=20):
                alpha = step / 20
                if alpha > 0:
                    info_window.attributes("-alpha", alpha)
                    self.after(10, lambda: step_out(step - 1))
                else:
                    info_window.destroy()
            step_out()

        try:
            info_window.iconbitmap(ICON_PATH)
        except Exception as e:
            print(f"Couldn't reach icon on info_window: {e}")  #this just exists so you can edit the icons and logotypes shown under, it doesn't work on the .exe because contents are installed in already.

        self.update_idletasks()
        main_x = self.winfo_rootx()
        main_y = self.winfo_rooty()
        main_width = self.winfo_width()
        main_height = self.winfo_height()
        info_width = 300
        info_height = 260
        pos_x = main_x + (main_width - info_width) // 2
        pos_y = main_y + (main_height - info_height) // 2
        info_window.geometry(f"{info_width}x{info_height}+{pos_x}+{pos_y}")

        try:
            logo_image = Image.open(LOGO_PATH).resize((64, 64), Image.Resampling.LANCZOS) 
            logo = CTkImage(light_image=logo_image, size=(64, 64))
            logo_label = ctk.CTkLabel(info_window, image=logo, text="")
            logo_label.pack(pady=(10, 5))
        except Exception as e:
            print(f"Couldn't load logo on logo_path: {e}") 

        title_label = ctk.CTkLabel(info_window, text="Developed by Kindsushi", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 0))

        selectable_text = tk.Text(
            info_window, wrap="word", height=5, width=30,
            bg="#1a1a1a", bd=0, relief="flat",
            font=("Arial", 13), fg="gray85", cursor="arrow"
        )
        selectable_text.insert("1.0", "Lewdy\nv1.00.0\nThank you for using Lewdy!\n\n")  #idk why I made it selectable text at the first time, maybe I wanted to type another selectable thing I don't remember...
        selectable_text.tag_configure("center", justify="center")                       #too lazy to fix this, might update it later! (￣ω￣;) | Also line before this shows version!
        selectable_text.tag_add("center", "1.0", "end")
        selectable_text.config(state="normal")
        selectable_text.pack(pady=(5, 0))
        selectable_text.bind("<Key>", lambda e: "break")

        link_label = ctk.CTkLabel(info_window, text="Report a bug/Github repo", text_color="lightblue", cursor="hand2")
        link_label.pack(pady=2)
        link_label.bind("<Button-1>", lambda e: (self.minimize_all(), fade_out(), webbrowser.open("https://github.com/kindsushi/Lewdy")))

        license_label = ctk.CTkLabel(info_window, text="See License", text_color="lightblue", cursor="hand2")
        license_label.pack(pady=2)
        license_label.bind("<Button-1>", lambda e: (self.minimize_all(), fade_out(), webbrowser.open("https://raw.githubusercontent.com/kindsushi/Lewdy/refs/heads/main/LICENSE")))

        info_window.protocol("WM_DELETE_WINDOW", fade_out)
        fade_in()

if __name__ == "__main__":
    app = LewdyApp()
    app.mainloop()

#  		ヾ(・ω・*)