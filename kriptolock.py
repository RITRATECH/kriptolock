import os
import sys
import base64
import hashlib
import qrcode
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from getpass import getpass
from datetime import datetime
from io import BytesIO


# === Fungsi pembentukan key dari password ===
def generate_key_from_password(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),  # perbaikan di sini
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

# === Fungsi untuk enkripsi file ===
def encrypt_file(filename, password=None, output_filename=None):
    if password is None:
        password = getpass("[🔑] Masukkan password untuk dekripsi: ")

    try:
        with open(filename, "rb") as f:
            salt = f.read(16)
            encrypted = f.read()

        key = generate_key_from_password(password, salt)
        fernet = Fernet(key)
        decrypted = fernet.decrypt(encrypted)

        output_path = output_filename if output_filename else filename.replace(".encrypted", "") + ".decrypted"

        with open(output_path, "wb") as f:
            f.write(decrypted)

        print(f"[🔓] File berhasil didekripsi menjadi '{output_path}'")
        write_log("DECRYPT", filename, "SUCCESS")

        # Hitung hash asli dan simpan
        original_hash = hash_file(filename)
        with open(filename + ".hash", "w") as h:
            h.write(original_hash)
        
        print(f"[🔒] File '{filename}' berhasil dienkripsi menjadi '{output_path}'")
        write_log("ENCRYPT", filename, "SUCCESS")
        
        #  Auto-Self-Destruct
        try:
            os.remove(filename)
            print(f"[💥] File asli '{filename}' telah dihapus otomatis.")
            write_log("DELETE", filename, "AUTO-SELF-DESTRUCT")
        except Exception as e:
            print(f"[⚠️] Gagal menghapus file asli: {e}")
            write_log("DELETE", filename, f"ERROR: {e}")

    except Exception as e:
        print(f"[❌] Gagal mengenkripsi: {e}")
        write_log("ENCRYPT", filename, f"ERROR: {str(e)}")

    
# === Fungsi untuk dekripsi file ===
def decrypt_file(filename, password=None, output_filename=None):
    if password is None:
        password = getpass("[🔑] Masukkan password untuk dekripsi: ")

    try:
        with open(filename, "rb") as f:
            salt = f.read(16)
            encrypted = f.read()

        key = generate_key_from_password(password, salt)
        fernet = Fernet(key)
        decrypted = fernet.decrypt(encrypted)

        output_path = output_filename if output_filename else filename.replace(".encrypted", "") + ".decrypted"
        with open(output_path, "wb") as f:
            f.write(decrypted)

        print(f"[🔓] File berhasil didekripsi menjadi '{output_path}'")
        write_log("DECRYPT", filename, "SUCCESS")

        # === Cek integritas file ===
        try:
            hash_file_original = os.path.splitext(filename)[0] + ".hash"
            if os.path.exists(hash_file_original):
                with open(hash_file_original, "r") as f:
                    original_hash = f.read().strip()
                decrypted_hash = hash_file(output_path)

                if decrypted_hash == original_hash:
                    print("[🛡️] Integritas OK: File cocok dengan aslinya")
                    write_log("INTEGRITY", output_path, "MATCH")
                else:
                    print("[⚠️] Integritas GAGAL: File TIDAK cocok!")
                    write_log("INTEGRITY", output_path, "MISMATCH")
            else:
                print("[ℹ️] File hash tidak ditemukan, melewatkan cek integritas.")
        except Exception as e:
            print(f"[⚠️] Gagal cek integritas: {e}")
            write_log("INTEGRITY", output_path, f"ERROR: {e}")

    except Exception as e:
        print(f"[❌] Gagal mendekripsi: {e}")
        write_log("DECRYPT", filename, f"ERROR: {str(e)}")


# === Fungsi untuk  Enkripsi & Dekripsi Seluruh Folder ===
def encrypt_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith(".encrypted"):
                continue  # Lewati file yang sudah terenkripsi
            filepath = os.path.join(root, filename)
            print(f"[📂] Mengenkripsi: {filepath}")
            encrypt_file(filepath)

def decrypt_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if not filename.endswith(".encrypted"):
                continue  # Lewati file yang bukan terenkripsi
            filepath = os.path.join(root, filename)
            print(f"[📂] Mendekripsi: {filepath}")
            decrypt_file(filepath)
            
# === Fungsi untuk logging ===
def write_log(action, filename, status):
    with open("kriptolock.log", "a") as log:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log.write(f"[{now}] [{action.upper()}] {filename} → {status}\n")
        
# === Fungsi untuk hash ===
def hash_file(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def generate_file_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(4096):
            hasher.update(chunk)
    return hasher.hexdigest()
    

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

# === Fungsi untuk  Secure Delete ===
def secure_delete(filepath):
    try:
        if not os.path.isfile(filepath):
            return

        length = os.path.getsize(filepath)

        with open(filepath, "ba+", buffering=0) as f:
            f.seek(0)
            f.write(os.urandom(length))  # timpa dengan byte acak

        os.remove(filepath)  # hapus file setelah ditimpa
        print(f"[🧠] Secure delete: '{filepath}' berhasil dihapus dengan aman.")
        write_log("SECURE_DELETE", filepath, "SUCCESS")

    except Exception as e:
        print(f"[⚠️] Gagal secure delete: {e}")
        write_log("SECURE_DELETE", filepath, f"ERROR: {e}")

# === CLI Interface ===
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="KriptoLock CLI")

    parser.add_argument("mode", choices=["encrypt", "decrypt", "qr"])
    parser.add_argument("target", nargs="?", help="File atau folder atau password untuk qr")
    parser.add_argument("extra_files", nargs="*", help="Tambahan file lain jika batch")
    parser.add_argument("--output", help="Nama file hasil output (untuk satu file)")
    parser.add_argument("--password", help="Password untuk enkripsi/dekripsi")

    args = parser.parse_args()

    if args.mode == "qr":
        if not args.target:
            print("Usage: python kriptolock.py qr <password>")
            sys.exit()
        img = generate_qr_from_text(args.target)
        with open("backup_password_qr.png", "wb") as f:
            f.write(img.read())
        print("[✅] QR Code untuk password telah disimpan sebagai 'backup_password_qr.png'")

    else:
        files = [args.target] + args.extra_files
        for target in files:
            if not target:
                continue
            if args.mode == "encrypt":
                if os.path.isdir(target):
                    encrypt_folder(target)
                else:
                    encrypt_file(target, password=args.password, output_filename=args.output)
            elif args.mode == "decrypt":
                if os.path.isdir(target):
                    decrypt_folder(target)
                else:
                    decrypt_file(target, password=args.password, output_filename=args.output)

        