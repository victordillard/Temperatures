Simple python script to download temperatures from global temperature database on a per city basis, taking the year to start from (inclusive), not for commercial use.

Uses ftp://ftp.ncdc.noaa.gov/pub/data/gsod/ish-history.txt

Used in following way

python TempExp.py "DUBLIN" 2007

// returns list of matches for new york
// type in the number of the most promising match
// (some matches have poorer coverage)
// downloads each year in daily format, creates an output .csv
// and lists any missing dates for you to any action

// Noticed that at certain times there must be higher traffic on
// the site it relies upon, around 1pm ET and requests timeout
// however, bigger cities generally have more places where data is
// collected so there can be a wait after executing the first command
// anyway, but this problem is more prevalent for bigger cities.
// Sometimes you have to run it a couple of times for this reason

// Tested on Python 2.6 (both windows and mac)