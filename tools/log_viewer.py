#!/usr/bin/env python3
"""
KeyLogger Pro - Log Görüntüleyici
Log dosyalarını okumak için grafiksel araç.
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk
import traceback

# Modül arama yolunu düzelt
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.utils import generate_key, decrypt_data

class LogViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KeyLogger Pro - Log Görüntüleyici")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Kullanıcı arayüzünü oluştur."""
        # Ana çerçeve
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Üst kontrol alanı
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Dosya seçme
        ttk.Label(control_frame, text="Log Dosyası:").grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        self.file_path_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.file_path_var, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(control_frame, text="Dosya Seç", command=self.select_file).grid(row=0, column=2, padx=5)
        
        # Şifre
        ttk.Label(control_frame, text="Şifre:").grid(row=1, column=0, padx=(0, 5), sticky=tk.W)
        self.password_var = tk.StringVar(value="default_key")
        self.password_entry = ttk.Entry(control_frame, textvariable=self.password_var, show="*", width=20)
        self.password_entry.grid(row=1, column=1, padx=5, sticky=tk.W)
        
        # Şifreyi göster/gizle
        self.show_password_var = tk.BooleanVar()
        ttk.Checkbutton(control_frame, text="Şifreyi göster", variable=self.show_password_var, 
                          command=self.toggle_password_visibility).grid(row=1, column=2, padx=5, sticky=tk.W)
        
        # Şifreleme seçeneği
        self.encrypted_var = tk.BooleanVar(value=False)  # Varsayılan olarak işaretsiz
        ttk.Checkbutton(control_frame, text="Dosya şifrelenmiş", variable=self.encrypted_var).grid(row=2, column=0, columnspan=2, padx=5, sticky=tk.W)
        
        # Oku butonu
        ttk.Button(control_frame, text="Dosyayı Oku", command=self.read_file).grid(row=3, column=1, pady=10)
        
        # Kaydet butonu
        ttk.Button(control_frame, text="Metni Farklı Kaydet", command=self.save_content).grid(row=3, column=2, pady=10)
        
        # İçerik alanı
        content_frame = ttk.LabelFrame(main_frame, text="Log İçeriği")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        self.content_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, width=80, height=20)
        self.content_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Durum çubuğu
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_var.set("Hazır - Dosya seçin ve 'Dosya şifrelenmiş' seçeneğini uygun şekilde ayarlayın")
    
    def toggle_password_visibility(self):
        """Şifre görünürlüğünü değiştir."""
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")
    
    def select_file(self):
        """Dosya seçme dialoku göster."""
        file_path = filedialog.askopenfilename(
            title="Log Dosyasını Seçin",
            filetypes=(("Tüm Dosyalar", "*.*"), ("DAT Dosyaları", "*.dat"), ("Metin Dosyaları", "*.txt"))
        )
        if file_path:
            self.file_path_var.set(file_path)
            self.status_var.set(f"Dosya seçildi: {os.path.basename(file_path)}")
            
            # Dosya uzantısına göre şifreleme seçeneğini otomatik ayarla
            if file_path.lower().endswith('.dat'):
                self.encrypted_var.set(True)
            else:
                self.encrypted_var.set(False)
    
    def read_file(self):
        """Seçilen dosyayı oku ve içeriği göster."""
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showerror("Hata", "Lütfen bir log dosyası seçin")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("Hata", "Seçilen dosya bulunamadı")
            return
        
        password = self.password_var.get()
        encrypted = self.encrypted_var.get()
        
        self.status_var.set("Dosya okunuyor...")
        self.root.update_idletasks()
        
        try:
            # Önce dosya boyutunu kontrol et
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                messagebox.showwarning("Uyarı", "Seçilen dosya boş")
                self.content_text.delete(1.0, tk.END)
                self.status_var.set("Boş dosya")
                return
                
            content = read_file(file_path, encrypted, password)
            
            # İçerik boş mu kontrol et
            if not content or content.strip() == "":
                if encrypted:
                    messagebox.showwarning("Uyarı", "Dosya içeriği okunamadı. Dosya şifrelenmiş mi? Şifre doğru mu?")
                    self.status_var.set("Dosya içeriği okunamadı - Şifreleme ayarlarını kontrol edin")
                else:
                    messagebox.showwarning("Uyarı", "Dosya içeriği boş")
                    self.status_var.set("Dosya içeriği boş")
                return
                
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(tk.END, content)
            self.status_var.set("Dosya başarıyla okundu")
        except Exception as e:
            error_details = traceback.format_exc()
            messagebox.showerror("Hata", f"Dosya okunamadı: {str(e)}\n\nDetaylar:\n{error_details}")
            self.status_var.set(f"Hata: {str(e)}")
    
    def save_content(self):
        """İçeriği farklı bir dosyaya kaydet."""
        if not self.content_text.get(1.0, tk.END).strip():
            messagebox.showwarning("Uyarı", "Kaydedilecek içerik yok")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Dosyayı Kaydet",
            defaultextension=".txt",
            filetypes=(("Metin Dosyaları", "*.txt"), ("Tüm Dosyalar", "*.*"))
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.content_text.get(1.0, tk.END))
            messagebox.showinfo("Bilgi", "Dosya başarıyla kaydedildi")
            self.status_var.set(f"Dosya kaydedildi: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya kaydedilemedi: {str(e)}")
            self.status_var.set("Hata: Dosya kaydedilemedi")

def read_file(file_path, encrypted=True, password="default_key"):
    """Log dosyasını oku ve içeriği döndür."""
    try:
        if encrypted:
            # Şifrelenmiş dosyayı oku
            key = generate_key(password)
            with open(file_path, 'rb') as f:
                content = f.read().split(b'\n')
                
            decrypted_content = []
            for line in content:
                if line.strip():
                    try:
                        decrypted_line = decrypt_data(line, key)
                        decrypted_content.append(decrypted_line)
                    except Exception as e:
                        # Şifre çözülemedi - hata bilgisini ekle
                        print(f"Satır çözülemedi: {e}")
                        pass
                        
            if not decrypted_content:
                return "Dosyanın şifresi çözülemedi. Şifre doğru mu? Dosya gerçekten şifrelenmiş mi?"
                    
            return '\n'.join(decrypted_content)
        else:
            # Şifrelenmemiş dosyayı oku
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
    except Exception as e:
        return f"Hata: {str(e)}"

def main():
    """Uygulamayı başlat."""
    root = tk.Tk()
    app = LogViewerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 