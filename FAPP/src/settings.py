# ---------------------------------------
#  TTK & Window Settings
# ---------------------------------------
TTK_THEME = "darkly"  # You can switch to "cyborg", "superhero", "solar", etc.

APP_BG_COLOR = "#2e2e2e"   # Main window background color
RIGHT_PANEL_BG = "#2e2e2e" # Right-side panel color
TEXT_WIDGET_BG = "#3c3c3c" # Background for the text-entry widget
TEXT_WIDGET_FG = "#ffffff" # Text color for the text-entry widget
TEXT_WIDGET_FONT = ("Helvetica", 14)

# ---------------------------------------
#  Post / Preview Settings
# ---------------------------------------
POST_SIZE = (1080, 1080)                 # The final post image size
PREVIEW_DISPLAY_SIZE = (500, 500)        # The preview area size
PREVIEW_BORDER_COLOR = "#ffffff"
PREVIEW_BORDER_WIDTH = 2

# ---------------------------------------
#  Background Mode
#    "color" => Solid color background
#    "image" => Use an image file
# ---------------------------------------
BACKGROUND_MODE = "color"
BACKGROUND_COLOR = "#ffffff"             # If BACKGROUND_MODE == "color"
BACKGROUND_IMAGE_PATH = "my_bg.jpg"      # If BACKGROUND_MODE == "image"

# ---------------------------------------
#  Quote Settings
# ---------------------------------------
QUOTE_COLOR = "#111111"
QUOTE_FONT_SIZE = 48
QUOTE_ALIGN = "center"  # "left", "center", or "right"

# For PIL fonts, specify a TrueType font file.
FONT_PATH = "arial.ttf"

# Padding around the quote text
QUOTE_PADDING_TOP = 100
QUOTE_PADDING_BOTTOM = 100
QUOTE_PADDING_LEFT = 100
QUOTE_PADDING_RIGHT = 100

# ---------------------------------------
#  Signature Settings
# ---------------------------------------
SIGNATURE_TEXT = "- Stay Motivated"
SIGNATURE_COLOR = "#111111"
SIGNATURE_FONT_SIZE = 24

# Signature anchor: choose one of
#  "top_left", "top_right", "bottom_left", "bottom_right"
SIGNATURE_ANCHOR = "bottom_right"

# Margins from each side for the signature text
SIGNATURE_MARGIN_TOP = 20
SIGNATURE_MARGIN_BOTTOM = 20
SIGNATURE_MARGIN_LEFT = 20
SIGNATURE_MARGIN_RIGHT = 20
