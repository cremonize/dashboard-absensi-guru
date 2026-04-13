import streamlit as st
import pandas as pd
from datetime import date
import os

# ==============================
# KONFIGURASI
# ==============================
st.set_page_config(page_title="Dashboard Absensi + Excel", layout="wide")

DB_FILE = "absensi_db.csv"
EXCEL_FILE = "ABSENSI_GURU_v4_fixed.xlsx"

# ==============================
# INIT DATABASE
# ==============================
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["Nama", "Tanggal", "Status"]).to_csv(DB_FILE, index=False)


def load_db():
    return pd.read_csv(DB_FILE, parse_dates=["Tanggal"])


def save_db(df):
    df.to_csv(DB_FILE, index=False)


# ==============================
# LOAD DATA GURU DARI EXCEL
# ==============================
@st.cache_data
def load_guru():
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name="DATA_GURU", header=None)
        df = df.iloc[2:]
        df.columns = ["No", "Nama", "Mapel", "X"]
        return df["Nama"].dropna().tolist()
    except:
        return []


# ==============================
# LOGIN
# ==============================
st.sidebar.title("🔐 Login")
role = st.sidebar.selectbox("Masuk sebagai", ["Admin", "User"])

# ==============================
# MENU
# ==============================
menu = st.sidebar.radio("Menu", [
    "📊 Dashboard",
    "📅 Data Absensi",
    "✍️ Input Absensi",
    "⬇️ Export Excel"
])

# ==============================
# LOAD DATA
# ==============================
df = load_db()
guru_list = load_guru()

# ==============================
# DASHBOARD
# ==============================
if menu == "📊 Dashboard":
    st.title("📊 Dashboard Absensi (Live Input)")

    if df.empty:
        st.warning("Belum ada data")
    else:
        total = len(df)
        hadir = len(df[df["Status"] == "Mengajar"])
        izin = len(df[df["Status"] == "Izin"])
        sakit = len(df[df["Status"] == "Sakit"])

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total", total)
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
            idx = st.number_input("Index", 0, len(df)-1, 0)

            if st.button("Hapus"):
                df = df.drop(index=idx)
                save_db(df)
                st.success("Data dihapus")
                st.rerun()

# ==============================
# INPUT ABSENSI
# ==============================
elif menu == "✍️ Input Absensi":
    st.title("✍️ Input Absensi")

    if role != "Admin":
        st.error("Hanya admin")
    else:
        with st.form("form"):
            nama = st.selectbox("Nama Guru", guru_list if guru_list else ["Manual"])
            tanggal = st.date_input("Tanggal", date.today())
            status = st.selectbox("Status", [
                "Mengajar", "Sakit", "Izin", "Tanpa Keterangan"
            ])

            submit = st.form_submit_button("Simpan")

            if submit:
                new = pd.DataFrame([{
                    "Nama": nama,
                    "Tanggal": tanggal,
                    "Status": status
                }])

                df = pd.concat([df, new], ignore_index=True)
                save_db(df)

                st.success("Tersimpan")
                st.rerun()

# ==============================
# EXPORT KE EXCEL
# ==============================
elif menu == "⬇️ Export Excel":
    st.title("⬇️ Export ke Excel")

    if df.empty:
        st.warning("Tidak ada data")
    else:
        file_name = "absensi_export.xlsx"
        df.to_excel(file_name, index=False)

        with open(file_name, "rb") as f:
            st.download_button("Download Excel", f, file_name=file_name)

# ==============================
# FOOTER
# ==============================
st.sidebar.markdown("---")
st.sidebar.caption("Versi Interaktif + Excel")
