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
    # Dapatkan lokasi absolut folder tempat app.py ini berada
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Buat jalur pasti ke file index.html
    root_path = os.path.join(base_dir, 'index.html')
    template_path = os.path.join(base_dir, 'templates', 'index.html')
    
    try:
        if os.path.exists(root_path):
            with open(root_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return f"Error: Tidak bisa menemukan file index.html di {root_path} maupun {template_path}"
    except Exception as e:
        return f"Server Error: {str(e)}"

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

    # Cari baris judul (header) secara dinamis sampai maksimal 10 baris ke bawah
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
        return 'Error: Could not find Latitude and/or Longitude columns. Pastikan baris nama kolom (Latitude/Longitude) ikut di-copy ya.', 400

    headers = [str(h).replace('\n', ' ').strip() for h in rows[header_idx]]
    kml = simplekml.Kml()
    last_values = {}

    # Proses data mulai dari baris di bawah header
    for row_idx, row in enumerate(rows[header_idx + 1:], start=1):
        if not row:
            continue
            
        # Perpanjang row jika lebih pendek dari headers
        while len(row) < len(headers):
            row.append('')

        row_data = {}
        for i, h in enumerate(headers):
            val = str(row[i]).strip()
            
            # Bawa nilai dari baris sebelumnya untuk 3 kolom pertama (Scenario, dsb)
            # Ini sangat berguna jika ada Merge Cell di Excel
            if not val and i < 3:
                val = last_values.get(h, '')
            else:
                last_values[h] = val
                
            row_data[h] = val

        # Ambil Latitude dan Longitude dengan aman
        lat_str = row_data.get(headers[lat_col], '')
        lon_str = row_data.get(headers[lon_col], '')

        if not lat_str or not lon_str:
            continue # Lewati jika kosong
        
        try:
            lat = float(lat_str.replace(',', '.'))
            lon = float(lon_str.replace(',', '.'))
        except ValueError:
            continue # Lewati jika bukan angka koordinat yang valid

        # Buat tampilan deskripsi tabel HTML saat pin di-klik
        desc_html = '<table border="1" style="border-collapse: collapse;">'
        for k, v in row_data.items():
            desc_html += f'<tr><th style="padding: 5px; text-align: left;">{k}</th><td style="padding: 5px;">{v}</td></tr>'
        desc_html += '</table>'

        # Penamaan Pin Point otomatis
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

        # Buat Pin
        pnt = kml.newpoint(name=name, coords=[(lon, lat)]) 
        pnt.description = desc_html
        pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pushpin/red-pushpin.png'

    # Simpan KMZ dan kirim
    kmz_io = io.BytesIO()
    kml.savekmz(kmz_io)
    kmz_io.seek(0)
    
    return send_file(
        kmz_io,
        mimetype='application/vnd.google-earth.kmz',
        as_attachment=True,
        download_name='pinpoints.kmz'
    )

if __name__ == '__main__':
    app.run(debug=False)
