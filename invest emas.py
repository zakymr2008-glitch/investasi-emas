# emas_investasi.py
import tkinter as tk
from tkinter import messagebox, ttk
from decimal import Decimal, ROUND_HALF_UP, getcontext
import random
import csv
from datetime import datetime

# Preset precision untuk Decimal
getcontext().prec = 28

def D(x):
    # helper untuk membuat Decimal dari float/str dengan pembulatan ke 2 desimal (untuk rupiah)
    return Decimal(str(x))

def money_fmt(d: Decimal):
    return f"Rp {d.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):,}"

def gram_fmt(d: Decimal):
    # 3 desimal untuk gram
    return f"{d.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)} g"

class InvestmentApp:
    def __init__(self, master):
        self.master = master
        master.title("Investasi Emas")
        master.resizable(False, False)

        # State awal
        self.cash = D(100000000)               # saldo awal: Rp 10.000.000
        self.gold_grams = D(0)                # gram emas milik user
        self.price_per_gram = D(1_000_000)    # harga awal: Rp 1.000.000 per gram
        self.day = 1

        # History list (in-memory)
        self.history = []
        self._init_ui()

    def _init_ui(self):
        frm = ttk.Frame(self.master, padding=12)
        frm.grid(row=0, column=0, sticky="nsew")

        # Info frame
        info = ttk.LabelFrame(frm, text="Status")
        info.grid(row=0, column=0, sticky="ew", padx=6, pady=6)

        ttk.Label(info, text="Hari:").grid(row=0, column=0, sticky="w")
        self.lbl_day = ttk.Label(info, text=str(self.day))
        self.lbl_day.grid(row=0, column=1, sticky="w")

        ttk.Label(info, text="Harga / gram:").grid(row=1, column=0, sticky="w")
        self.lbl_price = ttk.Label(info, text=money_fmt(self.price_per_gram))
        self.lbl_price.grid(row=1, column=1, sticky="w")

        ttk.Label(info, text="Saldo:").grid(row=2, column=0, sticky="w")
        self.lbl_cash = ttk.Label(info, text=money_fmt(self.cash))
        self.lbl_cash.grid(row=2, column=1, sticky="w")

        ttk.Label(info, text="Emas (gram):").grid(row=3, column=0, sticky="w")
        self.lbl_gold = ttk.Label(info, text=gram_fmt(self.gold_grams))
        self.lbl_gold.grid(row=3, column=1, sticky="w")

        # Trade frame
        trade = ttk.LabelFrame(frm, text="Transaksi")
        trade.grid(row=1, column=0, sticky="ew", padx=6, pady=6)

        ttk.Label(trade, text="Beli (gram):").grid(row=0, column=0, sticky="w")
        self.entry_buy = ttk.Entry(trade, width=12)
        self.entry_buy.grid(row=0, column=1, sticky="w")
        ttk.Button(trade, text="Beli", command=self.buy_gold).grid(row=0, column=2, padx=6)

        ttk.Label(trade, text="Jual (gram):").grid(row=1, column=0, sticky="w")
        self.entry_sell = ttk.Entry(trade, width=12)
        self.entry_sell.grid(row=1, column=1, sticky="w")
        ttk.Button(trade, text="Jual", command=self.sell_gold).grid(row=1, column=2, padx=6)

        ttk.Button(trade, text="Jual Semua", command=self.sell_all).grid(row=2, column=0, columnspan=3, pady=6, sticky="ew")

        # Market frame
        market = ttk.LabelFrame(frm, text="Pasar")
        market.grid(row=2, column=0, sticky="ew", padx=6, pady=6)
        ttk.Button(market, text="Lewati 1 Hari (simulasi harga)", command=self.advance_day).grid(row=0, column=0, pady=4, sticky="ew")
        ttk.Button(market, text="Simpan riwayat ke CSV", command=self.save_history).grid(row=1, column=0, pady=4, sticky="ew")

        # History frame (table)
        history_frame = ttk.LabelFrame(frm, text="Riwayat Transaksi")
        history_frame.grid(row=3, column=0, sticky="nsew", padx=6, pady=6)
        cols = ("waktu", "aksi", "gram", "harga_per_gram", "total", "saldo", "emas")
        self.tree = ttk.Treeview(history_frame, columns=cols, show="headings", height=8)
        for c in cols:
            self.tree.heading(c, text=c.replace("_", " ").title())
            self.tree.column(c, width=110, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=0, column=1, sticky="ns")

        # Inisialisasi entri history awal
        self._add_history("START", D(0), self.price_per_gram, D(0), self.cash, self.gold_grams)

    def _update_labels(self):
        self.lbl_day.config(text=str(self.day))
        self.lbl_price.config(text=money_fmt(self.price_per_gram))
        self.lbl_cash.config(text=money_fmt(self.cash))
        self.lbl_gold.config(text=gram_fmt(self.gold_grams))

    def _add_history(self, action, grams, price_per_gram, total, cash_after, gold_after):
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = (time, action, f"{grams}", f"{price_per_gram}", f"{total}", f"{cash_after}", f"{gold_after}")
        self.history.append(row)
        # tampil di treeview
        self.tree.insert("", "end", values=(
            time,
            action,
            gram_fmt(grams),
            money_fmt(price_per_gram),
            money_fmt(total),
            money_fmt(cash_after),
            gram_fmt(gold_after),
        ))

    def buy_gold(self):
        val = self.entry_buy.get().strip()
        if not val:
            messagebox.showinfo("Input kosong", "Masukkan jumlah gram yang ingin dibeli.")
            return
        try:
            grams = D(val)
            if grams <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Input salah", "Masukkan angka positif untuk gram.")
            return

        cost = (grams * self.price_per_gram).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if cost > self.cash:
            messagebox.showwarning("Dana tidak cukup", f"Anda perlu {money_fmt(cost)} namun saldo hanya {money_fmt(self.cash)}.")
            return

        self.cash -= cost
        self.gold_grams += grams
        self._add_history("Beli", grams, self.price_per_gram, cost, self.cash, self.gold_grams)
        self._update_labels()
        self.entry_buy.delete(0, tk.END)

    def sell_gold(self):
        val = self.entry_sell.get().strip()
        if not val:
            messagebox.showinfo("Input kosong", "Masukkan jumlah gram yang ingin dijual.")
            return
        try:
            grams = D(val)
            if grams <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Input salah", "Masukkan angka positif untuk gram.")
            return

        if grams > self.gold_grams:
            messagebox.showwarning("Emas tidak cukup", f"Anda hanya memiliki {gram_fmt(self.gold_grams)}.")
            return

        revenue = (grams * self.price_per_gram).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self.gold_grams -= grams
        self.cash += revenue
        self._add_history("Jual", grams, self.price_per_gram, revenue, self.cash, self.gold_grams)
        self._update_labels()
        self.entry_sell.delete(0, tk.END)

    def sell_all(self):
        if self.gold_grams <= 0:
            messagebox.showinfo("Tidak ada emas", "Anda tidak memiliki emas untuk dijual.")
            return
        grams = self.gold_grams
        revenue = (grams * self.price_per_gram).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self.gold_grams = D(0)
        self.cash += revenue
        self._add_history("Jual Semua", grams, self.price_per_gram, revenue, self.cash, self.gold_grams)
        self._update_labels()

    def advance_day(self):
        # Simulasi perubahan harga: persentase perubahan antara -5% dan +5% (dapat diubah)
        pct = Decimal(str(random.uniform(-0.05, 0.05)))
        new_price = (self.price_per_gram * (Decimal(1) + pct)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Mencegah harga <= 0
        if new_price <= 0:
            new_price = D(1000)

        self.price_per_gram = new_price
        self.day += 1
        self._add_history("Market Update", D(0), self.price_per_gram, D(0), self.cash, self.gold_grams)
        self._update_labels()

        # Info singkat
        change_pct = (pct * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        messagebox.showinfo("Pasar", f"Hari {self.day-1} -> {self.day}\nPerubahan harga: {change_pct}%\nHarga sekarang: {money_fmt(self.price_per_gram)}")

    def save_history(self):
        fname = f"riwayat_emas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        try:
            with open(fname, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["waktu", "aksi", "gram", "harga_per_gram", "total", "saldo", "emas"])
                for row in self.history:
                    writer.writerow(row)
            messagebox.showinfo("Sukses", f"Riwayat disimpan ke {fname}")
        except Exception as e:
            messagebox.showerror("Gagal simpan", f"Tidak dapat menyimpan file: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = InvestmentApp(root)
    root.mainloop()
