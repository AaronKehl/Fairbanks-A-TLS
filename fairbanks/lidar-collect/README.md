Decompressing and compiling the lidarcollect.zip library from a terminal.

1. cd /home/fairbanks/fairbanks
2. cp source_location /lidar-collect.zip
3. unzip lidar-collect.zip
4. mv LidarCollect-master lidar-collect
5. rm lidar-collect.zip
6. cd lidar-collect
7. cp source location /CMakeLists.txt
8. mkdir build
9. cd build
10. cmake .. -DCMAKE_PREFIX_PATH=/home/fairbanks/fairbanks/rivlib/
11. make

**Note: To run on the Stealth LPC-835, the CMakeLists.txt file is updated to
run on a 64-bit system. The 64-bit CMakeLists.txt is included in this directory
and must be copy/pasted, overwrite, the native CMakeLists.txt file provided when
unpacking the lidarcollect.zip.  If it has been overwritten, line 54 will read:
set_target_properties(LidarCollect PROPERTIES COMPILE_FLAGS "-m64" LINK_FLAGS "-m64")


Requires libLas, which requires libboost-all-dev and libgeotiff-dev.
