import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Dasbor Analisis BSM",
    page_icon="🚢",
    layout="wide"
)

# --- FUNGSI HALAMAN 1: ANALISIS BSM KAPAL ---
def display_bsm_kapal():
    # ... (Semua kode di dalam fungsi ini tetap sama persis seperti sebelumnya) ...
    # --- FUNGSI LOADING DATA (DARI GOOGLE SHEETS) ---
    @st.cache_data
    def load_data_from_gsheets(spreadsheet_id, tab_id):
        url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={tab_id}'
        try:
            df = pd.read_csv(
                url, index_col='BSM_CREATED_ON', parse_dates=True,
                na_values=['', ' ', '-', 'NA', 'N/A']
            )
            df.index = df.index.normalize()
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            return df
        except Exception as e:
            st.error(f"Gagal memuat data dari Google Sheets. Cek kembali ID & hak akses. Error: {e}")
            return None

    # --- DATA SOURCE ---
    SPREADSHEET_ID = "1pjRKmpjqwIkV41Q0DOS3x0QgLGO13LDQNJJyo3kR2fM"
    TAB_ID_AKTUAL = "542042387"
    TAB_ID_TRAIN = "1217230565"
    TAB_ID_TEST = "1677129148"
    TAB_ID_FORECAST = "0"

    # --- MEMUAT DATA ---
    with st.spinner("Memuat data untuk Analisis BSM Kapal..."):
        df_aktual = load_data_from_gsheets(SPREADSHEET_ID, TAB_ID_AKTUAL)
        df_train = load_data_from_gsheets(SPREADSHEET_ID, TAB_ID_TRAIN)
        df_test = load_data_from_gsheets(SPREADSHEET_ID, TAB_ID_TEST)
        df_forecast = load_data_from_gsheets(SPREADSHEET_ID, TAB_ID_FORECAST)
    
    # --- KONTEN HALAMAN ---
    st.header("Dasbor Hasil Analisis - BSM Kapal")

    # --- MENGGUNAKAN TABS UNTUK ORGANISASI KONTEN ---
    tab1, tab2, tab3 = st.tabs(["🧩 Dekomposisi Data", "📊 Forecast Result", "📄 Tinjau Data"])

    with tab1:
        st.subheader("Total Pengeluaran Mingguan (Data Aktual)")
        if df_aktual is not None and 'observed' in df_aktual.columns:
            col1, col2 = st.columns([3, 1])
            with col1:
                fig_aktual = px.line(df_aktual, x=df_aktual.index, y='observed')
                fig_aktual.update_traces(
                    hovertemplate="<b>Tanggal:</b> %{x|%d %b %Y}<br><b>Pengeluaran:</b> Rp %{y:,.0f}<extra></extra>"
                )
                fig_aktual.update_layout(
                    height=350,
                    yaxis_title='Nilai (Rp)',
                    yaxis_tickprefix='Rp ',
                    yaxis_tickformat=',.0f'
                )
                st.plotly_chart(fig_aktual, use_container_width=True)
            with col2:
                st.write("#### 📝 Ringkasan Analisis")
                st.markdown("""
                - Biaya mingguan BSM Kapal konsisten di kisaran **4,11 juta–717 juta**, dengan beberapa lonjakan tajam.
                - Distribusi fluktuatif merata dari **2023–2025** dan mencerminkan ritme operasional yang konsisten.
                """)
        else:
            st.warning("Kolom 'observed' untuk data aktual tidak ditemukan.")
        st.markdown("---")
        st.subheader("Dekomposisi Data Historis")
        st.caption("Grafik ini menguraikan pengeluaran menjadi tiga komponen: pola jangka panjang (Trend), pola berulang (Seasonal), dan noise acak (Residual).")
        required_cols = ['trend', 'seasonal', 'resid']
        if df_aktual is not None and all(col in df_aktual.columns for col in required_cols):
            col1, col2, col3 = st.columns(3)
            hovertemplate = "<b>Tanggal:</b> %{x|%d %b %Y}<br><b>Nilai:</b> Rp %{y:,.0f}<extra></extra>"
            with col1:
                fig_trend = px.line(df_aktual, x=df_aktual.index, y='trend', title='Komponen Trend', height=200)
                fig_trend.update_traces(hovertemplate=hovertemplate)
                fig_trend.update_layout(margin=dict(t=30, b=10, l=10, r=10), yaxis_title=None, xaxis_title=None)
                st.plotly_chart(fig_trend, use_container_width=True)
                st.caption("""
            - Biaya pengeluaran secara jangka panjang sedang dalam fase kenaikan yang kuat.
            - Garis trend dapat dideteksi awal dengan menarikkan garis secara semu ke grafik total pengeluaran.
            """)

            with col2:
                fig_seasonal = px.line(df_aktual, x=df_aktual.index, y='seasonal', title='Komponen Seasonal', height=200)
                fig_seasonal.update_traces(hovertemplate=hovertemplate)
                fig_seasonal.update_layout(margin=dict(t=30, b=10, l=10, r=10), yaxis_title=None, xaxis_title=None)
                st.plotly_chart(fig_seasonal, use_container_width=True)
                st.caption("""
            - Pengeluaran memiliki pola musiman tahunan yang kuat dan berulang.
            - Pola ini menjelaskan perilaku pengeluaran yang menjelaskan naik turunnya sepanjang periode.
            """)
                
            with col3:
                fig_resid = px.line(df_aktual, x=df_aktual.index, y='resid', title='Komponen Residual', height=200)
                fig_resid.update_traces(hovertemplate=hovertemplate)
                fig_resid.update_layout(margin=dict(t=30, b=10, l=10, r=10), yaxis_title=None, xaxis_title=None)
                st.plotly_chart(fig_resid, use_container_width=True)
                st.caption("""
            - Risiko biaya tak terduga yang tidak cukup dijelaskan dengan trend dan musiman.
            - Nilai risiko tak terduga selalu muncul di akhir pekan Desember hingga akhir pekan Juli.
            """)
        else:
            st.info("Data dekomposisi (kolom 'trend', 'seasonal', 'resid') tidak ditemukan.")

    with tab2:
        st.subheader("Ringkasan Performa pada Data Test")
        if df_test is not None and df_aktual is not None:
            df_error_test = pd.concat([df_aktual['observed'], df_test['prediksi_inti']], axis=1).dropna()
            if not df_error_test.empty:
                df_error_test['error'] = (df_error_test['observed'] - df_error_test['prediksi_inti']).abs()
                mae = df_error_test['error'].mean()
                squared_errors = (df_error_test['observed'] - df_error_test['prediksi_inti']) ** 2
                mse = np.mean(squared_errors)
                rmse = np.sqrt(mse)
                mean_actual = df_error_test['observed'].mean()
                rrmse = (rmse / mean_actual) * 100 if mean_actual != 0 else 0
                max_error_date = df_error_test['error'].idxmax()
                max_error_value = df_error_test['error'].max()
                col1, col2, col3 = st.columns(3)
                col1.metric(label="Relative RMSE (RRMSE)", value=f"{rrmse:.2f}%")
                col2.metric(label="Rata-rata Error (MAE)", value=f"Rp {mae:,.0f}")
                col3.metric(label="Error Tertinggi Terjadi Pada", value=max_error_date.strftime('%d %B %Y'), help=f"Selisih sebesar Rp {max_error_value:,.0f}")
            else:
                st.warning("Tidak ada periode data test yang tumpang tindih untuk dihitung performanya.")
        else:
            st.info("Data test atau data aktual tidak ditemukan untuk menghitung metrik performa.")

        st.markdown("---")
        st.subheader("Visualisasi Hasil Model")
        plot_col, table_col = st.columns([3, 1])
        with plot_col:
            fig = go.Figure()
            if df_aktual is not None: fig.add_trace(go.Scatter(x=df_aktual.index, y=df_aktual['observed'], mode='lines', name='Data Aktual', line=dict(color='#0068C9', width=2)))
            if df_train is not None: fig.add_trace(go.Scatter(x=df_train.index, y=df_train['Train Pred'], mode='lines', name='Hasil Training', line=dict(color='#FFAA00', width=2, dash='dash')))
            if df_test is not None: fig.add_trace(go.Scatter(x=df_test.index, y=df_test['prediksi_inti'], mode='lines', name='Prediksi Test', line=dict(color='#FF4B4B', width=2)))
            if df_forecast is not None:
                fig.add_trace(go.Scatter(x=df_forecast.index, y=df_forecast['batas_atas_99'], mode='lines', line=dict(width=0), hoverinfo='skip', showlegend=False))
                fig.add_trace(go.Scatter(x=df_forecast.index, y=df_forecast['batas_bawah_99'], mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(45, 201, 55, 0.2)', hoverinfo='skip', name='Batas Risiko Forecast'))
                fig.add_trace(go.Scatter(x=df_forecast.index, y=df_forecast['prediksi_inti'], mode='lines', name='Forecast', line=dict(color='#2DC937', width=3), customdata=df_forecast[['batas_bawah_99', 'batas_atas_99']], hovertemplate="<b>Forecast: Rp %{y:,.0f}</b><br>Batas Bawah: Rp %{customdata[0]:,.0f}<br>Batas Atas: Rp %{customdata[1]:,.0f}<extra></extra>"))

            if df_forecast is not None and not df_forecast.empty:
                start_forecast_date = df_forecast.index.min()
                fig.add_shape(type="line", x0=start_forecast_date, y0=0, x1=start_forecast_date, y1=1, yref="paper", line=dict(color="grey", width=2, dash="dash"))
                fig.add_annotation(x=start_forecast_date, y=1.05, yref="paper", text="Mulai Forecast", showarrow=False, xanchor="left")

            fig.update_layout(title_text="", xaxis_title='BSM_CREATED_ON', yaxis_title='Nilai (Rp)', yaxis_tickprefix='Rp ', yaxis_tickformat=',.0f', hovermode='x unified', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig, use_container_width=True)

        with table_col:
            st.caption("Detail Nilai Forecast")
            if df_forecast is not None:
                df_forecast_display = df_forecast[['prediksi_inti', 'batas_bawah_99', 'batas_atas_99']].copy().reset_index()
                df_forecast_display = df_forecast_display.rename(columns={'BSM_CREATED_ON': 'BSM_CREATED_ON', 'prediksi_inti': 'Forecast', 'batas_bawah_99': 'Batas Bawah', 'batas_atas_99': 'Batas Atas'})
                for col in ['Forecast', 'Batas Bawah', 'Batas Atas']:
                    df_forecast_display[col] = df_forecast_display[col].apply(lambda x: f"Rp {x:,.0f}" if pd.notna(x) else "")
                st.dataframe(df_forecast_display, column_config={"BSM_CREATED_ON": st.column_config.DateColumn("BSM_CREATED_ON", format="DD MMM YYYY")}, hide_index=True, use_container_width=True)
            else: st.info("Data forecast tidak tersedia.")

    with tab3:
        st.subheader("Tinjau Data Mentah")
        def create_unified_display_df(df_aktual, df_train, df_test, df_forecast):
            s_aktual = df_aktual['observed'].rename('Aktual') if df_aktual is not None else pd.Series(name='Aktual')
            s_train = df_train['Train Pred'].rename('Prediksi') if df_train is not None else pd.Series(name='Prediksi')
            s_test = df_test['prediksi_inti'].rename('Prediksi') if df_test is not None else pd.Series(name='Prediksi')
            s_forecast = df_forecast['prediksi_inti'].rename('Prediksi') if df_forecast is not None else pd.Series(name='Prediksi')
            s_prediksi = pd.concat([s_train, s_test, s_forecast])
            unified_df = pd.concat([s_aktual, s_prediksi], axis=1)
            unified_df['Keterangan'] = 'Data Historis'
            if df_train is not None: unified_df.loc[df_train.index, 'Keterangan'] = 'Hasil Training'
            if df_test is not None: unified_df.loc[df_test.index, 'Keterangan'] = 'Prediksi Test'
            if df_forecast is not None: unified_df.loc[df_forecast.index, 'Keterangan'] = 'Forecast Masa Depan'
            for col in ['Aktual', 'Prediksi']:
                if col in unified_df.columns:
                    unified_df[col] = unified_df[col].apply(lambda x: f"Rp {x:,.0f}" if pd.notna(x) else "")
            unified_df = unified_df.reset_index().rename(columns={'index': 'BSM_CREATED_ON'})
            unified_df = unified_df[['BSM_CREATED_ON', 'Keterangan', 'Aktual', 'Prediksi']]
            return unified_df

        unified_df = create_unified_display_df(df_aktual, df_train, df_test, df_forecast)
        st.caption("Tabel ini menggabungkan semua data yang digunakan dalam grafik di atas.")
        st.dataframe(unified_df, column_config={"BSM_CREATED_ON": st.column_config.DateColumn("BSM_CREATED_ON", format="DD MMM YYYY")}, use_container_width=True, hide_index=True)

# --- FUNGSI UNTUK HALAMAN DUMMY BSM ALAT BERAT ---
def display_bsm_alat_berat():
    st.header("Dasbor Hasil Analisis - BSM Alat Berat")
    st.image("https://placehold.co/600x300/EFEFEF/AAAAAA?text=Grafik+Analisis", caption="Contoh Grafik")
    st.info("🚧 Analisis sedang diproses.")
    st.write("Konten dan analisis untuk BSM Alat Berat akan segera tersedia di sini.")

# --- BAGIAN UTAMA APLIKASI ---

# Judul utama aplikasi di bagian atas sidebar
st.sidebar.title("Dasbor Analisis BSM")

# Navigasi dropdown dipindahkan ke sidebar
pilihan_bsm = st.sidebar.selectbox(
    "Pilih Jenis Data:",
    ("BSM Kapal", "BSM Alat Berat")
)

st.markdown("---") # Garis pemisah di bawah judul

# --- KONTEN DINAMIS BERDASARKAN PILIHAN ---
if pilihan_bsm == "BSM Kapal":
    display_bsm_kapal()  # Panggil fungsi untuk menampilkan analisis kapal

elif pilihan_bsm == "BSM Alat Berat":
    display_bsm_alat_berat()  # Panggil fungsi untuk halaman dummy