import csv

text_data = """TEST INFORMATION
Scenario	Distance 
to BTS (mtr)	Target
(Mbps)	Sector	Position	Test Location Category	Latitude	Longitude
Scenario 1	50-150	DL 315	1	Outdoor	high dense residential	-7.6194	109.0193
			2	Outdoor	high dense residential	-7.6194	109.0193
			3	Outdoor	high dense residential	-7.6194	109.0193"""

lines = text_data.split('\n')
max_tabs = max(line.count('\t') for line in lines)
print(f"Max tabs: {max_tabs}")

reconstructed_lines = []
current_line = ""

start_idx = 0
while start_idx < len(lines) and lines[start_idx].count('\t') == 0:
    start_idx += 1

for line in lines[start_idx:]:
    line = line.strip('\r')
    if current_line:
        if current_line.count('\t') + line.count('\t') <= max_tabs:
            current_line += " " + line
        else:
            reconstructed_lines.append(current_line)
            current_line = line
    else:
        current_line = line
        
if current_line:
    reconstructed_lines.append(current_line)

for i, l in enumerate(reconstructed_lines):
    print(f"R-Line {i} ({l.count('	')} tabs): {l}")
