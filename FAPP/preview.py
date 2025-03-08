# preview.py

import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os
import datetime

from settings import (
    # Window & preview
    POST_SIZE,
    PREVIEW_DISPLAY_SIZE,
    PREVIEW_BORDER_COLOR,
    PREVIEW_BORDER_WIDTH,

    # Background
    BACKGROUND_MODE,
    BACKGROUND_COLOR,
    BACKGROUND_IMAGE_PATH,

    # Quote
    QUOTE_COLOR,
    QUOTE_FONT_SIZE,
    QUOTE_ALIGN,
    FONT_PATH,
    QUOTE_PADDING_TOP,
    QUOTE_PADDING_BOTTOM,
    QUOTE_PADDING_LEFT,
    QUOTE_PADDING_RIGHT,

    # Signature
    SIGNATURE_TEXT,
    SIGNATURE_COLOR,
    SIGNATURE_FONT_SIZE,
    SIGNATURE_ANCHOR,
    SIGNATURE_MARGIN_TOP,
    SIGNATURE_MARGIN_BOTTOM,
    SIGNATURE_MARGIN_LEFT,
    SIGNATURE_MARGIN_RIGHT,
)

class PreviewFrame(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        # The frame size includes border space
        self.config(
            width=PREVIEW_DISPLAY_SIZE[0] + 2 * PREVIEW_BORDER_WIDTH,
            height=PREVIEW_DISPLAY_SIZE[1] + 2 * PREVIEW_BORDER_WIDTH,
            bg=PREVIEW_BORDER_COLOR,
        )
        self.pack_propagate(False)

        # Canvas to display the scaled image (no border)
        self.canvas = tk.Canvas(
            self,
            width=PREVIEW_DISPLAY_SIZE[0],
            height=PREVIEW_DISPLAY_SIZE[1],
            highlightthickness=0
        )
        self.canvas.pack(padx=PREVIEW_BORDER_WIDTH, pady=PREVIEW_BORDER_WIDTH)

        self.quote_text = ""
        self.photo_image = None  # Keep a reference to avoid GC
        self.update_preview_image()

    def generate_post_image(self):
        """
        Generate the full-size (1080x1080) PIL image with the chosen background,
        quote text, and signature text.
        """
        # 1. Create the background
        if BACKGROUND_MODE == "image":
            # Load the background image, resize it to POST_SIZE
            bg = Image.open(BACKGROUND_IMAGE_PATH).convert("RGB")
            bg = bg.resize(POST_SIZE, Image.LANCZOS)
            image = bg
        else:
            # Solid color background
            image = Image.new("RGB", POST_SIZE, BACKGROUND_COLOR)

        draw = ImageDraw.Draw(image)

        # 2. Load fonts
        try:
            quote_font = ImageFont.truetype(FONT_PATH, QUOTE_FONT_SIZE)
        except Exception:
            quote_font = ImageFont.load_default()

        try:
            signature_font = ImageFont.truetype(FONT_PATH, SIGNATURE_FONT_SIZE)
        except Exception:
            signature_font = ImageFont.load_default()

        # 3. Draw the quote
        text = self.quote_text
        # We'll start by computing the bounding box if we draw the text at (0,0)
        # so we can figure out how big it is.
        temp_bbox = draw.multiline_textbbox((0, 0), text, font=quote_font, align=QUOTE_ALIGN)
        text_width = temp_bbox[2] - temp_bbox[0]
        text_height = temp_bbox[3] - temp_bbox[1]

        # Decide the x-coordinate based on alignment
        if QUOTE_ALIGN.lower() == "center":
            x = (POST_SIZE[0] - text_width) / 2
        elif QUOTE_ALIGN.lower() == "right":
            x = POST_SIZE[0] - QUOTE_PADDING_RIGHT - text_width
        else:
            # left
            x = QUOTE_PADDING_LEFT

        # For y, we simply respect QUOTE_PADDING_TOP
        y = QUOTE_PADDING_TOP

        # Ensure we don't exceed the bottom limit (in case of large text).
        # But typically, you'd handle that by resizing fonts or adjusting padding.
        # For now, let's assume there's enough space.
        draw.multiline_text(
            (x, y),
            text,
            fill=QUOTE_COLOR,
            font=quote_font,
            align=QUOTE_ALIGN
        )

        # 4. Draw the signature
        sig_bbox = draw.textbbox((0, 0), SIGNATURE_TEXT, font=signature_font)
        sig_width = sig_bbox[2] - sig_bbox[0]
        sig_height = sig_bbox[3] - sig_bbox[1]

        # We'll place it based on SIGNATURE_ANCHOR
        if SIGNATURE_ANCHOR == "bottom_right":
            sig_x = POST_SIZE[0] - sig_width - SIGNATURE_MARGIN_RIGHT
            sig_y = POST_SIZE[1] - sig_height - SIGNATURE_MARGIN_BOTTOM
        elif SIGNATURE_ANCHOR == "bottom_left":
            sig_x = SIGNATURE_MARGIN_LEFT
            sig_y = POST_SIZE[1] - sig_height - SIGNATURE_MARGIN_BOTTOM
        elif SIGNATURE_ANCHOR == "top_right":
            sig_x = POST_SIZE[0] - sig_width - SIGNATURE_MARGIN_RIGHT
            sig_y = SIGNATURE_MARGIN_TOP
        else:  # top_left
            sig_x = SIGNATURE_MARGIN_LEFT
            sig_y = SIGNATURE_MARGIN_TOP

        draw.text(
            (sig_x, sig_y),
            SIGNATURE_TEXT,
            fill=SIGNATURE_COLOR,
            font=signature_font
        )

        return image

    def update_preview_image(self):
        """Update the preview canvas with a scaled version of the post image."""
        image = self.generate_post_image()
        preview_image = image.resize(PREVIEW_DISPLAY_SIZE, Image.LANCZOS)
        self.photo_image = ImageTk.PhotoImage(preview_image)

        # Clear the canvas and draw the new image
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo_image)

    def update_quote(self, new_quote):
        self.quote_text = new_quote
        self.update_preview_image()

    def clear(self):
        self.quote_text = ""
        self.update_preview_image()

    def save_post(self):
        """Save the full-size post image to the 'posts' folder as a PNG file."""
        image = self.generate_post_image()
        # Make sure we have a 'posts' folder
        posts_dir = os.path.join(os.getcwd(), "posts")
        if not os.path.exists(posts_dir):
            os.makedirs(posts_dir)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(posts_dir, f"post_{timestamp}.png")
        image.save(filename)
        return filename
