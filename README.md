# LOLA Processing
This codebase is used for downloading and processing LOLA RDRs to get spacecraft clock, altitude, longitude, latitude, and detector ID for non-flagged measurements, as well as the spacecraft clock, longitude, latitude, and detector ID for all measurements regardless of flag.

rdr2tab is from the LOLA RDR Software provided by the LOLA Science Team.

To download all the .DAT files for a specific subdirectory, run DownloadIndividualSubdir.py. Change the folder name in line 7 to specify the subdirectory.

To process the downloaded .DAT files, execute process_rdr_w_txt.bat. This application utilizes rdr2tab from the LOLA RDR software to process the files and creates/adds to a .txt file listing all the .DAT files that have been processed.

To analyze the processed files, run analyzeLOLA.py. Change DataSetName in line 6 to match the folder name. This saves the non-flagged data, the groundtracks of all data, and non-flagged pole data (lat ≥ 80° and lat ≤ −80°) as .gzip files. Every 50 data points, intermediate plots showing the valid data and the ground tracks will be saved. Final plots showing the ground tracks, elevation contour, and distribution of valid data points are generated at the end.
