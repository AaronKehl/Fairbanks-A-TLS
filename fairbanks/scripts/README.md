User made tools :  
AWS:
  - syncaws: Copy scans from ~/fairbanks/scans_external to AWS S3 Bucket

GPIO:
  - scanner_poweron: Switches the GPIO pin to on.
  - scanner_poweroff: Switches the GPIO pin to off.
  - scanner_shutdown: Software shutdown for the scanner
  - scanner_status: Poll the GPIO pin.

Logs:
  - logs_split: Splits logs by month to reduce file sizes

PDAL:
  - base-laz.json: Input file for PDAL to facilitate conversion from .rxp to .laz.


Scans:
  - compress: copy/converts .rxp to .laz then compresses .rxp to .gz files.
  - frame: conducts a basic framed TLS of the terrain, then uses PDAL to look for snow.


***** See the readme.md in each directory for more information on scripts *****
