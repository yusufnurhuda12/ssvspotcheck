import os
import csv
import io
from flask import Flask, render_template, request, send_file
import simplekml

# Explicitly define template folder path for Vercel
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__, template_folder=template_dir)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    text_data = request.form.get('data', '')
    if not text_data.strip():
        return "No data provided", 400

    lines = text_data.strip().split('\n')
    if not lines:
        return "No data provided", 400
        
    # Reconstruct rows broken by multiline cells when pasted as plain text
    max_tabs = max(line.count('\t') for line in lines)
    
    reconstructed_lines = []
    current_line = ""

    # Skip initial lines with 0 tabs to remove garbage like "TEST INFORMATION"
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

    # Now use csv.reader to parse the reconstructed lines
    reader = csv.reader(reconstructed_lines, delimiter='\t')
    rows = list(reader)

    if len(rows) < 1:
        return "Not enough data provided", 400

    # Find the header row by looking for Latitude and Longitude columns
    lat_col = None
    lon_col = None
    header_row_idx = -1
    headers = []

    for idx, row in enumerate(rows):
        temp_headers = [h.replace('\n', ' ').strip() for h in row]
        t_lat = None
        t_lon = None
        for i, h in enumerate(temp_headers):
            h_lower = h.lower()
            if 'lat' in h_lower:
                t_lat = i
            if 'lon' in h_lower or 'lng' in h_lower:
                t_lon = i
        
        if t_lat is not None and t_lon is not None:
            lat_col = t_lat
            lon_col = t_lon
            header_row_idx = idx
            headers = temp_headers
            break

    if header_row_idx == -1:
        return "Could not find Latitude and/or Longitude columns. Please ensure they are present.", 400

    kml = simplekml.Kml()
    last_values = {}

    for row_idx, row in enumerate(rows[header_row_idx + 1:], start=1):
        # Extend row if it's shorter than headers
        while len(row) < len(headers):
            row.append('')

        row_data = {}
        for i, h in enumerate(headers):
            val = row[i].strip()
            
            # Carry forward values for the first 3 columns (Scenario, Distance, Target) 
            # if they are empty, assuming merged cells in Excel
            if not val and i < 3:
                val = last_values.get(h, '')
            else:
                last_values[h] = val
                
            row_data[h] = val

        lat_str = row_data[headers[lat_col]]
        lon_str = row_data[headers[lon_col]]

        if not lat_str or not lon_str:
            continue # Skip rows without coordinates
        
        try:
            lat = float(lat_str.replace(',', '.'))
            lon = float(lon_str.replace(',', '.'))
        except ValueError:
            continue # Skip invalid coordinates

        # Create description as HTML table
        desc_html = '<table border="1" style="border-collapse: collapse;">'
        for k, v in row_data.items():
            desc_html += f'<tr><th style="padding: 5px; text-align: left;">{k}</th><td style="padding: 5px;">{v}</td></tr>'
        desc_html += '</table>'

        # Dynamically set name based on Scenario and Sector
        scenario = row_data.get(headers[0], '').strip()
        sector_val = ""
        for h in headers:
            if 'sector' in h.lower():
                sector_val = row_data.get(h, '').strip()
                break
                
        name_parts = []
        if scenario:
            name_parts.append(scenario)
        if sector_val:
            name_parts.append(f"Sector {sector_val}")
            
        if name_parts:
            name = " ".join(name_parts)
        else:
            name = f"Point {row_idx}"

        pnt = kml.newpoint(name=name, coords=[(lon, lat)]) # simplekml expects (lon, lat)
        pnt.description = desc_html
        
        # We could customize the pin style here
        pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pushpin/red-pushpin.png'

    # Save to KMZ and send
    # Generate temporary file path
    kmz_path = "output.kmz"
    kml.savekmz(kmz_path)
    
    return send_file(
        kmz_path,
        as_attachment=True,
        download_name='pinpoints.kmz',
        mimetype='application/vnd.google-earth.kmz'
    )

if __name__ == '__main__':
    # Start the application
    app.run(debug=True, host='127.0.0.1', port=5000)
