codes.csv: codes.html
	python extract.py codes.html > codes.csv

codes.html:
	curl -o codes.html 'http://www.geonames.org/export/codes.html'

