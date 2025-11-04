import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import os
from boolean import search_images as boolean_search_images
from vectorielle import search_images as vector_search_images


class ImageSearchApp:
    def __init__(self, root):
        self.bg_color = "#201F1F"
        self.fg_color = "white"
        self.small_font = ("Arial", 16)
        self.large_font = ("Arial", 20, "bold")
        self.root = root
        self.root.title("TP IRI")
        self.root.geometry("1280x720")
        self.root.configure(bg=self.bg_color)
        self.images_path = "images/"
        self.photo_references = []

        title_label = tk.Label(
            root,
            text="Image Search",
            font=self.large_font,
            bg=self.bg_color,
            fg=self.fg_color,
        )
        title_label.pack(pady=10)

        search_frame = tk.Frame(root, bg=self.bg_color)
        search_frame.pack(pady=5)

        tk.Label(
            search_frame,
            text="Search:",
            font=self.small_font,
            bg=self.bg_color,
            fg=self.fg_color,
        ).pack(side=tk.LEFT, padx=5)

        self.search_entry = tk.Entry(search_frame, font=self.small_font, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", lambda e: self.perform_search())

        self.search_button = tk.Button(
            search_frame,
            text="Search",
            font=self.small_font,
            command=self.perform_search,
            bg="#3A3A3A",
            fg=self.fg_color,
            relief=tk.RAISED,
        )
        self.search_button.pack(side=tk.LEFT, padx=5)

        # Method selector (Boolean | Vectorielle | Histogram)
        method_frame = tk.Frame(root, bg=self.bg_color)
        method_frame.pack(pady=5)
        tk.Label(
            method_frame,
            text="Method:",
            font=self.small_font,
            bg=self.bg_color,
            fg=self.fg_color,
        ).pack(side=tk.LEFT, padx=5)
        self.method_var = tk.StringVar(value="boolean")
        rb_bool = tk.Radiobutton(
            method_frame,
            text="Boolean",
            variable=self.method_var,
            value="boolean",
            font=self.small_font,
            bg=self.bg_color,
            fg=self.fg_color,
            selectcolor=self.bg_color,
            activebackground=self.bg_color,
            activeforeground=self.fg_color,
        )
        rb_bool.pack(side=tk.LEFT, padx=10)
        rb_vec = tk.Radiobutton(
            method_frame,
            text="Vectorielle",
            variable=self.method_var,
            value="vectorielle",
            font=self.small_font,
            bg=self.bg_color,
            fg=self.fg_color,
            selectcolor=self.bg_color,
            activebackground=self.bg_color,
            activeforeground=self.fg_color,
        )
        rb_vec.pack(side=tk.LEFT, padx=10)

        rb_hist = tk.Radiobutton(
            method_frame,
            text="Histogram",
            variable=self.method_var,
            value="histogram",
            font=self.small_font,
            bg=self.bg_color,
            fg=self.fg_color,
            selectcolor=self.bg_color,
            activebackground=self.bg_color,
            activeforeground=self.fg_color,
        )
        rb_hist.pack(side=tk.LEFT, padx=10)

        # Histogram: choose image button (enabled only when histogram method selected)
        self.selected_hist_image = None
        self.choose_image_button = tk.Button(
            method_frame,
            text="Choose image...",
            font=self.small_font,
            command=self.choose_histogram_image,
            bg="#3A3A3A",
            fg=self.fg_color,
            relief=tk.RAISED,
            state=tk.DISABLED,
        )
        self.choose_image_button.pack(side=tk.LEFT, padx=10)

        # Toggle choose button when method changes
        self.method_var.trace_add("write", lambda *args: self._on_method_change())

        self.results_label = tk.Label(
            root,
            text="",
            font=self.small_font,
            bg=self.bg_color,
            fg=self.fg_color,
        )
        self.results_label.pack(pady=5)

        canvas_frame = tk.Frame(root, bg=self.bg_color)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.scrollbar = tk.Scrollbar(canvas_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas = tk.Canvas(
            canvas_frame,
            bg=self.bg_color,
            yscrollcommand=self.scrollbar.set,
            highlightthickness=0,
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar.config(command=self.canvas.yview)

        self.images_frame = tk.Frame(self.canvas, bg=self.bg_color)
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.images_frame, anchor="nw"
        )

        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.images_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind_all("<Button-4>", self.on_mousewheel)
        self.canvas.bind_all("<Button-5>", self.on_mousewheel)

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    def _on_method_change(self):
        method = self.method_var.get()
        if method == "histogram":
            self.choose_image_button.config(state=tk.NORMAL)
        else:
            self.choose_image_button.config(state=tk.DISABLED)
            self.selected_hist_image = None

    def choose_histogram_image(self):
        path = filedialog.askopenfilename(
            title="Select query image",
            initialdir=self.images_path,
            filetypes=[
                ("Images", "*.jpg *.jpeg *.png *.bmp *.webp *.avif"),
                ("All files", "*.*"),
            ],
        )
        if path:
            self.selected_hist_image = path
            self.results_label.config(
                text=f"Selected: {os.path.basename(path)}", fg=self.fg_color
            )

    def perform_search(self):
        method = self.method_var.get()
        query = self.search_entry.get().strip()
        # Only require a text query for boolean/vectorielle methods
        if method in ("boolean", "vectorielle") and not query:
            messagebox.showwarning("Empty Search", "Please enter search keywords!")
            return

        self.clear_results()
        scores = None
        if method == "vectorielle":
            # vectorielle returns (sorted_images, cosine_scores)
            result_images, scores = vector_search_images(query)
        elif method == "boolean":
            # boolean returns list of image filenames
            result_images = boolean_search_images(query)
        else:
            # histogram method ignores textual query; uses selected image
            if not self.selected_hist_image:
                messagebox.showwarning(
                    "Histogram", "Please choose an image for histogram search."
                )
                return
            try:
                from histogram import search_images_by_histogram

                result_images, distances = search_images_by_histogram(
                    self.selected_hist_image,
                    db_json_path="rgb_dictionary.json",
                    bins=256,
                    normalize=True,
                    metric="bhattacharyya",
                )
                # For display, pass distances as 'scores'
                scores = distances
            except Exception as e:
                messagebox.showerror(
                    "Histogram", f"Error while searching by histogram:\n{e}"
                )
                return

        if not result_images:
            if method == "histogram":
                self.results_label.config(text="No similar images found", fg="red")
            else:
                self.results_label.config(
                    text=f"No images found for '{query}'", fg="red"
                )
        else:
            if method == "vectorielle":
                suffix = " (vectorielle)"
            elif method == "boolean":
                suffix = " (boolean)"
            else:
                suffix = " (histogram)"
            self.results_label.config(
                text=f"Found {len(result_images)} image(s)" + suffix, fg=self.fg_color
            )
            self.display_images(result_images, scores)

    def clear_results(self):
        for widget in self.images_frame.winfo_children():
            widget.destroy()
        self.photo_references.clear()
        self.canvas.yview_moveto(0)

    def display_images(self, image_filenames, scores=None):
        columns = int(self.root.winfo_width() / 270)
        max_width = 250
        max_height = 250

        for idx, filename in enumerate(image_filenames):
            row = idx // columns
            col = idx % columns

            full_path = os.path.join(self.images_path, filename)
            img_frame = tk.Frame(
                self.images_frame, bg=self.bg_color, relief=tk.RIDGE, borderwidth=2
            )
            img_frame.grid(row=row, column=col, padx=10, pady=10)

            try:
                img = Image.open(full_path)
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

                photo = ImageTk.PhotoImage(img)
                self.photo_references.append(photo)

                img_label = tk.Label(img_frame, image=photo, bg=self.bg_color)
                img_label.pack(padx=5, pady=5)

                # Build label text; include score if provided
                label_text = filename
                if scores is not None and filename in scores:
                    label_text = f"{filename}  ({scores[filename]:.4f})"

                name_label = tk.Label(
                    img_frame,
                    text=label_text,
                    font=("Arial", 12),
                    bg=self.bg_color,
                    fg=self.fg_color,
                    wraplength=max_width,
                )
                name_label.pack(pady=(0, 5))
            except Exception:
                error_label = tk.Label(
                    img_frame,
                    text=f"Error: {filename}",
                    font=("Arial", 12),
                    bg=self.bg_color,
                    fg="red",
                )
                error_label.pack(padx=10, pady=10)

        for col in range(columns):
            self.images_frame.grid_columnconfigure(col, weight=1)


def main():
    root = tk.Tk()
    ImageSearchApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
