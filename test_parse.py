import csv
import io

text_data = """TEST INFORMATION
Scenario	Distance 
to BTS (mtr)	Target
(Mbps)	Sector	Position	Test Location Category	Latitude	Longitude
Scenario 1	50-150	DL 315	1	Outdoor	high dense residential	-7.6194	109.0193
			2	Outdoor	high dense residential	-7.6194	109.0193
			3	Outdoor	high dense residential	-7.6194	109.0193"""

reader = csv.reader(io.StringIO(text_data.strip()), delimiter='\t')
rows = list(reader)

for i, r in enumerate(rows):
    print(f"Row {i}: {r}")
