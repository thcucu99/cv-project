from PIL import Image
import numpy as np
import os


def create_obstructed_images(image_path, output_dir):
    # Load the image
    img = Image.open(image_path)
    width, height = img.size

    # Define the quarters
    quarters = [(0, 0, width // 2, height // 2),  # top-left
                (width // 2, 0, width, height // 2),  # top-right
                (0, height // 2, width // 2, height),  # bottom-left
                (width // 2, height // 2, width, height)]  # bottom-right

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Generate the 16 combinations
    for i in range(16):  # There are 2^4 = 16 combinations
        copy_img = img.copy()
        pixels = copy_img.load()
        name_suffix = ''

        for j in range(4):
            if (i >> j) & 1:  # Check if the j-th bit is set
                for x in range(quarters[j][0], quarters[j][2]):
                    for y in range(quarters[j][1], quarters[j][3]):
                        pixels[x, y] = (128, 128, 128)  # Grey out this quarter
                name_suffix += 'x'
            else:
                name_suffix += str(j+1)
        # Save the modified image
        base_name = image_path.split('/')[-1].split('.')[0]
        copy_img.save(os.path.join(output_dir, f'{base_name}_{name_suffix}.png'))


# Example usage:
create_obstructed_images('images/original/image_95.png', 'images/all_images')

