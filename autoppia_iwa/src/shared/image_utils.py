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
