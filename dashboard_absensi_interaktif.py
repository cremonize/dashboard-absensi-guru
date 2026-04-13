import streamlit as st
import pandas as pd
from datetime import date
import os

# ==============================
# KONFIGURASI AWAL
# ==============================
st.set_page_config(page_title="Dashboard Absensi Interaktif", layout="wide")

DATA_FILE = "absensi_db.csv"

# ==============================
# INIT DATABASE (CSV)
# ==============================
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=["Nama", "Tanggal", "Status"])
    df_init.to_csv(DATA_FILE, index=False)


def load_data():
    return pd.read_csv(DATA_FILE, parse_dates=["Tanggal"])


def save_data(df):
    df.to_csv(DATA_FILE, index=False)


# ==============================
# LOGIN SEDERHANA
# ==============================
st.sidebar.title("🔐 Login")
role = st.sidebar.selectbox("Masuk sebagai", ["Admin", "User"])

# ==============================
# NAVIGASI
# ==============================
menu = st.sidebar.radio("Menu", [
    "📊 Dashboard",
    "📅 Data Absensi",
    "✍️ Input Absensi"
])

# ==============================
# LOAD DATA
# ==============================
df = load_data()

# ==============================
# DASHBOARD
# ==============================
if menu == "📊 Dashboard":
    st.title("📊 Dashboard Absensi Guru")

    if df.empty:
        st.warning("Belum ada data")
    else:
        total = len(df)
        hadir = len(df[df["Status"] == "Mengajar"])
        izin = len(df[df["Status"] == "Izin"])
        sakit = len(df[df["Status"] == "Sakit"])

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Data", total)
        c2.metric("Mengajar", hadir)
        c3.metric("Izin", izin)
        c4.metric("Sakit", sakit)

        st.subheader("Data Terbaru")
        st.dataframe(df.sort_values("Tanggal", ascending=False), use_container_width=True)

# ==============================
# DATA ABSENSI
# ==============================
elif menu == "📅 Data Absensi":
    st.title("📅 Data Absensi")

    if df.empty:
        st.warning("Belum ada data")
    else:
        st.dataframe(df, use_container_width=True)

        if role == "Admin":
            st.subheader("🗑️ Hapus Data")
            idx = st.number_input("Index data", min_value=0, max_value=len(df)-1, step=1)

            if st.button("Hapus"):
                df = df.drop(index=idx)
                save_data(df)
                st.success("Data dihapus")
                st.rerun()

# ==============================
# INPUT ABSENSI
# ==============================
elif menu == "✍️ Input Absensi":
    st.title("✍️ Input Absensi")

    if role != "Admin":
        st.error("Hanya admin yang bisa input data")
    else:
        with st.form("form_input"):
            nama = st.text_input("Nama Guru")
            tanggal = st.date_input("Tanggal", date.today())
            status = st.selectbox("Status", [
                "Mengajar", "Sakit", "Izin", "Tanpa Keterangan"
            ])

            submit = st.form_submit_button("Simpan")

            if submit:
                new_data = pd.DataFrame([{
                    "Nama": nama,
                    "Tanggal": tanggal,
                    "Status": status
                }])

                df = pd.concat([df, new_data], ignore_index=True)
                save_data(df)

                st.success("Data berhasil disimpan")
                st.rerun()

# ==============================
# FOOTER
# ==============================
st.sidebar.markdown("---")
st.sidebar.caption("Dashboard Absensi v2 (Interaktif)")
