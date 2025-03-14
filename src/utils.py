"""
Yardımcı fonksiyonlar ve veri güvenliği modülü.
"""
import os
import base64
import platform
import getpass
import socket
import psutil
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import zlib
import shutil

# ===== Sistem Bilgileri Fonksiyonları =====

def get_system_info():
    """Temel sistem bilgilerini al."""
    info = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'platform': platform.system(),
        'platform_release': platform.release(),
        'platform_version': platform.version(),
        'architecture': platform.machine(),
        'processor': platform.processor(),
        'hostname': socket.gethostname(),
        'username': getpass.getuser(),
        'ip_address': get_ip_address(),
        'memory': get_memory_info(),
        'disk': get_disk_info()
    }
    return info

def get_ip_address():
    """Bilgisayarın IP adresini al."""
    try:
        # Dış bağlantı kurmadan IP adresini almak için
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "IP adresi alınamadı"

def get_memory_info():
    """Bellek kullanım bilgilerini al."""
    try:
        memory = psutil.virtual_memory()
        return {
            'total': f"{memory.total / (1024**3):.2f} GB",
            'available': f"{memory.available / (1024**3):.2f} GB",
            'percent_used': f"{memory.percent}%"
        }
    except:
        return "Bellek bilgisi alınamadı"

def get_disk_info():
    """Disk kullanım bilgilerini al."""
    try:
        disk = psutil.disk_usage('/')
        return {
            'total': f"{disk.total / (1024**3):.2f} GB",
            'used': f"{disk.used / (1024**3):.2f} GB",
            'free': f"{disk.free / (1024**3):.2f} GB",
            'percent_used': f"{disk.percent}%"
        }
    except:
        return "Disk bilgisi alınamadı"

def format_system_info(info):
    """Sistem bilgilerini bir dize olarak biçimlendir."""
    lines = [
        "=== Sistem Bilgileri ===",
        f"Zaman Damgası: {info['timestamp']}",
        f"Platform: {info['platform']} {info['platform_release']} ({info['platform_version']})",
        f"Mimari: {info['architecture']}",
        f"İşlemci: {info['processor']}",
        f"Bilgisayar Adı: {info['hostname']}",
        f"Kullanıcı Adı: {info['username']}",
        f"IP Adresi: {info['ip_address']}",
    ]
    
    # Bellek bilgilerini ekle
    if isinstance(info['memory'], dict):
        lines.extend([
            "--- Bellek Bilgileri ---",
            f"Toplam: {info['memory']['total']}",
            f"Kullanılabilir: {info['memory']['available']}",
            f"Kullanım Yüzdesi: {info['memory']['percent_used']}"
        ])
    
    # Disk bilgilerini ekle
    if isinstance(info['disk'], dict):
        lines.extend([
            "--- Disk Bilgileri ---",
            f"Toplam: {info['disk']['total']}",
            f"Kullanılan: {info['disk']['used']}",
            f"Boş: {info['disk']['free']}",
            f"Kullanım Yüzdesi: {info['disk']['percent_used']}"
        ])
    
    lines.append("==========================")
    return "\n".join(lines)

def ensure_directory(directory):
    """Bir dizinin var olduğundan emin ol."""
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

# ===== Şifreleme ve Güvenlik Fonksiyonları =====

def generate_key(password):
    """Şifreleme anahtarı üret."""
    salt = b"static_salt_for_edu"  # Gerçek uygulamada random salt kullanılmalı
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def encrypt_data(data, key):
    """Veriyi şifrele."""
    try:
        f = Fernet(key)
        if isinstance(data, str):
            return f.encrypt(data.encode())
        return f.encrypt(data)
    except Exception as e:
        # Şifreleme başarısız olursa ham veriyi döndür
        if isinstance(data, str):
            return data.encode()
        return data

def decrypt_data(encrypted_data, key):
    """Şifrelenmiş veriyi çöz."""
    try:
        f = Fernet(key)
        return f.decrypt(encrypted_data).decode()
    except Exception as e:
        # Çözme başarısız olursa boş string döndür
        return ""

def secure_delete_file(file_path, passes=3):
    """Dosyayı güvenli bir şekilde sil."""
    if not os.path.exists(file_path):
        return False
        
    try:
        # Dosya boyutunu al
        file_size = os.path.getsize(file_path)
        
        # Dosyayı belirtilen sayıda geçişle üzerine yaz
        for i in range(passes):
            with open(file_path, "wb") as f:
                f.write(os.urandom(file_size))
                f.flush()
                os.fsync(f.fileno())
                
        # Dosyayı sil
        os.remove(file_path)
        return True
    except Exception as e:
        return False

def expand_path(path):
    """Yol içindeki ortam değişkenlerini genişlet."""
    # Windows ortam değişkenlerini destekle
    if '%USERPROFILE%' in path:
        path = path.replace('%USERPROFILE%', os.path.expanduser('~'))
    if '%APPDATA%' in path:
        path = path.replace('%APPDATA%', os.getenv('APPDATA'))
    if '%TEMP%' in path:
        path = path.replace('%TEMP%', os.getenv('TEMP'))
    return os.path.expandvars(path)

def get_log_path(config):
    """Config ve debug durumuna göre log dosyası yolunu belirle."""
    debug_mode = config.getboolean('General', 'debug_mode', fallback=False)
    
    if debug_mode:
        # Debug modunda masaüstüne kaydet
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        return os.path.join(desktop, 'debug_log.txt')
    else:
        # Normal modda güvenli konuma kaydet
        output_file = config.get('Output', 'output_file')
        return expand_path(output_file)

def ensure_log_directory(log_path):
    """Log dizininin var olduğundan emin ol."""
    log_dir = os.path.dirname(log_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    return log_dir

def check_log_rotation(config, log_path):
    """Log dosyası boyutunu kontrol et ve gerekirse rotasyon yap."""
    if not config.getboolean('Output', 'log_rotation', fallback=False):
        return
        
    try:
        max_size = config.getint('Output', 'max_log_size', fallback=10) * 1024 * 1024  # MB to bytes
        if os.path.exists(log_path) and os.path.getsize(log_path) > max_size:
            # Yedek dosya adı oluştur
            backup_path = f"{log_path}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
            # Eski dosyayı yedekle
            os.rename(log_path, backup_path)
            # Güvenli silme aktifse eski dosyayı güvenli sil
            if config.getboolean('Output', 'secure_delete', fallback=False):
                secure_delete_file(backup_path)
    except Exception as e:
        print(f"Log rotasyon hatası: {e}") 

def compress_log_file(file_path, delete_original=True):
    """Log dosyasını sıkıştır."""
    try:
        if not os.path.exists(file_path):
            return False
            
        # Sıkıştırılmış dosya adı
        compressed_path = f"{file_path}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.gz"
        
        # Dosyayı sıkıştır
        with open(file_path, 'rb') as f_in:
            with open(compressed_path, 'wb') as f_out:
                compressed_data = zlib.compress(f_in.read(), level=9)
                f_out.write(compressed_data)
        
        # Orijinal dosyayı sil
        if delete_original:
            if os.path.exists(compressed_path):
                os.remove(file_path)
            
        return True
    except Exception as e:
        print(f"Sıkıştırma hatası: {e}")
        return False

def rotate_logs(config, log_path):
    """Log dosyalarını döndür ve yedekle."""
    try:
        if not config.getboolean('Output', 'log_rotation', fallback=False):
            return
            
        # Maksimum dosya boyutu ve yedek sayısı
        max_size = config.getint('Output', 'max_log_size', fallback=10) * 1024 * 1024
        max_backups = config.getint('Output', 'max_backup_count', fallback=5)
        
        if os.path.exists(log_path) and os.path.getsize(log_path) > max_size:
            # Yedek dosyaları kontrol et
            backup_files = []
            for f in os.listdir(os.path.dirname(log_path)):
                if f.startswith(os.path.basename(log_path)) and f.endswith('.gz'):
                    backup_files.append(os.path.join(os.path.dirname(log_path), f))
            
            # Maksimum yedek sayısını aşıyorsa en eski dosyaları sil
            backup_files.sort()
            while len(backup_files) >= max_backups:
                oldest = backup_files.pop(0)
                if config.getboolean('Output', 'secure_delete', fallback=False):
                    secure_delete_file(oldest)
                else:
                    os.remove(oldest)
            
            # Mevcut log dosyasını sıkıştır
            if config.getboolean('Output', 'compress_logs', fallback=True):
                compress_log_file(log_path)
            else:
                # Sıkıştırma istenmediyse sadece yedekle
                backup_path = f"{log_path}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
                shutil.move(log_path, backup_path)
                
    except Exception as e:
        print(f"Log rotasyon hatası: {e}") 