Scripts involved in obtaining lidar scans or processing lidar scan files

compress:
 - Converts riegl scan files from .rxp to .laz using PDAL, preserves original files.
 - Compresses the original .rxp file into a .gz file.

frame:
 - Conducts a basic frame scan using the LidarCollect library.
 - Analyzes two spheres within the frame scan using PDAL to determine snowfall.
 - If it is snowing, it will call the line script
