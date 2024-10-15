# RMSR.py
This Python script processes atomic force microscopy (AFM) data to generate 3D topography visualizations and calculate surface roughness metrics. It reads .spm files, corrects height data, and produces high-resolution images of the surface topography along with root mean square roughness values saved in an Excel file. 

Script was utilized to process data for the following manuscript: Chibrikov, V., Pieczywek, P. M., Cybulska, J., & Zdunek, A. (2024). The effect of hemicelluloses on biosynthesis, structure and mechanical performance of bacterial cellulose-hemicellulose hydrogels. Scientific Reports, 14(1), 21671. https://doi.org/10.1038/s41598-024-72513-w

- Visual Studio Code release used: 1.93.1
- Python release used: 3.12.4. 64-bit
> Warning! There are no guaranties this code will run on your machine.

## Features
- AFM data processing: script corrects and filters height data from AFM .spm files, including line correction, plane correction, and scar removal
- 3D visualization: script generates 3D surface topography plots using matplotlib
- Automatic output management: script creates output directories for images and roughness data, saving results in user-specified locations.
- Root mean square roughness calculation: script computes and saves root mean square roughness statistics to an Excel file for each processed AFM file.

## Dependencies
The following Python packages are required:
- numpy
- pandas
- matplotlib
- scipy
- pySPM
- scikit-image

## Parameters
- input_folder: path to the folder containing AFM .spm files.
- output_folder: directory where the generated 3D topography images will be saved.
- output_folder_roughness: directory where the calculated roughness data will be saved.
- pixels_to_nm: conversion factor from pixels to nanometers. Conversion factor is calculated as x/y, where x is image height/width, and y is a number of pixels per image length/height

## Description
The script is structured into several key blocks, as detailed below:

### Library imports and setup
This section imports the necessary libraries, including pySPM for handling AFM data, numpy and pandas for data manipulation, and matplotlib for visualization. It also defines paths for input files and output locations. 
```
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
 ```

### Processing AFM data and correcting height information
Code snippet iterates through the AFM files, applying corrections to the height data, such as line and plane corrections, and adjusts for minimum height to ensure accurate topography representation.
```
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
 ```

### Root mean square roughness calculation
Code calculates the root mean square roughness of the corrected height data, providing a measure of the surface's texture.
```
        mean_height = np.mean(adjusted_height_data)
        rms_roughness = np.sqrt(np.mean((adjusted_height_data - mean_height) ** 2))
        summary_stats.append({
            'Filename': file,
            'RMS Roughness (nm)': rms_roughness
        })
 ```

### 3D topography visualization
Code generates a 3D surface plot for each processed AFM image using matplotlib and saves the resulting images to the specified output directory.
```
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

 ```

### Saving roughness results
Code snippet compiles root mean square roughness data into a Pandas DataFrame and exports it to an Excel file.
```
summary_df = pd.DataFrame(summary_stats)

xlsx_output_path = os.path.join(output_folder_roughness, '_data.xlsx')
summary_df.to_excel(xlsx_output_path, index=False)
print(f"Summary statistics saved to {xlsx_output_path}")
 ```

## License
This project is licensed under the MIT License. See LICENSE file.
