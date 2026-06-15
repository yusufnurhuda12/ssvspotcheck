import os
import csv
import io
from flask import Flask, request, send_file
import simplekml

app = Flask(__name__)

@app.route('/')
def index():
    # CARA ANTI-GAGAL: Langsung baca file index.html dari root
    # Ini akan mencari index.html yang posisinya sejajar dengan app.py
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # Cadangan jika ternyata index.html ditaruh di dalam folder templates
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            return f.read()

@app.route('/generate', methods=['POST'])
def generate_kmz():
    if 'data' not in request.form:
        return 'No data provided', 400

    text_data = request.form['data']
    
    # Read TSV data
    reader = csv.reader(io.StringIO(text_data), delimiter='\t')
    rows = list(reader)

    if not rows:
        return 'Data is empty', 400

    # Parse header to find Latitude and Longitude columns
    header = rows[0]
    lat_idx = -1
    lon_idx = -1
    
    # Clean and find indices
    cleaned_header = [col.strip().lower() for col in header]
    for i, col_name in enumerate(cleaned_header):
        if 'latitude' in col_name or col_name == 'lat':
            lat_idx = i
        elif 'longitude' in col_name or col_name == 'long' or col_name == 'lon':
            lon_idx = i

    if lat_idx == -1 or lon_idx == -1:
        return 'Error: Could not find Latitude and/or Longitude columns. Please ensure they are present in the headers.', 400

    kml = simplekml.Kml()
    
    # Variables to track the last seen valid values for merging/forward-filling
    last_scenario = ""
    last_distance = ""
    last_target = ""

    # Process data rows
    for row in rows[1:]:
        if not row or len(row) <= max(lat_idx, lon_idx):
            continue
            
        # Get coordinates, replacing commas with dots for float conversion
        lat_str = row[lat_idx].replace(',', '.').strip()
        lon_str = row[lon_idx].replace(',', '.').strip()
        
        if not lat_str or not lon_str:
            continue
            
        try:
            lat = float(lat_str)
            lon = float(lon_str)
        except ValueError:
            continue # Skip invalid coordinate rows

        # Handle merged cells by forward-filling missing data
        # Assuming typical column order: Scenario (0), Distance (1), Target (2), Sector (3)
        scenario = row[0].strip() if len(row) > 0 and row[0].strip() else last_scenario
        distance = row[1].strip() if len(row) > 1 and row[1].strip() else last_distance
        target = row[2].strip() if len(row) > 2 and row[2].strip() else last_target
        sector = row[3].strip() if len(row) > 3 else ""
        
        # Update last seen values
        last_scenario = scenario
        last_distance = distance
        last_target = target

        # Construct pinpoint name
        point_name = f"{scenario} Sector {sector}" if sector else scenario
        
        # Construct description
        description = f"Distance to BTS: {distance}\nTarget: {target}"
        
        # Create pinpoint
        pnt = kml.newpoint(name=point_name, description=description, coords=[(lon, lat)])

    # Save to memory and send
    kmz_io = io.BytesIO()
    kml.savekmz(kmz_io)
    kmz_io.seek(0)
    
    return send_file(
        kmz_io,
        mimetype='application/vnd.google-earth.kmz',
        as_attachment=True,
        download_name='pinpoints.kmz'
    )

# Required by Vercel
if __name__ == '__main__':
    app.run(debug=False)
