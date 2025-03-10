import base64
import io

from PIL import Image


def print_task_screenshot_in_terminal(task, width=80):
    """
    Prints a Task's screenshot image in the terminal as simple ASCII art.

    Args:
        task (Task): The task containing a base64 encoded screenshot
        width (int): Width of the ASCII art in characters. Defaults to 80.

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

        # Use simple ASCII art - no terminal detection that might cause ioctl errors
        return simple_ascii_art(image, width)

    except Exception as e:
        print(f"Error displaying screenshot: {e}")
        return False


def simple_ascii_art(image, width=80):
    """Convert and print image as ASCII art with no terminal operations"""
    try:
        # Hard-coded safe width
        width = min(width, 100)

        # Calculate height with aspect ratio, with safety bounds
        aspect_ratio = image.height / max(1, image.width)
        height = max(1, int(width * aspect_ratio * 0.5))

        # Resize and convert to grayscale safely
        try:
            image = image.resize((width, height))
            image = image.convert("L")
        except Exception as e:
            print(f"Error resizing image: {e}")
            return False

        # Simple ASCII characters from dark to light
        chars = " .:-=+*#%@"

        # Print header
        print("\n----- Screenshot -----")

        # Generate and print ASCII art line by line
        for y in range(height):
            line = ""
            for x in range(width):
                try:
                    # Get pixel brightness (0-255)
                    brightness = image.getpixel((x, y))
                    # Map brightness to ASCII character with bounds checking
                    char_idx = min(len(chars) - 1, max(0, int(brightness / 255 * (len(chars) - 1))))
                    line += chars[char_idx]
                except Exception:
                    # If any error, just add a safe character
                    line += "."
            print(line)

        print("----- End Screenshot -----\n")
        return True
    except Exception as e:
        print(f"Error in ASCII conversion: {e}")
        return False
