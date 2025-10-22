import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from main import search_images


class ImageSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Search")
        self.root.geometry("900x600")
        self.root.configure(bg="lightgray")

        self.images_path = "images/"
        self.photo_references = []

        # Title
        title_label = tk.Label(
            root, text="Image Search", font=("Arial", 16, "bold"), bg="lightgray"
        )
        title_label.pack(pady=10)

        # Search Frame
        search_frame = tk.Frame(root, bg="lightgray")
        search_frame.pack(pady=5)

        # Search Label
        tk.Label(search_frame, text="Search:", font=("Arial", 10), bg="lightgray").pack(
            side=tk.LEFT, padx=5
        )

        # Search Entry
        self.search_entry = tk.Entry(search_frame, font=("Arial", 10), width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", lambda e: self.perform_search())

        # Search Button
        self.search_button = tk.Button(
            search_frame, text="Search", font=("Arial", 10), command=self.perform_search
        )
        self.search_button.pack(side=tk.LEFT, padx=5)

        # Results Label
        self.results_label = tk.Label(root, text="", font=("Arial", 9), bg="lightgray")
        self.results_label.pack(pady=5)

        # Create canvas with scrollbar for images
        canvas_frame = tk.Frame(root, bg="lightgray")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollbar
        self.scrollbar = tk.Scrollbar(canvas_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Canvas
        self.canvas = tk.Canvas(
            canvas_frame, bg="lightgray", yscrollcommand=self.scrollbar.set
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar.config(command=self.canvas.yview)

        # Frame inside canvas for images
        self.images_frame = tk.Frame(self.canvas, bg="lightgray")
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.images_frame, anchor="nw"
        )

        # Bind canvas resize
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.images_frame.bind("<Configure>", self.on_frame_configure)

        # Bind mouse wheel
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind_all("<Button-4>", self.on_mousewheel)
        self.canvas.bind_all("<Button-5>", self.on_mousewheel)

    def on_canvas_configure(self, event):
        """Handle canvas resize"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def on_frame_configure(self, event):
        """Update scroll region when frame size changes"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    def perform_search(self):
        query = self.search_entry.get().strip()

        if not query:
            messagebox.showwarning("Empty Search", "Please enter search keywords!")
            return

        self.clear_results()

        result_images = search_images(query)

        if not result_images:
            self.results_label.config(text=f"No images found for '{query}'")
        else:
            self.results_label.config(text=f"Found {len(result_images)} image(s)")
            self.display_images(result_images)

    def clear_results(self):
        for widget in self.images_frame.winfo_children():
            widget.destroy()
        self.photo_references.clear()
        self.canvas.yview_moveto(0)

    def display_images(self, image_filenames):
        columns = 3
        max_width = 250
        max_height = 250

        for idx, filename in enumerate(image_filenames):
            row = idx // columns
            col = idx % columns

            full_path = os.path.join(self.images_path, filename)

            img_frame = tk.Frame(
                self.images_frame, bg="lightgray", relief=tk.RIDGE, borderwidth=2
            )
            img_frame.grid(row=row, column=col, padx=10, pady=10)

            try:
                img = Image.open(full_path)
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

                photo = ImageTk.PhotoImage(img)
                self.photo_references.append(photo)

                img_label = tk.Label(img_frame, image=photo, bg="lightgray")
                img_label.pack(padx=5, pady=5)

                name_label = tk.Label(
                    img_frame,
                    text=filename,
                    font=("Arial", 8),
                    bg="lightgray",
                    wraplength=max_width,
                )
                name_label.pack(pady=(0, 5))

            except Exception:
                error_label = tk.Label(
                    img_frame,
                    text=f"Error: {filename}",
                    font=("Arial", 9),
                    bg="lightgray",
                    fg="red",
                )
                error_label.pack(padx=10, pady=10)

        # Configure grid weights for responsive layout
        for col in range(columns):
            self.images_frame.grid_columnconfigure(col, weight=1)



def main():
    root = tk.Tk()
    app = ImageSearchApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
