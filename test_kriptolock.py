import os
import hashlib
import time
from kriptolock import encrypt_file, decrypt_file, write_log, generate_file_hash

TEST_FILE = "testdata.txt"
ENC_FILE = TEST_FILE + ".encrypted"
DEC_FILE = TEST_FILE + ".decrypted"
HASH_FILE = TEST_FILE + ".hash"
PASSWORD = "unittestpass123"

def setup_test_file():
    with open(TEST_FILE, "w") as f:
        f.write("Ini adalah data rahasia untuk unit testing.")
    print("[🧪] Test file dibuat.")

def cleanup():
    for f in [TEST_FILE, ENC_FILE, DEC_FILE, HASH_FILE]:
        if os.path.exists(f):
            os.remove(f)
    print("[🧼] Semua file test dibersihkan.")

def test_encryption_and_decryption():
    print("[🔒] Uji Enkripsi...")
    encrypt_file(TEST_FILE, password=PASSWORD)
    assert os.path.exists(ENC_FILE), "❌ Enkripsi gagal: file .encrypted tidak ditemukan."

    print("[🔓] Uji Dekripsi...")
    decrypt_file(ENC_FILE, password=PASSWORD)
    assert os.path.exists(DEC_FILE), "❌ Dekripsi gagal: file .decrypted tidak ditemukan."

    print("[🧠] Uji Hash...")
    # Ambil hash asli yang disimpan sebelumnya
    with open(TEST_FILE + ".hash", "r") as f:
        hash1 = f.read().strip()

    hash2 = generate_file_hash(DEC_FILE)
    assert hash1 == hash2, "❌ Hash tidak cocok! File hasil dekripsi berbeda dari aslinya."
    print("✅ Enkripsi & Dekripsi berhasil, hash cocok.")

def test_logging():
    print("[📋] Uji Logging...")
    log_file = "kriptolock.log"
    assert os.path.exists(log_file), "❌ File log tidak ditemukan."
    with open(log_file, "r") as f:
        log_data = f.read()
        assert "ENCRYPT" in log_data or "DECRYPT" in log_data, "❌ Log tidak mencatat aksi."

    print("✅ Log tercatat dengan baik.")

if __name__ == "__main__":
    print("\n=== 🧪 Memulai Unit Test KriptoLock ===\n")
    cleanup()
    setup_test_file()
    test_encryption_and_decryption()
    test_logging()
    cleanup()
    print("\n✅ Semua test selesai.\n")
