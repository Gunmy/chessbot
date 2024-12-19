import os

def get_offset(offset_file):
    """Retrieve the current offset from the offset file."""
    if os.path.exists(offset_file):
        with open(offset_file, "r") as f:
            return int(f.read().strip())
    return 0

def save_offset(offset, offset_file):
    """Save the current offset to the offset file."""
    
    with open(offset_file, "w") as f:
        f.write(str(offset))

def read_lines(file_path, start_line, num_lines):
    """Read num_lines from start_line"""

    with open(file_path, "r") as file:

        # Skip lines until start_line
        for _ in range(start_line):
            next(file, None)

        lines = [next(file, None) for _ in range(num_lines)]

    return [line for line in lines if line is not None]