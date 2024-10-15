import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from skimage.morphology import binary_erosion, disk
from scipy.interpolate import RegularGridInterpolator
import pySPM

# Set the input and output directories
input_folder = '/Users/vadymchibrikov/Desktop/ARTYKUL_4_THE_EFFECT_OF_HEMICELLULOSE_SPECIFIC_ENZYMES/DANE/BC_COMPOSITE_ROUGHNESS/INPUT/RAW/BC'
output_folder = '/Users/vadymchibrikov/Desktop/ARTYKUL_4_THE_EFFECT_OF_HEMICELLULOSE_SPECIFIC_ENZYMES/DANE/BC_COMPOSITE_ROUGHNESS/OUTPUT/3D/RAW'
output_folder_roughness = '/Users/vadymchibrikov/Desktop/ARTYKUL_4_THE_EFFECT_OF_HEMICELLULOSE_SPECIFIC_ENZYMES/DANE/BC_COMPOSITE_ROUGHNESS/OUTPUT/ROUGHNESS'


# Ensure the output directory exists
os.makedirs(output_folder, exist_ok=True)

# Conversion factor from pixels to nanometers
pixels_to_nm = 2000 / 1024  # 2000 nm / 1024 pixels

# List to store summary statistics
summary_stats = []

for subdir, _, files in os.walk(input_folder):
    print(f"Current subdir: {subdir}")
    for file in files:
        # Skip .DS_Store files
        if file == '.DS_Store':
            continue
        
        image_path = os.path.join(subdir, file)
        print(f"Processing file: {image_path}")

        print(f"Loading image: {image_path}")
        image = pySPM.Bruker(image_path)
        
        height = image.get_channel("Height")

        # Correcting and processing the image
        top = height.correct_lines(inline=False)
        top = top.correct_plane(inline=False)
        top = top.filter_scars_removal(.7, inline=False)
        top = top.correct_plane(inline=False)
        top = top.correct_lines(inline=False)
        top = top.correct_plane(inline=False)

        # Extract the height data
        height_data = top.pixels
        print("Height Data Shape:", height_data.shape)

        # Adjust height data so the minimum value is 0
        min_height = np.min(height_data)
        adjusted_height_data = height_data - min_height

        # Calculate RMS roughness
        mean_height = np.mean(adjusted_height_data)
        rms_roughness = np.sqrt(np.mean((adjusted_height_data - mean_height) ** 2))

        # Append summary statistics
        summary_stats.append({
            'Filename': file,
            'RMS Roughness (nm)': rms_roughness
        })

        # Create a meshgrid for X and Y coordinates scaled to nanometers
        y = np.arange(height_data.shape[0]) * pixels_to_nm
        x = np.arange(height_data.shape[1]) * pixels_to_nm
        X, Y = np.meshgrid(x, y)

        # Plotting in 3D
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        surf = ax.plot_surface(X, Y, adjusted_height_data, cmap='viridis', edgecolor='none')

        # Adding a colorbar with adjusted size
        cbar = fig.colorbar(surf, ax=ax, shrink=0.4, aspect=8)
        cbar.set_label('Height (nm)')

        # Centered bold title closer to the plot
        fig.suptitle("BC Raw", fontsize=32, fontweight='bold', y=0.9)

        ax.set_xlabel('X (nm)')
        ax.set_ylabel('Y (nm)')
        ax.set_zlabel('Height (nm)')

        # Rotate the view (You can adjust the angles as needed)
        ax.view_init(elev=45, azim=30)  # Rotate around X and Y axes
        ax.set_zlim(0, 1.1 * np.max(adjusted_height_data))  # Set Z-axis limit for better visualization

        # Save the plot with high resolution (600 ppi)
        output_image_path = os.path.join(output_folder, f"{os.path.splitext(file)[0]}_3D.png")
        plt.savefig(output_image_path, dpi=600, bbox_inches='tight')
        plt.close()  # Close the plot to free up memory

# Convert summary statistics to a DataFrame
summary_df = pd.DataFrame(summary_stats)

# # Save the DataFrame to an Excel file
# xlsx_output_path = os.path.join(output_folder_roughness, 'BCRAW.xlsx')
# summary_df.to_excel(xlsx_output_path, index=False)
# print(f"Summary statistics saved to {xlsx_output_path}")
