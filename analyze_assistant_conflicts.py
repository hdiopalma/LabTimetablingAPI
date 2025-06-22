import os
import django
import pandas as pd
import plotly.express as px
from datetime import datetime
from collections import defaultdict

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LabTimetablingAPI.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "True"
django.setup()

from scheduling_data.models import Assistant

# Konfigurasi direktori
DIR_PATH = 'experiment_results/latest_result'
EXCEL_PATH = os.path.join(DIR_PATH, 'jadwal_praktikum.xlsx')
REPORT_PATH = os.path.join(DIR_PATH, 'konflik_jadwal_asisten.html')

# Buat direktori jika belum ada
os.makedirs(DIR_PATH, exist_ok=True)

# Baca file Excel
df = pd.read_excel(EXCEL_PATH)

# Konversi tipe data
df['Date'] = pd.to_datetime(df['Date'])
df['DayName'] = df['Date'].dt.day_name()

# Fungsi untuk memeriksa konflik jadwal
def detect_schedule_conflicts(df):
    # Ambil semua asisten dari database
    assistants = Assistant.objects.all()
    assistant_schedules = {assistant.name: assistant.regular_schedule for assistant in assistants}
    
    conflicts = []
    conflict_details = []
    
    # Mapping hari Indonesia ke Inggris (jika diperlukan)
    day_mapping = {
        'Monday': 'Senin',
        'Tuesday': 'Selasa',
        'Wednesday': 'Rabu',
        'Thursday': 'Kamis',
        'Friday': 'Jumat',
        'Saturday': 'Sabtu',
        'Sunday': 'Minggu'
    }
    
    # Balik mapping untuk konversi dari Indonesia ke Inggris
    reverse_day_mapping = {v: k for k, v in day_mapping.items()}
    
    for _, row in df.iterrows():
        assistant_name = row['Assistant']
        shift = row['Shift']
        day_name = row['DayName']
        
        # Konversi nama hari jika perlu
        english_day = reverse_day_mapping.get(day_name, day_name)
        
        # Dapatkan jadwal asisten
        schedule = assistant_schedules.get(assistant_name)
        
        # print(f"Memeriksa konflik untuk asisten: {assistant_name}, Shift: {shift}, Hari: {day_name}")
        
        if not schedule:
            conflicts.append({
                'Date': row['Date'],
                'Assistant': assistant_name,
                'Shift': shift,
                'Day': day_name,
                'Conflict_Reason': 'Jadwal reguler tidak ditemukan',
                'Chapter': row['Chapter'],
                'Group': row['Group']
            })
            continue
        
        # Periksa ketersediaan di jadwal reguler
        day_schedule = schedule.get(english_day)
        if not day_schedule:
            conflicts.append({
                'Date': row['Date'],
                'Assistant': assistant_name,
                'Shift': shift,
                'Day': day_name,
                'Conflict_Reason': f'Hari {english_day} tidak ada di jadwal reguler',
                'Chapter': row['Chapter'],
                'Group': row['Group']
            })
            continue
        
        # Periksa shift spesifik
        available = day_schedule.get(shift)
        if available is None:
            conflicts.append({
                'Date': row['Date'],
                'Assistant': assistant_name,
                'Shift': shift,
                'Day': day_name,
                'Conflict_Reason': f'Shift {shift} tidak ada di jadwal reguler',
                'Chapter': row['Chapter'],
                'Group': row['Group']
            })
        elif not available:
            conflicts.append({
                'Date': row['Date'],
                'Assistant': assistant_name,
                'Shift': shift,
                'Day': day_name,
                'Conflict_Reason': 'Asisten tidak tersedia di shift ini',
                'Chapter': row['Chapter'],
                'Group': row['Group']
            })
    
    return pd.DataFrame(conflicts)

# Analisis pola konflik
def analyze_conflict_patterns(conflicts_df):
    if conflicts_df.empty:
        return None, None, None, None
    
    # Konflik per asisten
    per_assistant = conflicts_df.groupby('Assistant').size().reset_index(name='Conflict_Count')
    per_assistant = per_assistant.sort_values('Conflict_Count', ascending=False)
    
    # Konflik per hari
    per_day = conflicts_df.groupby('Day').size().reset_index(name='Conflict_Count')
    per_day = per_day.sort_values('Conflict_Count', ascending=False)
    
    # Konflik per shift
    per_shift = conflicts_df.groupby('Shift').size().reset_index(name='Conflict_Count')
    per_shift = per_shift.sort_values('Conflict_Count', ascending=False)
    
    # Konflik per alasan
    per_reason = conflicts_df.groupby('Conflict_Reason').size().reset_index(name='Conflict_Count')
    per_reason = per_reason.sort_values('Conflict_Count', ascending=False)
    
    return per_assistant, per_day, per_shift, per_reason

# Generate visualisasi
def generate_conflict_visualizations(analysis, vis_path):
    per_assistant, per_day, per_shift, per_reason = analysis
    
    os.makedirs(vis_path, exist_ok=True)
    
    # Visualisasi konflik per asisten
    if per_assistant is not None:
        fig1 = px.bar(
            per_assistant,
            x='Assistant',
            y='Conflict_Count',
            title='Konflik Jadwal per Asisten',
            text='Conflict_Count',
            color='Assistant'
        )
        fig1.write_html(os.path.join(vis_path, 'conflicts_per_assistant.html'))
    
    # Visualisasi konflik per hari
    if per_day is not None:
        fig2 = px.bar(
            per_day,
            x='Day',
            y='Conflict_Count',
            title='Konflik Jadwal per Hari',
            text='Conflict_Count',
            color='Day'
        )
        fig2.write_html(os.path.join(vis_path, 'conflicts_per_day.html'))
    
    # Visualisasi konflik per shift
    if per_shift is not None:
        fig3 = px.bar(
            per_shift,
            x='Shift',
            y='Conflict_Count',
            title='Konflik Jadwal per Shift',
            text='Conflict_Count',
            color='Shift'
        )
        fig3.write_html(os.path.join(vis_path, 'conflicts_per_shift.html'))
    
    # Visualisasi konflik per alasan
    if per_reason is not None:
        fig4 = px.pie(
            per_reason,
            names='Conflict_Reason',
            values='Conflict_Count',
            title='Distribusi Penyebab Konflik'
        )
        fig4.write_html(os.path.join(vis_path, 'conflicts_per_reason.html'))

# Generate laporan HTML
def generate_conflict_report(conflicts_df, analysis, report_path, vis_path):
    per_assistant, per_day, per_shift, per_reason = analysis
    
    # Fungsi untuk membuat iframe relatif
    def vis_iframe(filename):
        rel_path = os.path.relpath(os.path.join(vis_path, filename), os.path.dirname(report_path))
        return f'<iframe src="{rel_path}" width="100%" height="500px"></iframe>'
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Laporan Konflik Jadwal Asisten</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1, h2, h3 {{ color: #2c3e50; }}
            .section {{ 
                margin-bottom: 30px; 
                padding: 20px; 
                border-radius: 10px; 
                background-color: #f9f9f9; 
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .conflict {{ color: #e74c3c; }}
            .visualization {{ 
                margin: 20px 0; 
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                background: white;
            }}
            table {{ 
                border-collapse: collapse; 
                width: 100%; 
                margin: 15px 0;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }}
            th, td {{ 
                border: 1px solid #ddd; 
                padding: 12px; 
                text-align: left; 
            }}
            th {{ 
                background-color: #3498db; 
                color: white; 
            }}
            tr:nth-child(even) {{ background-color: #f5f9fc; }}
            .header {{
                background: linear-gradient(135deg, #3498db, #2c3e50);
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 30px;
            }}
            .summary-card {{
                display: flex;
                justify-content: space-around;
                margin: 20px 0;
                flex-wrap: wrap;
            }}
            .card {{
                background: white;
                border-radius: 10px;
                padding: 15px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                min-width: 200px;
                text-align: center;
                margin: 10px;
            }}
            .card.conflict {{ background-color: #ffebee; }}
            .card h3 {{ margin-top: 0; color: #2c3e50; }}
            .card .value {{
                font-size: 24px;
                font-weight: bold;
                color: #e74c3c;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Laporan Konflik Jadwal Asisten</h1>
            <p>Tanggal laporan: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        
        <div class="summary-card">
            <div class="card conflict">
                <h3>Total Konflik</h3>
                <p class="value">{len(conflicts_df)}</p>
            </div>
            <div class="card">
                <h3>Asisten Terlibat</h3>
                <p class="value">{conflicts_df['Assistant'].nunique() if not conflicts_df.empty else 0}</p>
            </div>
            <div class="card">
                <h3>Hari Terbanyak</h3>
                <p class="value">{per_day.iloc[0]['Day'] if per_day is not None and not per_day.empty else '-'}</p>
            </div>
            <div class="card">
                <h3>Shift Terbanyak</h3>
                <p class="value">{per_shift.iloc[0]['Shift'] if per_shift is not None and not per_shift.empty else '-'}</p>
            </div>
        </div>
        
        <div class="section">
            <h2>Detail Konflik Jadwal</h2>
            {conflicts_df.to_html(index=False) if not conflicts_df.empty else '<p>Tidak ada konflik jadwal</p>'}
        </div>
        
        <div class="section">
            <h2>Analisis Pola Konflik</h2>
            
            <h3>Konflik per Asisten</h3>
            {per_assistant.to_html(index=False) if per_assistant is not None else '<p>Tidak ada data</p>'}
            <div class="visualization">
                {vis_iframe('conflicts_per_assistant.html') if per_assistant is not None else ''}
            </div>
            
            <h3>Konflik per Hari</h3>
            {per_day.to_html(index=False) if per_day is not None else '<p>Tidak ada data</p>'}
            <div class="visualization">
                {vis_iframe('conflicts_per_day.html') if per_day is not None else ''}
            </div>
            
            <h3>Konflik per Shift</h3>
            {per_shift.to_html(index=False) if per_shift is not None else '<p>Tidak ada data</p>'}
            <div class="visualization">
                {vis_iframe('conflicts_per_shift.html') if per_shift is not None else ''}
            </div>
            
            <h3>Distribusi Penyebab Konflik</h3>
            {per_reason.to_html(index=False) if per_reason is not None else '<p>Tidak ada data</p>'}
            <div class="visualization">
                {vis_iframe('conflicts_per_reason.html') if per_reason is not None else ''}
            </div>
        </div>
    </body>
    </html>
    """
    
    with open(report_path, 'w') as f:
        f.write(html_content)

# Eksekusi utama
if __name__ == "__main__":
    print("Memulai deteksi konflik jadwal asisten...")
    print(f"Direktori kerja: {os.path.abspath(DIR_PATH)}")
    
    # Deteksi konflik
    print("Mendeteksi konflik dengan jadwal kuliah...")
    conflicts_df = detect_schedule_conflicts(df)
    
    # Analisis pola
    print("Menganalisis pola konflik...")
    analysis = analyze_conflict_patterns(conflicts_df)
    
    # Generate visualisasi
    vis_path = os.path.join(DIR_PATH, 'conflict_visualizations')
    print("Membuat visualisasi konflik...")
    generate_conflict_visualizations(analysis, vis_path)
    
    # Buat laporan HTML
    print("Menyusun laporan HTML...")
    generate_conflict_report(conflicts_df, analysis, REPORT_PATH, vis_path)
    
    print(f"Laporan konflik berhasil dibuat di: {os.path.abspath(REPORT_PATH)}")
    print(f"Visualisasi disimpan di: {os.path.abspath(vis_path)}")