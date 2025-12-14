# colors.py

# Cool Colors (Blues, Cyan, Greens)
Blue = '\033[94m'
Cyan = '\033[96m'
LightCyan = '\033[96m'  # Light Cyan for info
Green = '\033[92m'
LightGreen = '\033[92m'  # Light Green for success

# Warm Colors (Yellows, Oranges, Reds)
Yellow = '\033[38;5;226m'  # Bright Yellow for warnings
LightYellow = '\033[93m'  # Light Yellow
Orange = '\033[38;5;214m'  # Orange
Red = '\033[91m'  # Red for errors

# Accent Colors (Purples, Magentas)
Purple = '\033[95m'
Magenta = '\033[35m'  # Magenta for important notes

# Neutrals (Grey, White)
Grey = '\033[0m'  # Default
White = '\033[1m'

# Special Characters
AlertSound = '\007'

# Function to print colored text
def printcol(color, text):
    print(f'{color}{text}{Grey}')

# Function to test all colors
def test_colors():
    print("Testing Colors on Dark Background:\n")
    
    # Loop through all attributes of the `colors` module dynamically
    for color_name, color_code in globals().items():
        # Only select color variables (excluding non-color attributes)
        if not color_name.startswith('__') and isinstance(color_code, str):
            printcol(color_code, f'{color_name}')

# Run the test if the file is executed directly
if __name__ == "__main__":
    test_colors()
