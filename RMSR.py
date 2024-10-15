import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from skimage.morphology import binary_erosion, disk
from scipy.interpolate import RegularGridInterpolator
import pySPM

input_folder = '/Users/path/to/input/afm/files'
output_folder = '/Users/path/to/output/3d/surface/topography/images'
output_folder_roughness = '/Users/path/to/output/roughness/data'

os.makedirs(output_folder, exist_ok=True)

x = 'modify_value'
y = 'modify_value'
pixels_to_nm = x / y 

summary_stats = []

for subdir, _, files in os.walk(input_folder):
    print(f"Current subdir: {subdir}")
    for file in files:
        if file == '.DS_Store':
            continue
        
        image_path = os.path.join(subdir, file)
        print(f"Processing file: {image_path}")

        print(f"Loading image: {image_path}")
        image = pySPM.Bruker(image_path)
        
        height = image.get_channel("Height")

        top = height.correct_lines(inline=False)
        top = top.correct_plane(inline=False)
        top = top.filter_scars_removal(.7, inline=False)
        top = top.correct_plane(inline=False)
        top = top.correct_lines(inline=False)
        top = top.correct_plane(inline=False)

        height_data = top.pixels
        print("Height Data Shape:", height_data.shape)

        min_height = np.min(height_data)
        adjusted_height_data = height_data - min_height

        mean_height = np.mean(adjusted_height_data)
        rms_roughness = np.sqrt(np.mean((adjusted_height_data - mean_height) ** 2))

        summary_stats.append({
            'Filename': file,
            'RMS Roughness (nm)': rms_roughness
        })

        y = np.arange(height_data.shape[0]) * pixels_to_nm
        x = np.arange(height_data.shape[1]) * pixels_to_nm
        X, Y = np.meshgrid(x, y)

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        surf = ax.plot_surface(X, Y, adjusted_height_data, cmap='viridis', edgecolor='none')

        cbar = fig.colorbar(surf, ax=ax, shrink=0.4, aspect=8)
        cbar.set_label('Height (nm)')

        fig.suptitle("Name", fontsize=32, fontweight='bold', y=0.9)

        ax.set_xlabel('X (nm)')
        ax.set_ylabel('Y (nm)')
        ax.set_zlabel('Height (nm)')

        ax.view_init(elev=45, azim=30)
        ax.set_zlim(0, 1.1 * np.max(adjusted_height_data))

        output_image_path = os.path.join(output_folder, f"{os.path.splitext(file)[0]}_3D.png")
        plt.savefig(output_image_path, dpi=600, bbox_inches='tight')
        plt.close()

summary_df = pd.DataFrame(summary_stats)

xlsx_output_path = os.path.join(output_folder_roughness, '_data.xlsx')
summary_df.to_excel(xlsx_output_path, index=False)
print(f"Summary statistics saved to {xlsx_output_path}")
