import streamlit as st
import base64
import os
import hashlib
import tempfile
import qrcode
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from io import BytesIO


st.set_page_config(page_title="🔐 KriptoLock GUI", layout="centered")

st.title("🔐 KriptoLock GUI – Enkripsi / Dekripsi File")
st.markdown("Drag & drop file, masukkan password, lalu pilih aksi.")

# === Helper untuk hash
def hash_file_bytes(data):
    sha256 = hashlib.sha256()
    sha256.update(data)
    return sha256.hexdigest()

# === Generate key from password
def generate_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

# === ENKRIPSI ===
def encrypt_bytes(data, password):
    salt = os.urandom(16)
    key = generate_key(password, salt)
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    return salt + encrypted, hash_file_bytes(data)

# === DEKRIPSI ===
def decrypt_bytes(data, password):
    salt = data[:16]
    encrypted = data[16:]
    key = generate_key(password, salt)
    fernet = Fernet(key)
    decrypted = fernet.decrypt(encrypted)
    return decrypted, hash_file_bytes(decrypted)

# === Fungsi untuk buat QR dari teks ===
def generate_qr_from_text(text):
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=2
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

# === Fungsi untuk Parse Log ===
def load_logs(log_path="kriptolock.log"):
    logs = []
    try:
        with open(log_path, "r") as f:
            for line in f:
                try:
                    parts = line.strip().split("] ")
                    timestamp = parts[0].replace("[", "")
                    action = parts[1].replace("[", "").replace("]", "")
                    filename, status = parts[2].split(" → ")
                    logs.append({
                        "Timestamp": timestamp,
                        "Action": action,
                        "File": filename,
                        "Status": status
                    })
                except:
                    continue
    except FileNotFoundError:
        logs = []
    return logs

# === UI Upload
uploaded_files = st.file_uploader("🗂️ Upload satu atau lebih file", type=None, accept_multiple_files=True)


# === UI Password
password = st.text_input("🔑 Masukkan Password", type="password")
if password:
    st.subheader("📦 Backup Password sebagai QR Code")
    qr_image = generate_qr_from_text(password)
    st.image(qr_image, caption="Scan QR untuk backup password", use_column_width=False)
    st.download_button("⬇️ Download QR Code", data=qr_image, file_name="kriptolock_password_qr.png", mime="image/png")

# === Tombol Proses
col1, col2 = st.columns(2)

if uploaded_files and password:
    for uploaded_file in uploaded_files:
        file_bytes = uploaded_file.read()
        filename = uploaded_file.name

        st.markdown(f"### 📄 {filename}")
        col1, col2 = st.columns(2)

        with col1:
            if st.button(f"🔒 Encrypt {filename}", key="encrypt"+filename):
                result, file_hash = encrypt_bytes(file_bytes, password)
                st.success(f"✅ {filename} berhasil dienkripsi.")
                st.download_button("⬇️ Download .encrypted", data=result, file_name=filename + ".encrypted", key="dlenc"+filename)
                st.code(f"SHA256: {file_hash}")

        with col2:
            if st.button(f"🔓 Decrypt {filename}", key="decrypt"+filename):
                try:
                    result, file_hash = decrypt_bytes(file_bytes, password)
                    st.success(f"✅ {filename} berhasil didekripsi.")
                    st.download_button("⬇️ Download .decrypted", data=result, file_name=filename.replace(".encrypted", ".decrypted"), key="dldec"+filename)
                    st.code(f"SHA256: {file_hash}")
                except Exception as e:
                    st.error(f"❌ Gagal dekripsi: {e}")

else:
    st.info("⬆️ Silakan upload file dan isi password terlebih dahulu.")

st.markdown("## 📊 Log Activity Dashboard")

logs = load_logs()
if not logs:
    st.info("Belum ada log yang tercatat.")
else:
    import pandas as pd
    df = pd.DataFrame(logs)

    # 🔍 Filter
    col1, col2 = st.columns(2)
    with col1:
        action_filter = st.selectbox("Filter Aksi", ["All"] + sorted(df["Action"].unique().tolist()))
    with col2:
        search_file = st.text_input("Cari Nama File")

    # Terapkan filter
    filtered_df = df.copy()
    if action_filter != "All":
        filtered_df = filtered_df[filtered_df["Action"] == action_filter]
    if search_file:
        filtered_df = filtered_df[filtered_df["File"].str.contains(search_file)]

    # Tampilkan tabel
    st.dataframe(filtered_df, use_container_width=True)

    # Download tombol
    st.download_button("⬇️ Download log mentah (.log)", data=open("kriptolock.log", "rb"), file_name="kriptolock.log")
    if os.path.exists("log_report.html"):
        st.download_button("⬇️ Download versi HTML", data=open("log_report.html", "rb"), file_name="log_report.html")
