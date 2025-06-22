import pandas as pd
import plotly.express as px
import os
from datetime import datetime
from collections import defaultdict, Counter
import numpy as np

# Konfigurasi direktori
DIR_PATH = 'experiment_results/latest_result'
EXCEL_PATH = os.path.join(DIR_PATH, 'jadwal_praktikum.xlsx')
VIS_PATH = os.path.join(DIR_PATH, 'visualizations')
REPORT_PATH = os.path.join(DIR_PATH, 'laporan_jadwal.html')

# Buat direktori jika belum ada
os.makedirs(DIR_PATH, exist_ok=True)
os.makedirs(VIS_PATH, exist_ok=True)

# Baca file Excel
df = pd.read_excel(EXCEL_PATH)

# Konversi tipe data
df['Date'] = pd.to_datetime(df['Date'])
df['DayName'] = df['Date'].dt.day_name()

# 1. Deteksi Konflik Jadwal sesuai Fitness Function
def detect_conflicts(df):
    # Konflik asisten: asisten mengajar >1 chapter berbeda dalam shift yang sama
    assistant_conflicts = []
    assistant_violations = defaultdict(list)
    
    # Konflik grup: grup memiliki >1 sesi dalam shift yang sama
    group_conflicts = []
    group_violations = defaultdict(list)
    
    # Kapasitas asisten: asisten mengajar > threshold grup dalam satu shift
    capacity_violations = []
    
    # Kelompokkan berdasarkan tanggal, shift, dan asisten
    grouped = df.groupby(['Date', 'Shift', 'Assistant'])
    for (date, shift, assistant), group in grouped:
        chapters = group['Chapter'].unique()
        if len(chapters) > 1:
            # Konflik asisten: mengajar >1 chapter berbeda
            conflict_data = group.copy()
            conflict_data['Conflict_Type'] = 'Assistant Chapter Conflict'
            assistant_conflicts.append(conflict_data)
            
            # Catat chapter yang bertabrakan
            for _, row in group.iterrows():
                key = (date, shift, assistant)
                assistant_violations[key].append(row['Chapter'])
    
    # Kelompokkan berdasarkan tanggal, shift, dan grup
    grouped = df.groupby(['Date', 'Shift', 'Group'])
    for (date, shift, group_id), group in grouped:
        if len(group) > 1:
            # Konflik grup: memiliki >1 sesi dalam shift yang sama
            conflict_data = group.copy()
            conflict_data['Conflict_Type'] = 'Group Session Conflict'
            group_conflicts.append(conflict_data)
            
            # Catat sesi yang bertabrakan
            for _, row in group.iterrows():
                key = (date, shift, group_id)
                group_violations[key].append(row['Chapter'])
    
    # Deteksi kapasitas asisten per shift
    grouped = df.groupby(['Date', 'Shift', 'Assistant'])
    for (date, shift, assistant), group in grouped:
        groups_count = group['Group'].nunique()
        if groups_count > 3:  # Threshold 2 grup per shift
            violation_data = group.copy()
            violation_data['Violation_Type'] = f'Assistant Capacity > {groups_count} groups'
            capacity_violations.append(violation_data)
    
    # Gabungkan semua konflik
    assistant_conflicts_df = pd.concat(assistant_conflicts) if assistant_conflicts else pd.DataFrame()
    group_conflicts_df = pd.concat(group_conflicts) if group_conflicts else pd.DataFrame()
    capacity_violations_df = pd.concat(capacity_violations) if capacity_violations else pd.DataFrame()
    
    return {
        'assistant_conflicts': assistant_conflicts_df,
        'group_conflicts': group_conflicts_df,
        'capacity_violations': capacity_violations_df,
        'assistant_violations': dict(assistant_violations),
        'group_violations': dict(group_violations)
    }

# 2. Analisis Beban Kerja sesuai Fitness Function
def analyze_workload(df):
    # Hitung beban kerja asisten
    workload = df.groupby('Assistant').agg(
        Total_Sessions=('Chapter', 'count'),
        Groups_Handled=('Group', 'nunique'),
        Shifts_Handled=('Shift', 'nunique'),
        Days_Worked=('Date', 'nunique'),
        Chapters_Handled=('Chapter', 'nunique')
    ).reset_index()
    
    # Hitung shift per asisten per hari
    shifts_per_day = df.groupby(['Assistant', 'Date'])['Shift'].nunique().reset_index()
    shifts_per_day = shifts_per_day.rename(columns={'Shift': 'Shifts_Per_Day'})
    
    return workload, shifts_per_day

# 3. Analisis Distribusi
def analyze_distributions(df):
    # Distribusi per Kelompok
    group_coverage = df.groupby('Group')['Chapter'].nunique().reset_index()
    group_coverage.columns = ['Group', 'Unique Chapters']
    
    # Distribusi Shift
    shift_dist = df['Shift'].value_counts().reset_index()
    shift_dist.columns = ['Shift', 'Count']
    
    # Distribusi Asisten
    assistant_dist = df['Assistant'].value_counts().reset_index()
    assistant_dist.columns = ['Assistant', 'Sessions']
    
    # Distribusi Harian
    daily_dist = df['Date'].value_counts().reset_index()
    daily_dist.columns = ['Date', 'Sessions']
    daily_dist = daily_dist.sort_values('Date')
    
    # Distribusi Hari
    day_dist = df['DayName'].value_counts().reset_index()
    day_dist.columns = ['Day', 'Sessions']
    
    # Distribusi Laboratorium
    lab_dist = df['Lab'].value_counts().reset_index()
    lab_dist.columns = ['Lab', 'Sessions']
    
    return {
        'group_coverage': group_coverage,
        'shift_dist': shift_dist,
        'assistant_dist': assistant_dist,
        'daily_dist': daily_dist,
        'day_dist': day_dist,
        'lab_dist': lab_dist
    }

# 4. Generate Visualisasi
def generate_visualizations(distributions, workload_data, vis_path):
    # Distribusi Chapter per Kelompok
    fig1 = px.bar(
        distributions['group_coverage'],
        x='Group',
        y='Unique Chapters',
        title='Coverage Chapter per Kelompok',
        text='Unique Chapters',
        color='Group',
        height=400
    )
    fig1.update_layout(yaxis_range=[0, 8])
    fig1.write_html(os.path.join(vis_path, 'group_coverage.html'))
    
    # Distribusi Shift
    fig2 = px.pie(
        distributions['shift_dist'],
        names='Shift',
        values='Count',
        title='Distribusi Penggunaan Shift',
        height=500
    )
    fig2.write_html(os.path.join(vis_path, 'shift_distribution.html'))
    
    # Distribusi Asisten
    fig3 = px.bar(
        distributions['assistant_dist'],
        x='Assistant',
        y='Sessions',
        title='Beban Kerja Asisten',
        text='Sessions',
        color='Assistant',
        height=400
    )
    fig3.write_html(os.path.join(vis_path, 'assistant_workload.html'))
    
    # Distribusi Harian
    fig4 = px.line(
        distributions['daily_dist'],
        x='Date',
        y='Sessions',
        title='Jumlah Sesi per Hari',
        markers=True,
        height=400
    )
    fig4.update_xaxes(rangeslider_visible=True)
    fig4.write_html(os.path.join(vis_path, 'daily_sessions.html'))
    
    # Distribusi Hari
    fig5 = px.bar(
        distributions['day_dist'],
        x='Day',
        y='Sessions',
        title='Jumlah Sesi per Hari dalam Minggu',
        color='Day',
        height=400
    )
    fig5.write_html(os.path.join(vis_path, 'day_distribution.html'))
    
    # Distribusi Lab
    fig6 = px.pie(
        distributions['lab_dist'],
        names='Lab',
        values='Sessions',
        title='Distribusi Penggunaan Laboratorium',
        height=500
    )
    fig6.write_html(os.path.join(vis_path, 'lab_distribution.html'))
    
    # Heatmap Beban Kerja
    workload_df, _ = workload_data
    fig7 = px.imshow(
        workload_df.set_index('Assistant').drop(columns=['Total_Sessions']),
        labels=dict(x="Metric", y="Assistant", color="Value"),
        title='Heatmap Beban Kerja Asisten',
        aspect="auto",
        height=500
    )
    fig7.write_html(os.path.join(vis_path, 'workload_heatmap.html'))
    
    # Beban kelompok per asisten
    fig8 = px.bar(
        workload_df, 
        x='Assistant', 
        y='Groups_Handled',
        title='Kelompok yang Ditangani per Asisten',
        text='Groups_Handled',
        color='Assistant',
        height=400
    )
    fig8.write_html(os.path.join(vis_path, 'groups_handled.html'))

# 5. Generate Laporan HTML
def generate_html_report(conflicts, distributions, workload_data, report_path, vis_path):
    # Fungsi untuk membuat iframe relatif
    def vis_iframe(filename):
        rel_path = os.path.relpath(os.path.join(vis_path, filename), os.path.dirname(report_path))
        return f'<iframe src="{rel_path}" width="100%" height="500px"></iframe>'
    
    workload_df, shifts_per_day = workload_data
    
    # Ringkasan konflik
    assistant_conflict_count = len(conflicts['assistant_conflicts'])
    group_conflict_count = len(conflicts['group_conflicts'])
    capacity_violation_count = len(conflicts['capacity_violations'])
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Laporan Analisis Jadwal Praktikum</title>
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
            .conflict {{ color: #e74c3c; font-weight: bold; }}
            .warning {{ color: #e67e22; }}
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
                position: sticky;
                top: 0;
            }}
            tr:nth-child(even) {{ background-color: #f5f9fc; }}
            tr:hover {{ background-color: #f1f7fd; }}
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
            .card.warning {{ background-color: #fff3e0; }}
            .card.success {{ background-color: #e8f5e9; }}
            .card h3 {{ margin-top: 0; color: #2c3e50; }}
            .card .value {{
                font-size: 24px;
                font-weight: bold;
            }}
            .conflict .value {{ color: #e74c3c; }}
            .warning .value {{ color: #e67e22; }}
            .success .value {{ color: #2ecc71; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Laporan Analisis Jadwal Praktikum</h1>
            <p>Tanggal laporan: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        
        <div class="summary-card">
            <div class="card success">
                <h3>Total Sesi</h3>
                <p class="value">{len(df)}</p>
            </div>
            <div class="card success">
                <h3>Asisten</h3>
                <p class="value">{df['Assistant'].nunique()}</p>
            </div>
            <div class="card success">
                <h3>Kelompok</h3>
                <p class="value">{df['Group'].nunique()}</p>
            </div>
            <div class="card {'conflict' if assistant_conflict_count > 0 else 'success'}">
                <h3>Konflik Asisten</h3>
                <p class="value">{assistant_conflict_count}</p>
            </div>
            <div class="card {'conflict' if group_conflict_count > 0 else 'success'}">
                <h3>Konflik Grup</h3>
                <p class="value">{group_conflict_count}</p>
            </div>
            <div class="card {'warning' if capacity_violation_count > 0 else 'success'}">
                <h3>Pelanggaran Kapasitas</h3>
                <p class="value">{capacity_violation_count}</p>
            </div>
        </div>
        
        <div class="section">
            <h2>Konflik Jadwal Asisten</h2>
            <p>Terjadi ketika asisten mengajar lebih dari satu chapter berbeda dalam shift yang sama</p>
            {"<p>Tidak ada konflik asisten</p>" if assistant_conflict_count == 0 else conflicts['assistant_conflicts'].to_html(index=False)}
            
            <h2>Konflik Jadwal Grup</h2>
            <p>Terjadi ketika grup memiliki lebih dari satu sesi dalam shift yang sama</p>
            {"<p>Tidak ada konflik grup</p>" if group_conflict_count == 0 else conflicts['group_conflicts'].to_html(index=False)}
            
            <h2>Pelanggaran Kapasitas Asisten</h2>
            <p>Terjadi ketika asisten mengajar lebih dari 2 grup dalam satu shift</p>
            {"<p>Tidak ada pelanggaran kapasitas</p>" if capacity_violation_count == 0 else conflicts['capacity_violations'].to_html(index=False)}
        </div>
        
        <div class="section">
            <h2>Coverage Chapter per Kelompok</h2>
            <p>Setiap kelompok harus memiliki 8 chapter unik (U-1 hingga U-8):</p>
            {distributions['group_coverage'].to_html(index=False)}
            <div class="visualization">
                {vis_iframe('group_coverage.html')}
            </div>
        </div>
        
        <div class="section">
            <h2>Distribusi Shift</h2>
            {distributions['shift_dist'].to_html(index=False)}
            <div class="visualization">
                {vis_iframe('shift_distribution.html')}
            </div>
        </div>
        
        <div class="section">
            <h2>Analisis Beban Kerja Asisten</h2>
            <h3>Ringkasan Beban Kerja</h3>
            {workload_df.to_html(index=False)}
            
            <h3>Shift per Hari per Asisten</h3>
            {shifts_per_day.to_html(index=False)}
            
            <div class="visualization">
                {vis_iframe('assistant_workload.html')}
            </div>
            <div class="visualization">
                {vis_iframe('groups_handled.html')}
            </div>
            <div class="visualization">
                {vis_iframe('workload_heatmap.html')}
            </div>
        </div>
        
        <div class="section">
            <h2>Distribusi Harian</h2>
            <div class="visualization">
                {vis_iframe('daily_sessions.html')}
            </div>
        </div>
        
        <div class="section">
            <h2>Distribusi per Hari dalam Minggu</h2>
            {distributions['day_dist'].to_html(index=False)}
            <div class="visualization">
                {vis_iframe('day_distribution.html')}
            </div>
        </div>
        
        <div class="section">
            <h2>Distribusi Penggunaan Laboratorium</h2>
            {distributions['lab_dist'].to_html(index=False)}
            <div class="visualization">
                {vis_iframe('lab_distribution.html')}
            </div>
        </div>
    </body>
    </html>
    """
    
    with open(report_path, 'w') as f:
        f.write(html_content)

# Eksekusi Analisis
if __name__ == "__main__":
    print("Memulai analisis jadwal...")
    print(f"Direktori kerja: {os.path.abspath(DIR_PATH)}")
    
    # 1. Deteksi konflik sesuai fitness function
    print("Mendeteksi konflik jadwal berdasarkan aturan fitness...")
    conflicts = detect_conflicts(df)
    
    # 2. Analisis distribusi
    print("Menganalisis distribusi jadwal...")
    distributions = analyze_distributions(df)
    
    # 3. Analisis beban kerja
    print("Menganalisis beban kerja asisten...")
    workload_data = analyze_workload(df)
    
    # 4. Generate visualisasi
    print("Membuat visualisasi data...")
    generate_visualizations(distributions, workload_data, VIS_PATH)
    
    # 5. Buat laporan HTML
    print("Menyusun laporan HTML...")
    generate_html_report(conflicts, distributions, workload_data, REPORT_PATH, VIS_PATH)
    
    print(f"Laporan berhasil dibuat di: {os.path.abspath(REPORT_PATH)}")
    print(f"Visualisasi disimpan di: {os.path.abspath(VIS_PATH)}")