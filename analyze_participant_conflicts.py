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

from scheduling_data.models import Group, Participant

# Konfigurasi direktori
DIR_PATH = 'experiment_results/latest_result'
EXCEL_PATH = os.path.join(DIR_PATH, 'jadwal_praktikum.xlsx')
REPORT_PATH = os.path.join(DIR_PATH, 'konflik_jadwal_partisipan_grup.html')

# Buat direktori jika belum ada
os.makedirs(DIR_PATH, exist_ok=True)

# Baca file Excel
df = pd.read_excel(EXCEL_PATH)

# Konversi tipe data
df['Date'] = pd.to_datetime(df['Date'])
df['DayName'] = df['Date'].dt.day_name()

# Mapping hari Indonesia-Inggris
day_mapping = {
    'Monday': 'Senin',
    'Tuesday': 'Selasa',
    'Wednesday': 'Rabu',
    'Thursday': 'Kamis',
    'Friday': 'Jumat',
    'Saturday': 'Sabtu',
    'Sunday': 'Minggu'
}
reverse_day_mapping = {v: k for k, v in day_mapping.items()}

# Fungsi untuk memeriksa konflik jadwal partisipan
def detect_participant_conflicts(df):
    conflicts = []
    
    for _, row in df.iterrows():
        group_id = row['Group']
        # print(f"Memeriksa konflik untuk grup {group_id} pada {row['Date']} - Shift: {row['Shift']}")
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            conflicts.append({
                'Date': row['Date'],
                'Shift': row['Shift'],
                'Group': group_id,
                'Chapter': row['Chapter'],
                'Conflict_Type': 'Group not found',
                'Affected': 'All participants'
            })
            continue
        
        # Dapatkan semua partisipan dalam grup
        participants = group.participants.all()
        
        day_name = row['DayName']
        english_day = reverse_day_mapping.get(day_name, day_name)
        shift = row['Shift']
        
        for participant in participants:
            schedule = participant.regular_schedule
            
            if not schedule:
                conflicts.append({
                    'Date': row['Date'],
                    'Shift': row['Shift'],
                    'Group': group_id,
                    'Participant': participant.name,
                    'Participant_ID': participant.id,
                    'Conflict_Type': 'Participant schedule not found',
                    'Chapter': row['Chapter']
                })
                continue
            
            if english_day not in schedule:
                conflicts.append({
                    'Date': row['Date'],
                    'Shift': row['Shift'],
                    'Group': group_id,
                    'Participant': participant.name,
                    'Participant_ID': participant.id,
                    'Conflict_Type': f'Day {english_day} not in schedule',
                    'Chapter': row['Chapter']
                })
                continue
            
            day_schedule = schedule[english_day]
            if shift not in day_schedule:
                conflicts.append({
                    'Date': row['Date'],
                    'Shift': row['Shift'],
                    'Group': group_id,
                    'Participant': participant.name,
                    'Participant_ID': participant.id,
                    'Conflict_Type': f'Shift {shift} not in schedule',
                    'Chapter': row['Chapter']
                })
            elif not day_schedule[shift]:
                conflicts.append({
                    'Date': row['Date'],
                    'Shift': row['Shift'],
                    'Group': group_id,
                    'Participant': participant.name,
                    'Participant_ID': participant.id,
                    'Conflict_Type': 'Participant not available',
                    'Chapter': row['Chapter']
                })
    
    return pd.DataFrame(conflicts)

# Fungsi untuk memeriksa konflik jadwal grup
def detect_group_conflicts(df):
    conflicts = []
    
    for _, row in df.iterrows():
        group_id = row['Group']
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            conflicts.append({
                'Date': row['Date'],
                'Shift': row['Shift'],
                'Group': group_id,
                'Chapter': row['Chapter'],
                'Conflict_Type': 'Group not found',
                'Affected': 'All participants'
            })
            continue
        
        # Dapatkan jadwal grup (merged schedule)
        participants = group.participants.all()
        if not participants:
            conflicts.append({
                'Date': row['Date'],
                'Shift': row['Shift'],
                'Group': group_id,
                'Chapter': row['Chapter'],
                'Conflict_Type': 'No participants in group',
                'Affected': 'All'
            })
            continue
        
        # Ambil jadwal pertama sebagai template
        first_schedule = participants[0].regular_schedule
        if not first_schedule:
            conflicts.append({
                'Date': row['Date'],
                'Shift': row['Shift'],
                'Group': group_id,
                'Chapter': row['Chapter'],
                'Conflict_Type': 'No schedule template found',
                'Affected': 'All'
            })
            continue
        
        # Buat jadwal gabungan
        merged_schedule = {}
        for day in first_schedule:
            merged_schedule[day] = {}
            for shift_name in first_schedule[day]:
                available = True
                for participant in participants:
                    p_schedule = participant.regular_schedule
                    if not p_schedule or day not in p_schedule:
                        available = False
                        break
                    if shift_name not in p_schedule[day] or not p_schedule[day][shift_name]:
                        available = False
                        break
                merged_schedule[day][shift_name] = available
        
        day_name = row['DayName']
        english_day = reverse_day_mapping.get(day_name, day_name)
        shift = row['Shift']
        
        if english_day not in merged_schedule:
            conflicts.append({
                'Date': row['Date'],
                'Shift': row['Shift'],
                'Group': group_id,
                'Chapter': row['Chapter'],
                'Conflict_Type': f'Day {english_day} not in group schedule',
                'Affected': 'All'
            })
            continue
        
        day_schedule = merged_schedule[english_day]
        if shift not in day_schedule:
            conflicts.append({
                'Date': row['Date'],
                'Shift': row['Shift'],
                'Group': group_id,
                'Chapter': row['Chapter'],
                'Conflict_Type': f'Shift {shift} not in group schedule',
                'Affected': 'All'
            })
        elif not day_schedule[shift]:
            conflicts.append({
                'Date': row['Date'],
                'Shift': row['Shift'],
                'Group': group_id,
                'Chapter': row['Chapter'],
                'Conflict_Type': 'Group not available (merged schedule)',
                'Affected': 'All'
            })
    
    return pd.DataFrame(conflicts)

# Analisis pola konflik
def analyze_conflict_patterns(participant_conflicts, group_conflicts):
    # Gabungkan semua konflik
    all_conflicts = pd.concat([participant_conflicts, group_conflicts], ignore_index=True)
    
    if all_conflicts.empty:
        return None, None, None, None, None
    
    # Konflik per grup
    per_group = all_conflicts.groupby('Group').size().reset_index(name='Conflict_Count')
    per_group = per_group.sort_values('Conflict_Count', ascending=False)
    
    # Konflik per hari
    per_day = all_conflicts.groupby('Date').size().reset_index(name='Conflict_Count')
    per_day = per_day.sort_values('Date')
    
    # Konflik per shift
    per_shift = all_conflicts.groupby('Shift').size().reset_index(name='Conflict_Count')
    per_shift = per_shift.sort_values('Conflict_Count', ascending=False)
    
    # Konflik per tipe
    per_type = all_conflicts.groupby('Conflict_Type').size().reset_index(name='Conflict_Count')
    per_type = per_type.sort_values('Conflict_Count', ascending=False)
    
    # Konflik per partisipan (jika ada)
    if 'Participant' in all_conflicts.columns:
        per_participant = all_conflicts.groupby(['Participant', 'Participant_ID']).size().reset_index(name='Conflict_Count')
        per_participant = per_participant.sort_values('Conflict_Count', ascending=False)
    else:
        per_participant = None
    
    return per_group, per_day, per_shift, per_type, per_participant

# Generate visualisasi
def generate_conflict_visualizations(analysis, vis_path):
    per_group, per_day, per_shift, per_type, per_participant = analysis
    
    os.makedirs(vis_path, exist_ok=True)
    
    # Visualisasi konflik per grup
    if per_group is not None and not per_group.empty:
        fig1 = px.bar(
            per_group,
            x='Group',
            y='Conflict_Count',
            title='Konflik Jadwal per Grup',
            text='Conflict_Count',
            color='Group'
        )
        fig1.write_html(os.path.join(vis_path, 'conflicts_per_group.html'))
    
    # Visualisasi konflik per hari
    if per_day is not None and not per_day.empty:
        fig2 = px.line(
            per_day,
            x='Date',
            y='Conflict_Count',
            title='Konflik Jadwal per Hari',
            markers=True
        )
        fig2.write_html(os.path.join(vis_path, 'conflicts_per_day.html'))
    
    # Visualisasi konflik per shift
    if per_shift is not None and not per_shift.empty:
        fig3 = px.bar(
            per_shift,
            x='Shift',
            y='Conflict_Count',
            title='Konflik Jadwal per Shift',
            text='Conflict_Count',
            color='Shift'
        )
        fig3.write_html(os.path.join(vis_path, 'conflicts_per_shift.html'))
    
    # Visualisasi konflik per tipe
    if per_type is not None and not per_type.empty:
        fig4 = px.pie(
            per_type,
            names='Conflict_Type',
            values='Conflict_Count',
            title='Distribusi Jenis Konflik'
        )
        fig4.write_html(os.path.join(vis_path, 'conflicts_per_type.html'))
    
    # Visualisasi konflik per partisipan
    if per_participant is not None and not per_participant.empty:
        fig5 = px.bar(
            per_participant,
            x='Participant',
            y='Conflict_Count',
            title='Konflik Jadwal per Partisipan',
            text='Conflict_Count',
            color='Participant'
        )
        fig5.write_html(os.path.join(vis_path, 'conflicts_per_participant.html'))

# Generate laporan HTML
def generate_conflict_report(participant_conflicts, group_conflicts, analysis, report_path, vis_path):
    per_group, per_day, per_shift, per_type, per_participant = analysis
    
    # Fungsi untuk membuat iframe relatif
    def vis_iframe(filename):
        rel_path = os.path.relpath(os.path.join(vis_path, filename), os.path.dirname(report_path))
        return f'<iframe src="{rel_path}" width="100%" height="500px"></iframe>'
    
    total_conflicts = len(participant_conflicts) + len(group_conflicts)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Laporan Konflik Jadwal Partisipan & Grup</title>
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
            <h1>Laporan Konflik Jadwal Partisipan & Grup</h1>
            <p>Tanggal laporan: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        
        <div class="summary-card">
            <div class="card conflict">
                <h3>Total Konflik</h3>
                <p class="value">{total_conflicts}</p>
            </div>
            <div class="card">
                <h3>Konflik Partisipan</h3>
                <p class="value">{len(participant_conflicts)}</p>
            </div>
            <div class="card">
                <h3>Konflik Grup</h3>
                <p class="value">{len(group_conflicts)}</p>
            </div>
            <div class="card">
                <h3>Grup Terdampak</h3>
                <p class="value">{participant_conflicts['Group'].nunique() if not participant_conflicts.empty else 0}</p>
            </div>
        </div>
        
        <div class="section">
            <h2>Detail Konflik Partisipan</h2>
            {participant_conflicts.to_html(index=False) if not participant_conflicts.empty else '<p>Tidak ada konflik partisipan</p>'}
        </div>
        
        <div class="section">
            <h2>Detail Konflik Grup</h2>
            {group_conflicts.to_html(index=False) if not group_conflicts.empty else '<p>Tidak ada konflik grup</p>'}
        </div>
        
        <div class="section">
            <h2>Analisis Pola Konflik</h2>
            
            <h3>Konflik per Grup</h3>
            {per_group.to_html(index=False) if per_group is not None and not per_group.empty else '<p>Tidak ada data</p>'}
            <div class="visualization">
                {vis_iframe('conflicts_per_group.html') if per_group is not None and not per_group.empty else ''}
            </div>
            
            <h3>Konflik per Hari</h3>
            {per_day.to_html(index=False) if per_day is not None and not per_day.empty else '<p>Tidak ada data</p>'}
            <div class="visualization">
                {vis_iframe('conflicts_per_day.html') if per_day is not None and not per_day.empty else ''}
            </div>
            
            <h3>Konflik per Shift</h3>
            {per_shift.to_html(index=False) if per_shift is not None and not per_shift.empty else '<p>Tidak ada data</p>'}
            <div class="visualization">
                {vis_iframe('conflicts_per_shift.html') if per_shift is not None and not per_shift.empty else ''}
            </div>
            
            <h3>Distribusi Jenis Konflik</h3>
            {per_type.to_html(index=False) if per_type is not None and not per_type.empty else '<p>Tidak ada data</p>'}
            <div class="visualization">
                {vis_iframe('conflicts_per_type.html') if per_type is not None and not per_type.empty else ''}
            </div>
            
            <h3>Konflik per Partisipan</h3>
            {per_participant.to_html(index=False) if per_participant is not None and not per_participant.empty else '<p>Tidak ada data</p>'}
            <div class="visualization">
                {vis_iframe('conflicts_per_participant.html') if per_participant is not None and not per_participant.empty else ''}
            </div>
        </div>
    </body>
    </html>
    """
    
    with open(report_path, 'w') as f:
        f.write(html_content)

# Eksekusi utama
if __name__ == "__main__":
    print("Memulai deteksi konflik jadwal partisipan dan grup...")
    print(f"Direktori kerja: {os.path.abspath(DIR_PATH)}")
    
    # Deteksi konflik partisipan
    print("Mendeteksi konflik jadwal partisipan...")
    participant_conflicts = detect_participant_conflicts(df)
    
    # Deteksi konflik grup
    print("Mendeteksi konflik jadwal grup...")
    group_conflicts = detect_group_conflicts(df)
    
    # Analisis pola
    print("Menganalisis pola konflik...")
    analysis = analyze_conflict_patterns(participant_conflicts, group_conflicts)
    
    # Generate visualisasi
    vis_path = os.path.join(DIR_PATH, 'conflict_visualizations_participant')
    print("Membuat visualisasi konflik...")
    generate_conflict_visualizations(analysis, vis_path)
    
    # Buat laporan HTML
    print("Menyusun laporan HTML...")
    generate_conflict_report(participant_conflicts, group_conflicts, analysis, REPORT_PATH, vis_path)
    
    print(f"Laporan konflik berhasil dibuat di: {os.path.abspath(REPORT_PATH)}")
    print(f"Visualisasi disimpan di: {os.path.abspath(vis_path)}")