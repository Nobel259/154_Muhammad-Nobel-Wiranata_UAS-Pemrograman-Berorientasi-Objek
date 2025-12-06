import tkinter as tk
from tkinter import ttk, messagebox
from abc import ABC, abstractmethod
import math

# Class InvestasiBase
# Encapsulation:
# - _atribut (protected) digunakan agar boleh diakses subclass, tapi tidak secara bebas oleh luar kelas.
# - __atribut (private) digunakan agar nilai return lebih aman dan tidak dapat diubah langsung dari luar.
# Class ini adalah abstract class (tidak bisa dibuat objek langsung) dan menjadi template untuk semua jenis investasi.
class InvestasiBase(ABC):
    def __init__(self, nama, return_min, return_max, risiko):
        self._nama = nama               # Protected 
        self.__return_min = return_min  # Private 
        self.__return_max = return_max  # Private
        self._risiko = risiko           # Protected

    # Setiap produk investasi WAJIB memiliki deskripsi
    @abstractmethod
    def get_deskripsi(self):
        pass

    # Getter nama produk
    def get_nama(self):
        return self._nama

    # Mengembalikan rentang return tahunan
    def get_return_range(self):
        return (self.__return_min, self.__return_max)

    # Mengembalikan rata-rata return
    def get_return_avg(self):
        return (self.__return_min + self.__return_max) / 2

    # Getter risiko
    def get_risiko(self):
        return self._risiko


# Kelas turunan (Inheritance)
# Semua class di bawah mewarisi InvestasiBase dan mengimplementasikan metode get_deskripsi() secara berbeda (Polymorphism).
class ReksaDanaPasarUang(InvestasiBase):
    def __init__(self):
        super().__init__("Reksa Dana Pasar Uang (RDPU)", 3.0, 6.0, "konservatif")

    def get_deskripsi(self):
        return "RDPU cocok untuk investasi jangka pendek dengan risiko rendah. Return stabil 3-6% per tahun."


class ReksaDanaPendapatanTetap(InvestasiBase):
    def __init__(self):
        super().__init__("Reksa Dana Pendapatan Tetap (RDPT)", 6.0, 10.0, "konservatif")

    def get_deskripsi(self):
        return "RDPT cocok untuk investasi jangka menengah dengan risiko rendah-sedang. Return 6-10% per tahun."


class ReksaDanaCampuran(InvestasiBase):
    def __init__(self):
        super().__init__("Reksa Dana Campuran", 8.0, 15.0, "moderat")

    def get_deskripsi(self):
        return "RD Campuran cocok untuk investasi jangka menengah-panjang dengan risiko sedang. Return 8-15% per tahun."


class ReksaDanaSaham(InvestasiBase):
    def __init__(self):
        super().__init__("Reksa Dana Saham", 12.0, 25.0, "agresif")

    def get_deskripsi(self):
        return "RD Saham cocok untuk investasi jangka panjang dengan risiko tinggi. Return potensial 12-25% per tahun."


# RecommendationNode
# untuk membuat struktur tree rekomendasi investasi. Setiap node menyimpan: objek investasi + skor kecocokan.
class RecommendationNode:
    def __init__(self, investasi, skor):
        self.investasi = investasi   # Objek investasi
        self.skor = skor             # Skor kecocokan
        self.children = []           # Node turunan

    def add_child(self, child):
        self.children.append(child)


# KalkulatorInvestasi
# Class logic utama untuk:
# 1. Menghitung return yang diperlukan
# 2. Memilih investasi sesuai profil risiko
# 3. Menentukan rekomendasi terbaik
# 4. Membuat rekomendasi alternatif bila target tidak realistis
class KalkulatorInvestasi:
    def __init__(self):
        # Daftar produk investasi yang tersedia
        self.__daftar_investasi = [
            ReksaDanaPasarUang(),
            ReksaDanaPendapatanTetap(),
            ReksaDanaCampuran(),
            ReksaDanaSaham()
        ]

    # Menghitung return per tahun yang dibutuhkan agar modal awal mencapai target
    def hitung_return_dibutuhkan(self, modal_awal, target, tahun):
        if modal_awal >= target:
            return 0
        return ((target / modal_awal) ** (1 / tahun) - 1) * 100

    # Mengembalikan list investasi sesuai tingkat risiko user
    def get_investasi_by_profil(self, profil_risiko):
        mapping = {
            "konservatif": ["konservatif"],
            "moderat": ["konservatif", "moderat"],
            "agresif": ["konservatif", "moderat", "agresif"]
        }
        return [inv for inv in self.__daftar_investasi if inv.get_risiko() in mapping.get(profil_risiko, [])]

    # Proses inti yang menghasilkan rekomendasi investasi terbaik
    def cari_rekomendasi(self, modal_awal, target, tahun, profil_risiko):
        return_dibutuhkan = self.hitung_return_dibutuhkan(modal_awal, target, tahun)
        investasi_sesuai = self.get_investasi_by_profil(profil_risiko)

        # Membuat root tree rekomendasi
        root = RecommendationNode(None, 0)

        rekomendasi_utama = None
        skor_terbaik = float('-inf')

        # Hitung kecocokan setiap produk
        for inv in investasi_sesuai:
            ret_min, ret_max = inv.get_return_range()

            # Jika produk mampu menghasilkan return cukup
            if return_dibutuhkan <= ret_max:
                skor = 100 - abs(return_dibutuhkan - inv.get_return_avg())
                node = RecommendationNode(inv, skor)
                root.add_child(node)

                # Produk dengan skor tertinggi menjadi rekomendasi utama
                if skor > skor_terbaik:
                    skor_terbaik = skor
                    rekomendasi_utama = inv

        return {
            "return_dibutuhkan": return_dibutuhkan,
            "rekomendasi_utama": rekomendasi_utama,
            "tree": root,
            "realistis": rekomendasi_utama is not None
        }

    # Jika target tidak realistis → beri beberapa alternatif
    def buat_rekomendasi_alternatif(self, modal_awal, target, tahun_awal, profil_awal):
        alternatif = []

        # Alternatif 1: naikkan profil risiko
        profil_map = {"konservatif": "moderat", "moderat": "agresif"}
        if profil_awal in profil_map:
            profil_baru = profil_map[profil_awal]
            hasil = self.cari_rekomendasi(modal_awal, target, tahun_awal, profil_baru)
            if hasil["realistis"]:
                alternatif.append({
                    "jenis": "Ubah Profil Risiko",
                    "detail": f"Profil: {profil_baru.title()}",
                    "investasi": hasil["rekomendasi_utama"],
                    "tahun": tahun_awal,
                    "return": hasil["return_dibutuhkan"]
                })

        # Alternatif 2: Tambah waktu investasi
        for tambah_tahun in [2, 5, 10]:
            tahun_baru = tahun_awal + tambah_tahun
            hasil = self.cari_rekomendasi(modal_awal, target, tahun_baru, profil_awal)
            if hasil["realistis"]:
                alternatif.append({
                    "jenis": "Perpanjang Waktu",
                    "detail": f"Waktu: {tahun_baru} tahun",
                    "investasi": hasil["rekomendasi_utama"],
                    "tahun": tahun_baru,
                    "return": hasil["return_dibutuhkan"]
                })
                break  # Ambil satu saja

        # Alternatif 3: kombinasi kedua cara
        if profil_awal == "konservatif":
            hasil = self.cari_rekomendasi(modal_awal, target, tahun_awal + 3, "moderat")
            if hasil["realistis"]:
                alternatif.append({
                    "jenis": "Kombinasi",
                    "detail": f"Profil: Moderat, Waktu: {tahun_awal + 3} tahun",
                    "investasi": hasil["rekomendasi_utama"],
                    "tahun": tahun_awal + 3,
                    "return": hasil["return_dibutuhkan"]
                })

        return alternatif


# Class GUI AplikasiReksaDana 
# Menangani:
# - tampilan GUI
# - input user
# - memanggil kalkulator investasi
# - menampilkan hasil
class AplikasiReksaDana:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulasi Rekomendasi Reksa Dana")
        self.root.geometry("900x800")
        self.root.resizable(False, False)

        # Objek kalkulator sebagai LOGIC backend
        self.kalkulator = KalkulatorInvestasi()

        self.setup_ui()

    # Membuat seluruh elemen UI
    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#2290ff", height=80)
        header.pack(fill=tk.X)

        title = tk.Label(header, text="Simulasi Reksa Dana",
                         font=("Arial", 24, "bold"), bg="#2290ff", fg="white")
        title.pack(pady=20)

        # Frame utama
        main = tk.Frame(self.root, bg="#ecf0f1")
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Input section
        input_frame = tk.LabelFrame(
            main, text="Data Investasi", font=("Arial", 12, "bold"), bg="#ecf0f1", padx=15, pady=15)
        input_frame.pack(fill=tk.X, pady=(0, 20))

        # Modal awal
        tk.Label(input_frame, text="Modal Awal (Rp):",
                 bg="#ecf0f1", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=8)
        self.modal_entry = tk.Entry(input_frame, font=("Arial", 10), width=30)
        self.modal_entry.grid(row=0, column=1, pady=8, padx=10)

        # Target
        tk.Label(input_frame, text="Target Nominal (Rp):",
                 bg="#ecf0f1", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=8)
        self.target_entry = tk.Entry(input_frame, font=("Arial", 10), width=30)
        self.target_entry.grid(row=1, column=1, pady=8, padx=10)

        # Tahun
        tk.Label(input_frame, text="Jangka Waktu (Tahun):",
                 bg="#ecf0f1", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, pady=8)
        self.tahun_entry = tk.Entry(input_frame, font=("Arial", 10), width=30)
        self.tahun_entry.grid(row=2, column=1, pady=8, padx=10)

        # Profil Risiko (Radio Button)
        tk.Label(input_frame, text="Profil Risiko:",
                 bg="#ecf0f1", font=("Arial", 10)).grid(row=3, column=0, sticky=tk.W, pady=8)
        self.profil_var = tk.StringVar(value="konservatif")

        profil_frame = tk.Frame(input_frame, bg="#ecf0f1")
        profil_frame.grid(row=3, column=1, sticky=tk.W, padx=10)

        tk.Radiobutton(profil_frame, text="Konservatif",
                       variable=self.profil_var, value="konservatif", bg="#ecf0f1").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(profil_frame, text="Moderat",
                       variable=self.profil_var, value="moderat", bg="#ecf0f1").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(profil_frame, text="Agresif",
                       variable=self.profil_var, value="agresif", bg="#ecf0f1").pack(side=tk.LEFT, padx=5)

        # Tombol
        btn_frame = tk.Frame(main, bg="#ecf0f1")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Cari Rekomendasi", command=self.proses_rekomendasi,
                  bg="#00c150", fg="white", font=("Arial", 12, "bold"),
                  padx=20, pady=10, cursor="hand2").pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Reset", command=self.reset_form,
                  bg="#b41200", fg="white", font=("Arial", 12, "bold"),
                  padx=20, pady=10, cursor="hand2").pack(side=tk.LEFT, padx=5)

        # Hasil rekomendasi
        self.result_frame = tk.LabelFrame(
            main, text="Hasil Rekomendasi", font=("Arial", 12, "bold"), bg="#ecf0f1", padx=15, pady=15)
        self.result_frame.pack(fill=tk.BOTH, expand=True)

        self.result_text = tk.Text(
            self.result_frame, height=15, font=("Arial", 10),
            wrap=tk.WORD, bg="white", relief=tk.SOLID, borderwidth=1
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(self.result_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.result_text.yview)

    # Validasi input user dari Entry
    def validasi_input(self):
        try:
            modal = float(self.modal_entry.get())
            target = float(self.target_entry.get())
            tahun = int(self.tahun_entry.get())

            if modal <= 0 or target <= 0 or tahun <= 0:
                raise ValueError("Nilai harus positif")

            if modal >= target:
                messagebox.showwarning(
                    "Perhatian", "Modal awal sudah mencapai atau melebihi target!")
                return None

            return modal, target, tahun
        except ValueError:
            messagebox.showerror(
                "Error", "Input tidak valid! Pastikan semua data diisi dengan benar.")
            return None

    # Proses utama: mengambil input -> menghitung -> menampilkan hasil
    def proses_rekomendasi(self):
        data = self.validasi_input()
        if not data:
            return

        modal, target, tahun = data
        profil = self.profil_var.get()

        # Panggil kalkulator
        hasil = self.kalkulator.cari_rekomendasi(
            modal, target, tahun, profil)

        # Bersihkan hasil lama
        self.result_text.delete(1.0, tk.END)

        # Header hasil
        self.result_text.insert(tk.END, "=" * 80 + "\n")
        self.result_text.insert(tk.END, "HASIL ANALISIS INVESTASI\n")
        self.result_text.insert(tk.END, "=" * 80 + "\n\n")

        # Tampilkan informasi input
        self.result_text.insert(tk.END, f"Modal Awal        : Rp {modal:,.0f}\n")
        self.result_text.insert(tk.END, f"Target            : Rp {target:,.0f}\n")
        self.result_text.insert(tk.END, f"Jangka Waktu      : {tahun} tahun\n")
        self.result_text.insert(tk.END, f"Profil Risiko     : {profil.title()}\n")
        self.result_text.insert(tk.END, f"Return Dibutuhkan : {hasil['return_dibutuhkan']:.2f}% per tahun\n\n")

        # Jika target realistis
        if hasil["realistis"]:
            inv = hasil["rekomendasi_utama"]

            self.result_text.insert(tk.END, "TARGET REALISTIS!\n\n", "success")
            self.result_text.insert(tk.END, f"Rekomendasi: {inv.get_nama()}\n", "bold")
            self.result_text.insert(tk.END, f"{inv.get_deskripsi()}\n\n")

            # Hitung estimasi hasil skenario konservatif/optimis
            ret_min, ret_max = inv.get_return_range()
            estimasi_min = modal * ((1 + ret_min / 100) ** tahun)
            estimasi_max = modal * ((1 + ret_max / 100) ** tahun)

            self.result_text.insert(tk.END, "Estimasi Hasil:\n")
            self.result_text.insert(
                tk.END, f"  - Skenario konservatif ({ret_min}%): Rp {estimasi_min:,.0f}\n")
            self.result_text.insert(
                tk.END, f"  - Skenario optimis ({ret_max}%): Rp {estimasi_max:,.0f}\n")

        # Jika tidak realistis
        else:
            self.result_text.insert(tk.END, "TARGET TIDAK REALISTIS!\n\n", "warning")
            self.result_text.insert(
                tk.END, f"Return {hasil['return_dibutuhkan']:.2f}% per tahun terlalu tinggi untuk profil risiko Anda.\n\n")

            alternatif = self.kalkulator.buat_rekomendasi_alternatif(
                modal, target, tahun, profil)

            if alternatif:
                self.result_text.insert(
                    tk.END, "REKOMENDASI ALTERNATIF:\n\n", "bold")
                for i, alt in enumerate(alternatif, 1):
                    self.result_text.insert(tk.END, f"{i}. {alt['jenis']}\n")
                    self.result_text.insert(tk.END, f"   {alt['detail']}\n")
                    self.result_text.insert(
                        tk.END, f"   Produk: {alt['investasi'].get_nama()}\n")
                    self.result_text.insert(
                        tk.END, f"   Return dibutuhkan: {alt['return']:.2f}% per tahun\n")
                    self.result_text.insert(
                        tk.END, f"   {alt['investasi'].get_deskripsi()}\n\n")
            else:
                self.result_text.insert(
                    tk.END, "Saran: Tambah modal awal atau turunkan target.\n")

        # Styling tag text
        self.result_text.tag_config(
            "success", foreground="#27ae60", font=("Arial", 12, "bold"))
        self.result_text.tag_config(
            "warning", foreground="#e74c3c", font=("Arial", 12, "bold"))
        self.result_text.tag_config("bold", font=("Arial", 11, "bold"))

    # Reset form input
    def reset_form(self):
        self.modal_entry.delete(0, tk.END)
        self.target_entry.delete(0, tk.END)
        self.tahun_entry.delete(0, tk.END)
        self.profil_var.set("konservatif")
        self.result_text.delete(1.0, tk.END)


# MAIN PROGRAM
if __name__ == "__main__":
    root = tk.Tk()
    app = AplikasiReksaDana(root)
    root.mainloop()