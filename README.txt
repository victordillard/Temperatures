Simple python script to download temperatures from global temperature database on a per city basis, taking the year to start from (inclusive).

Not for commercial use.

Uses ftp://ftp.ncdc.noaa.gov/pub/data/gsod/ish-history.txt

Used in following way

python TempExp.py "DUBLIN" 2007

then follow the instructions.

More likely that the request times out the further back in time one goes and the bigger the city (more temperature data sources = more requests).