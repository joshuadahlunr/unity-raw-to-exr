import sys
import os
from pathlib import Path
import math
import numpy as np
import imageio


def raw_to_exr(raw_file_name, exr_file_name = None):
    # Define the Maximum Value for a C# short
    max_short = 32767  # 65535

    # Initialize the Minimum and Maximum Height Tracking Variables
    min_value = max_short
    max_value = -1

    # Initialize the array of Height Data
    height_data = []

    # Open the RAW file as a Binary File
    file = open(raw_file_name, "rb")  # 'rb' - Opens the file in Binary Mode

    # Since the data in the RAW file is 16-Bit and each byte is 8-bits:  Read 2 bytes of data
    sixteen_bits = file.read(2)

    # Continue to loop until sixteen_bits is empty
    while sixteen_bits:
        # Convert the data in sixteen_bits to an integer, knowing that the RAW file is encoded using little endian
        short_value = int.from_bytes(sixteen_bits, byteorder="little")

        # Normalize the short_value by dividing by the maximum value of a short
        float_value_of_height = short_value / max_short

        # Identify and record the Minimum and Maximum values of float_value_of_height
        if float_value_of_height < min_value:
            min_value = float_value_of_height
        if float_value_of_height > max_value:
            max_value = float_value_of_height

        # Add this value to the height_data
        height_data.append(float_value_of_height)

        # Read 2 more bytes
        sixteen_bits = file.read(2)

    # Assuming that the RAW Image is square, both the row length and the column height will be
    # the square-root of the length of the height_data
    row_length = int(math.sqrt(len(height_data)))

    # Reshape the height_data from a flat array into a 2-dimensional array and save it to exr_data
    exr_data = np.array(height_data).reshape(row_length, row_length)

    # make sure that the data in the exr_data array is float32
    exr_data = exr_data.astype("float32")

    # Define the name of the EXR file
    if exr_file_name is None:
        exr_file_name = Path(raw_file_name).with_suffix(".exr")

    # Print out some statistics
    print("Minimum Height: %s  -  Maximum Height: %s  -  Number Of Points: %s  -  Image Shape: %s  -  EXR File: %s" %
          (min_value, max_value, len(height_data), exr_data.shape, exr_file_name))

    # Save the exr_data to an EXR file
    imageio.v2.imwrite(exr_file_name, exr_data)

def exr_to_raw(exr_file_name, raw_file_name = None):
    # Load the EXR data from the file
    exr_data = imageio.v2.imread(exr_file_name)

    if len(exr_data.shape) == 3:
        print("WARNING: EXR image encoded as RGB, converting only the red channel!")
        exr_data = exr_data[:, :, 0]

    # Flatten the 2D array to a 1D array of normalized float values
    height_data = exr_data.flatten()

    # Define the Maximum Value for a C# short
    max_short = 32767  # 65535

    # Define the name of the RAW file
    if raw_file_name is None:
        raw_file_name = Path(exr_file_name).with_suffix(".raw")

    # Open the RAW file for writing in binary mode
    with open(raw_file_name, "wb") as file:
        # Loop through each normalized float value in height_data
        for float_value in height_data:
            # Convert the normalized float value to a short value
            short_value = int(float_value * max_short)

            # Convert the short value to bytes in little-endian format
            byte_data = short_value.to_bytes(2, byteorder="little")

            # Write the byte data to the RAW file
            file.write(byte_data)

    # Print out some statistics
    min_value = int(np.min(height_data) * max_short)
    max_value = int(np.max(height_data) * max_short)
    num_points = len(height_data)
    image_shape = exr_data.shape
    print("Minimum Height: %s  -  Maximum Height: %s  -  Number Of Points: %s  -  Image Shape: %s  -  RAW File: %s" %
          (min_value, max_value, num_points, image_shape, raw_file_name))


if __name__ == '__main__':
    # If freeimage is not on this computer, download it
    imageio.plugins.freeimage.download()

    # If there is no argument for the RAW file, exit with an error
    if len(sys.argv) != 2:
        sys.exit("No Input File")

    # Get the input_file_name from the command-line arguments
    input_file_name = Path(sys.argv[1])

    # If the input_file_name does not exist, exit with an error
    if not input_file_name.exists():
        sys.exit("%s does not exist" % input_file_name)


    if input_file_name.suffix in [".raw", ".r16"]:
        # Convert the input_file_name from RAW to EXR
        raw_to_exr(input_file_name)
    elif input_file_name.suffix in [".exr"]:
        # Convert the input_file_name from EXR to RAW
        exr_to_raw(input_file_name)
    else: sys.exit("Input file must be a .raw/.r16 or a .exr")
