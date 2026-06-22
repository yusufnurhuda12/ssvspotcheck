import os
import csv
import io
from flask import Flask, render_template, request, send_file
import simplekml

# Explicitly define template folder path for Vercel Serverless
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

    # Gunakan csv.reader asli bawaan Python yang pintar meng-handle multiline cell dari Excel
    reader = csv.reader(io.StringIO(text_data.strip()), delimiter='\t')
    rows = list(reader)

    if not rows:
        return "No data provided", 400

    # Find the header row by looking for Latitude and Longitude columns dynamically
    # Look through the first 10 rows in case there are title rows
    header_idx = -1
    lat_col = -1
    lon_col = -1
    
    for i, row in enumerate(rows[:10]):
        cleaned_row = [str(col).strip().lower() for col in row]
        temp_lat = -1
        temp_lon = -1
        for j, col_name in enumerate(cleaned_row):
            if 'latitude' in col_name or col_name == 'lat':
                temp_lat = j
            elif 'longitude' in col_name or col_name == 'long' or col_name == 'lon':
                temp_lon = j
                
        if temp_lat != -1 and temp_lon != -1:
            header_idx = i
            lat_col = temp_lat
            lon_col = temp_lon
            break

    if header_idx == -1 or lat_col == -1 or lon_col == -1:
        return 'Error: Could not find Latitude and/or Longitude columns. Please ensure you copied the table headers.', 400

    headers = [str(h).replace('\n', ' ').strip() for h in rows[header_idx]]
    kml = simplekml.Kml()
    last_values = {}

    # Process data rows starting AFTER the header row
    for row_idx, row in enumerate(rows[header_idx + 1:], start=1):
        if not row:
            continue
            
        # Extend row if it's shorter than headers
        while len(row) < len(headers):
            row.append('')

        row_data = {}
        for i, h in enumerate(headers):
            val = str(row[i]).strip()
            
            # Carry forward values for the first 3 columns (Scenario, Distance, Target) 
            # if they are empty, assuming merged cells in Excel
            if not val and i < 3:
                val = last_values.get(h, '')
            else:
                last_values[h] = val
                
            row_data[h] = val

        lat_str = row_data.get(headers[lat_col], '')
        lon_str = row_data.get(headers[lon_col], '')

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

    import tempfile
    
    # Generate temporary file path
    temp_dir = tempfile.gettempdir()
    kmz_path = os.path.join(temp_dir, "output.kmz")
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
