"""

Other tasks

- Get rid of reliance upon --space-- at end of file

- Aggregate over a number of files, e.g. 2005-2010 (extra arguments)

- Group by metric, e.g. by week, by month (extra arguments)
-- Must check number of days in year to ensure that haven't falsely aggregated, may
	also not know which DAY to start the weekly/monthly aggregation on

Download file

"""

import sys
import urllib
import gzip
import datetime
import re

# Returns all the matching cities as a List of dictionaries
def cityFinder(city):
	url = "ftp://ftp.ncdc.noaa.gov/pub/data/gsod/ish-history.txt"
	page = urllib.urlopen(url)
	line = page.readline()
	matches = []
	loop = 0
	index = 1
	
	print '\n[STATUS] looking up cities matching "%s"' % city
	
	while (line):
		find = line.find(city.upper())
		if (find != -1):
			dict = {
				'index': index,
				'code': line[0:12],
				'name': line[13:42], 	#.strip()
				'country': line[43:45]
			}
			matches.append(dict)
			index += 1
		line = page.readline()
		loop += 1
		if (loop % 1500 == 0):
			percent = loop/30000.0*100
			sys.stdout.write("[STATUS] Percent Complete: "+str(percent)+"%\r")
	page.close()
	del page
	print "\n[STATUS] found %s matches" % len(matches)
	return matches
	
# updates the completeness of retrieving temperature for given code	
# pass true if complete a year's search
class Completeness():
	# completeness is a decimal, not percentage
	def __init__(self):
		self.years = currentYear - startYear + datetime.datetime.now().month/12.0
		self.currentYear = 0
		self.completeness = 0.0
		sys.stdout.write("[STATUS] Percent Complete: 0.0%\r")
	def update(self, pct):
		if (pct == 1.1):
			self.currentYear += 1
		if (pct <= 1.0):
			completeness = pct/self.years
			
			add = self.currentYear/self.years
			self.completeness = completeness + add
			
			# in a loop that updates "percent"
			if (self.completeness <= 1.0):
				percent = str(self.completeness*100)[0:5]
				sys.stdout.write("[STATUS] Percent Complete: "+str(percent)+"%\r")
			else:
				sys.stdout.write("[STATUS] Percent Complete: 100.0%\r")
	def updateYear(self):
		self.currentYear += 1
	
# Returns proportion of record existing for given code and year
def resultQuality(code, year, complete=None):
	url = "ftp://ftp.ncdc.noaa.gov/pub/data/gsod/%s/" % year
	page = urllib.urlopen(url)
	line = page.readline()
	tally = 0
	loop = 0
	max = 9000.0 # 12k rows in 2008, 10k in 2009
	while (line):
		line = page.readline()
		loop += 1
		find = line.find(code.split()[0]+"-"+code.split()[1])
		if (loop % 450 == 0):
			percent = loop/max
			complete.update(percent)
		if (find != -1):
			tally = 1
			complete.update(1.1)
			break
	page.close()
	return tally
	
# Returns the proportion of available years
def totalQuality(code, year):
	years = currentYear - year + 1
	tally = 0.0
	complete = Completeness()
	for i in range(years):
		tally += resultQuality(code, (year+i), complete)
	return tally/years * 100

# Outputs the list of available cities and returns the index of choice
def userChoice(city, year):	
	cities = cityFinder(city)
	
	print '\n[STATUS] Checking years available for "%s", please be patient\n' % city
	
	for city in cities:
		output = 'No.: %s | ' % city['index']
		output += 'Name: %s | ' % city['name']
		output += 'Country: %s | ' % city['country']
		output += 'Yrs Avail.: %s' % totalQuality(city['code'], year)
		output += '%'
		print output
	index = input('type the No. of the one you want and hit enter: ')
	
	for city in cities:
		if (city['index'] == index):
			return city['code']
	
# Downloads the file
def download(code):
	print "\n[STATUS] downloading the years"
	years = []
	for i in range( currentYear - startYear + 1):
		years.append( startYear + i)
	
	for year in years:
		url = "ftp://ftp.ncdc.noaa.gov/pub/data/gsod/%s/" % year
		url += code.split(' ')[0]+'-'+code.split(' ')[1]+'-'+str(year)+".op.gz"
		(localFile, headers) = urllib.urlretrieve(url, str(year)+'.op.gz')

# UnGzips the file
def ungzip():
	print "[STATUS] decompressing the years"
	years = []
	for i in range( currentYear - startYear + 1):
		years.append( startYear + i)
		
	for year in years:	
		gzFile = gzip.GzipFile(str(year)+".op.gz")
		
		localFile = open(str(year)+".op", 'wb')
		localFile.write(gzFile.read())
		
		gzFile.close()
		localFile.close()
	
# deletes the .txt and .op.gz files created earlier	
def cleanUp():
	print "[STATUS] removing the working files, leaving your weather file"
	years = []
	for i in range( currentYear - startYear + 1):
		years.append( startYear + i)
		
	import os	
	for year in years:
		os.remove(str(year)+".op.gz")
		os.remove(str(year)+".op")
	
# transforms each .op line for csv usage
def transformLine(line):
	list = line.split()
	date = list[2]
	date = date[0:4]+"/"+date[4:6]+"/"+date[6:8]
	temp = list[3]
	
	if temp[-1] == '*': # metadata
		temp = temp[:-1]
		
	max = list[-5]
	if max[-1] == '*': # metadata
		max = max[:-1]
		
	min = list[-4]
	if min[-1] == '*': # metadata
		min = min[:-1]
	
	rain = list[-3]
	if (rain == '99.99'): # metadata
		rain = '0'
		
	aChar = re.compile('[a-z]')
	if (aChar.match(rain[-1].lower())):
		rain = rain[:-1]
		
		
	snow = list[-2]
	if snow == '999.9': # metadata
		snow = '0'
	
	output = date+", "+temp+", "+max+", "+min+", "+rain+", "+snow+"\n"
	return output
	
# constructs the outputted .csv file	
def csvOutputter():
	print "[STATUS] creating .csv file"
	years = []
	for i in range( currentYear - startYear + 1):
		years.append( startYear + i)
		
	outputFile = open(city+'-weather.csv', 'w')
	outputFile.write("date, temp, max, min, rain, snow\n")

	for year in years:
		localFile = open(str(year)+".op", 'r')
		line = localFile.readline()
		line = localFile.readline()
		while line != '':
			outputLine = transformLine(line)
			outputFile.write(outputLine)
			line = localFile.readline()
		localFile.close()

# constructs the outputted .csv file
def dateChecker():
	print '[STATUS] checking missing dates'
	
	csvFile = open(city+'-weather.csv', 'r')
	line = csvFile.readline()
	line = csvFile.readline()
	
	missingDates = []
	
	date = line.split(',')[0]	
	year = int(date[0:4])
	month = int(date[5:7])
	day = int(date[8:10])
	
	lastDate = datetime.datetime(year, month, day)
	oneDay = datetime.timedelta( days = 1 )
	lastDate -= oneDay
	
	while line != '':
		date = line.split(',')[0]
		
		year = int(date[0:4])
		month = int(date[5:7])
		day = int(date[8:10])
		
		thisDate = datetime.datetime(year, month, day)
		
		if (thisDate != lastDate + oneDay):
			missingDates.append(date)
		
		lastDate = thisDate
		
		line = csvFile.readline()	
	
	csvFile.close()
	
	if missingDates:
		print '[STATUS] check the day(s) before the following %s date(s):\n' % len(missingDates)
		for date in missingDates:
			print date,


city = sys.argv[1]
startYear = int(sys.argv[2])
# format = int(sys.argv[3]) # can be either 'daily', 'weekly', or 'monthly'
currentYear = int(datetime.datetime.now().year)

def main():
	codeChoice = userChoice(city, startYear)	
	download(codeChoice)
	ungzip()
	csvOutputter()
	cleanUp()
	dateChecker()
	
	print '\n\n[STATUS] finished run, you can collect %s' % city+'-weather.csv'

# RUN the program	
main()