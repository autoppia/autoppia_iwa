import base64
import io
from PIL import Image
import sys
import os


def print_task_screenshot_in_terminal(task, width=80):
    """
    Prints a Task's screenshot image in the terminal as ASCII art.

    Args:
        task (Task): The task containing a base64 encoded screenshot
        width (int, optional): Width of the terminal output in characters. Defaults to 80.

    Returns:
        bool: True if successful, False if there was an error.
    """
    if not task.screenshot:
        print("No screenshot available in this task.")
        return False

    try:
        # Decode the base64 string to bytes
        img_bytes = base64.b64decode(task.screenshot)

        # Create a PIL Image from bytes
        image = Image.open(io.BytesIO(img_bytes))

        # Just use ASCII art for reliability
        return print_as_ascii_art(image, width)

    except Exception as e:
        print(f"Error displaying screenshot: {e}")
        return False


def has_terminal_image_support():
    """Check if terminal supports direct image display via libraries like iTerm2"""
    try:
        # Check for iterm2 or kitty terminal
        import importlib.util
        if importlib.util.find_spec("iterm2_tools") is not None:
            return True
        if importlib.util.find_spec("kitty.graphics") is not None:
            return True
        return False
    except:
        return False


def display_with_terminal_image(image):
    """Display image in terminal using appropriate tools if available"""
    try:
        import importlib

        # Try iterm2
        if importlib.util.find_spec("iterm2_tools") is not None:
            from iterm2_tools.images import display_image_bytes
            with io.BytesIO() as buffer:
                image.save(buffer, format="PNG")
                display_image_bytes(buffer.getvalue())
                return True

        # Try kitty
        if importlib.util.find_spec("kitty.graphics") is not None:
            from kitty.graphics import display_image
            with io.BytesIO() as buffer:
                image.save(buffer, format="PNG")
                display_image(buffer.getvalue())
                return True

        return False
    except Exception as e:
        print(f"Error using terminal image tools: {e}")
        return False


def print_as_ascii_art(image, width=80):
    """Convert and print image as ASCII art"""
    try:
        # Ensure width is positive
        width = max(10, min(width, 200))

        # Resize the image to fit terminal width
        height = max(1, int(image.height * width / image.width / 2))  # Adjust for character aspect ratio
        image = image.resize((width, height))

        # Convert to grayscale for ASCII art
        image = image.convert("L")

        # Define ASCII characters from dark to light
        chars = " .:-=+*#%@"

        # Generate and print ASCII art
        print("\nScreenshot (ASCII representation):")
        for y in range(height):
            line = ""
            for x in range(width):
                # Get pixel brightness (0-255)
                brightness = image.getpixel((x, y))
                # Map brightness to ASCII character
                char_index = min(int(brightness / 255 * (len(chars) - 1)), len(chars) - 1)
                line += chars[char_index]
            print(line)

        return True
    except Exception as e:
        print(f"Error converting to ASCII: {e}")
        return False
