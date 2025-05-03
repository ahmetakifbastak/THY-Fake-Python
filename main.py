from tkinter import *
from tkinter import messagebox
import sqlite3
import random
import requests





screen = Tk()
screen.title("Türk Hava Yollari")

photo = PhotoImage(file="assets//anamenuresim.png")
labelPhoto = Label(screen, image=photo)
labelPhoto.pack()

listeKutusu = ""
listelePenceresi = ""

API_KEY = "611ca93c4c578a13efb0b07093b39c8c" 



# Türkçe şehir isimleri ile IATA kodlarını eşleştiriyoruz
iata_kodlari = {
    "istanbul": "IST",
    "ankara": "ESB",
    "izmir": "ADB",
    "antalya": "AYT",
    "londra": "LHR",
    "berlin": "BER",
    "paris": "CDG",
    "viyana": "VIE",
    "new york": "JFK",
    "los angeles": "LAX",
    "frankfurt": "FRA",
    "amsterdam": "AMS"
    # ihtiyaca göre eklenebilir
}



check_vars = []   # her checkbox için IntVar
check_buttons = []  # buton referansları
checkbox_vars = [] 




# Veritabanı bağlantısı ve tablo oluşturma
kullanici_veritabani = sqlite3.connect("kullaniciKaydi2.db")
curr = kullanici_veritabani.cursor()
curr.execute('''CREATE TABLE IF NOT EXISTS kullaniciKaydi2 (
  password TEXT NOT NULL,
  ad TEXT NOT NULL,
  tc TEXT NOT NULL
)''')
kullanici_veritabani.commit()
kullanici_veritabani.close()

def kullanici_giris():
    kullanici_giris = Toplevel(screen)
    kullanici_giris.title("Kullanici Giris Bölümü")
    kullanici_giris.geometry("300x300")
    
    Label(kullanici_giris, text="Ad Soyad:").pack(pady=5)
    entry_ad = Entry(kullanici_giris)
    entry_ad.pack(pady=5)

    Label(kullanici_giris, text="TC Kimlik No:").pack(pady=5)
    entry_tc = Entry(kullanici_giris)
    entry_tc.pack(pady=5)

    Label(kullanici_giris, text="Şifre Oluşturun (şifrenizi unutmayın, gerekli\n işlemlerde kullanılabilir)").pack(pady=5)
    entry_password = Entry(kullanici_giris)
    entry_password.pack(pady=5)

    def kaydet():
        ad = entry_ad.get()
        tc = entry_tc.get()
        password = entry_password.get()

        if not ad or not tc or not password:
            messagebox.showerror("Hata", "Lütfen tüm alanları doldurun!")
            return

        try:
            # Veritabanına bağlantı
            with sqlite3.connect("kullaniciKaydi2.db") as conn:
                cursor = conn.cursor()
            
            # Daha önce kayıt yapılmış mı kontrolü
                cursor.execute("SELECT COUNT(*) FROM kullaniciKaydi2")
                mevcut_kullanici_sayisi = cursor.fetchone()[0]
                if mevcut_kullanici_sayisi >= 1:
                    messagebox.showwarning("Uyarı", "Zaten bir kullanıcı kaydı yapılmış!")
                    return

                cursor.execute("SELECT * FROM kullaniciKaydi2 WHERE tc=?", (tc,))
                if cursor.fetchone():  # TC zaten varsa
                    messagebox.showerror("Hata", "Bu TC kimlik numarası zaten mevcut!")
                    return

                cursor.execute("INSERT INTO kullaniciKaydi2 (ad, tc, password) VALUES (?, ?, ?)", (ad, tc, password))
                conn.commit()

            messagebox.showinfo("Kayıt", "Kullanıcı başarıyla kaydedildi!")
            kullanici_giris.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Hata", f"Veritabanı hatası: {e}")


    kaydetButton = Button(kullanici_giris, text="KAYDET", command=kaydet)
    kaydetButton.pack()





def bilgi_ekrani():
    global listeKutusu
    bilgi_ekrani = Toplevel(screen)
    bilgi_ekrani.title("Hesap Bilgileri")
    bilgi_ekrani.geometry("400x400")

    Label(bilgi_ekrani, text="Kayıtlı Kullanıcılar", font=("Arial", 14, "bold")).pack(pady=10)

    listeKutusu = Listbox(bilgi_ekrani, width=50)
    listeKutusu.pack(pady=10)

    # Veritabanından kullanıcıları getir ve listbox'a ekle
    conn = sqlite3.connect("kullaniciKaydi2.db")
    cursor = conn.cursor()
    cursor.execute("SELECT ad, tc, password FROM kullaniciKaydi2")
    veriler = cursor.fetchall()
    conn.close()

    # Listeyi temizle ve verileri yeniden ekle
    listeKutusu.delete(0, END)
    for veri in veriler:
        ad, tc, password = veri
        listeKutusu.insert(END, f"Ad: {ad} - TC: {tc} - Password: {password}")

    # Silme butonu
    silButton = Button(bilgi_ekrani, text="Seçili Kaydı Sil", command=sil)
    silButton.pack(pady=5)
    verileri_yenile()




def verileri_yenile():
    conn = sqlite3.connect("kullaniciKaydi2.db")
    cursor = conn.cursor()
    cursor.execute("SELECT ad, tc, password FROM kullaniciKaydi2")
    veriler = cursor.fetchall()
    conn.close()

    listeKutusu.delete(0, END)
    for veri in veriler:
        ad, tc, password = veri
        listeKutusu.insert(END, f"Ad: {ad} - TC: {tc} - Password: {password}")


def sil():
    secilen = listeKutusu.curselection()
    if not secilen:
        messagebox.showerror("Hata", "Lütfen silmek için bir kullanıcı seçin!")
        return

    secili_veri = listeKutusu.get(secilen[0])
    try:
        # TC bilgisini ayıkla
        tc = secili_veri.split(" - ")[1].replace("TC: ", "")
    except IndexError:
        messagebox.showerror("Hata", "Seçilen veri formatı hatalı.")
        return

    cevap = messagebox.askokcancel("Sil", f"TC {tc} olan kullanıcıyı silmek istiyor musunuz?")
    if cevap:
        try:
            conn = sqlite3.connect("kullaniciKaydi2.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM kullaniciKaydi2 WHERE tc=?", (tc,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Başarılı", f"TC {tc} olan kullanıcı silindi.")
            verileri_yenile()  # Listeyi güncelle
        except Exception as e:
            messagebox.showerror("Hata", f"Silme işlemi başarısız oldu: {e}")





def cikis():
    cevap = messagebox.askokcancel("Çıkış", "Çıkmak istediğinize emin misiniz?")
    if cevap:
        screen.quit()




# bilet alma section



# --- Değişkenler ---
x1 = IntVar()
x2 = IntVar()
x3 = IntVar()
x4 = IntVar()
password_var = StringVar()

# --- Resimleri global tanımla ---
img1 = PhotoImage(file="assets/logo.png")





secilen_ucuslar = []
ucus_verileri = []



def arama_yap():
    for cb in check_buttons:
        cb.destroy()
    check_buttons.clear()
    check_vars.clear()

    sorgu = search_entry.get()
    try:
        nereden_tr, nereye_tr = sorgu.split("-")
        nereden_tr = nereden_tr.strip().lower()
        nereye_tr = nereye_tr.strip().lower()

        if nereden_tr in iata_kodlari and nereye_tr in iata_kodlari:
            nereden = iata_kodlari[nereden_tr]
            nereye = iata_kodlari[nereye_tr]
        else:
            result_label.config(text="Şehirlerden biri tanınmadı.")
            return

        url = f"http://api.aviationstack.com/v1/flights?access_key={API_KEY}&dep_iata={nereden}&arr_iata={nereye}"
        response = requests.get(url)
        data = response.json()

        if "data" in data and data["data"]:
            result_label.config(text="")  # önceki mesajları temizle
            for flight in data["data"][:5]:
                airline = flight["airline"]["name"]
                flight_number = flight["flight"]["iata"]
                departure = flight["departure"]["airport"]
                arrival = flight["arrival"]["airport"]
                text = f"{airline} | {flight_number} → {departure} - {arrival}"

                var = IntVar()
                cb = Checkbutton(checkbox_frame, text=text, variable=var, font=("Arial", 12), anchor="w", justify=LEFT)
                cb.pack(anchor="w", padx=10, pady=2)

                check_vars.append(var)
                check_buttons.append(cb)
                ucus_verileri.append(flight)  # bura onemli
        else:
            result_label.config(text="Uçuş bulunamadı.")
    except Exception as e:
        result_label.config(text=f"Hata: {str(e)}")

def sifre_ile_onayla():
    global secilenler
    girilen_sifre = password_var.get()

    try:
        conn = sqlite3.connect("kullaniciKaydi2.db")
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM kullaniciKaydi2 LIMIT 1")  # İlk kullanıcıyı al
        sonuc = cursor.fetchone()
        conn.close()

        if not sonuc:
            result_label.config(text="❌ Kayıtlı kullanıcı bulunamadı.", fg="red")
            return

        kayitli_sifre = sonuc[0]
        if girilen_sifre != kayitli_sifre:
            result_label.config(text="❌ Şifre yanlış!", fg="red")
            return

        # Seçilen uçuşları al
        secilenler = []
        for i, var in enumerate(check_vars):
            if var.get() == 1:
                secilenler.append(ucus_verileri[i])  # artık metin değil, uçuş verisi

        if len(secilenler) == 0:
            result_label.config(text="❗ Lütfen bir uçuş seçin.", fg="red")
        elif len(secilenler) > 1:
            result_label.config(text="❗ Lütfen sadece bir uçuş seçin.", fg="red")
        else:
            result_label.config(text="✅ Uçuş seçildi", fg="green")
            
            # Global listeyi güncelle
            secilen_ucuslar.clear()
            secilen_ucuslar.extend(secilenler)

            # Koltuk seçim penceresini aç
            open_flight_details(secilenler[0])
        
            # Uçuş detaylarını aç (isteğe bağlı, sadece uçuş bilgisi değil, koltuk seçimini önce yapabiliriz)
            # open_flight_details(secilenler[0])

    except Exception as e:
        result_label.config(text=f"Hata: {e}", fg="red")



        






def bilet_alma():
    
    global search_entry, checkbox_frame, result_label

    bilet_alma = Toplevel(screen)
    bilet_alma.title("Bilet Alma")
    bilet_alma.geometry("600x600")

    Label(bilet_alma, text="Nereden - Nereye (örn: İstanbul - Londra)", font=("Arial", 14)).pack(pady=10)

    search_entry = Entry(bilet_alma, font=("Arial", 14))
    search_entry.pack(pady=5)

    Button(bilet_alma, text="Ara", font=("Arial", 14), command=arama_yap, bg="blue", fg="white").pack(pady=5)

    checkbox_frame = Frame(bilet_alma)
    checkbox_frame.pack(pady=10)

    #Button(bilet_alma, text="Seçimi Onayla", command=secilenleri_goster, bg="green", fg="white").pack(pady=5)
    # Şifre girişi
    Label(bilet_alma, text="Şifre giriniz:", font=("Arial", 14)).pack(pady=(20, 5))
    Entry(bilet_alma, textvariable=password_var, show="*", font=("Arial", 14)).pack()
    Button(bilet_alma, text="Onayla", command=sifre_ile_onayla, font=("Arial", 14), bg="green", fg="white").pack(pady=10)

    result_label = Label(bilet_alma, text="", font=("Arial", 12), justify=LEFT)
    result_label.pack(pady=10)






onceki_buton = None  # İlk başta buton yok
secilen_koltuk = StringVar(value="")  # Başlangıçta seçilen koltuk yok

dolu_koltuklar = ["A2", "B3", "C1"]  # Örnek dolu koltuklar

"""
def koltuk_sec():
    global secilen_koltuk, onceki_buton
    koltuk_penceresi = Toplevel()
    koltuk_penceresi.title("Koltuk Seçimi")
    koltuk_penceresi.geometry("400x400")

    Label(koltuk_penceresi, text="Bir koltuk seçin:", font=("Arial", 14)).pack(pady=10)

    secilen_koltuk = StringVar(value="")

    koltuk_butonlari = {}
    koltuklar = []

    def koltuk_tikla(koltuk_no, buton):
        global onceki_buton
        if onceki_buton:
            onceki_buton.config(bg="SystemButtonFace")  # önceki seçimi sıfırla
        secilen_koltuk.set(koltuk_no)
        buton.config(bg="lightgreen")
        onceki_buton = buton

    # Koltukları oluştur
    for i in range(5):
        for j in range(4):
            koltuk_no = f"{chr(65+i)}{j+1}"
            koltuklar.append(koltuk_no)

            btn_state = DISABLED if koltuk_no in dolu_koltuklar else NORMAL
            btn_color = "gray" if koltuk_no in dolu_koltuklar else "SystemButtonFace"

            btn = Button(koltuk_penceresi, text=koltuk_no, width=5, height=2,
                         bg=btn_color, state=btn_state)
            btn.place(x=60*j + 40, y=50*i + 50)

            if btn_state == NORMAL:
                btn.config(command=lambda no=koltuk_no, b=btn: koltuk_tikla(no, b))

            koltuk_butonlari[koltuk_no] = btn

    # Rastgele koltuk seçme
    def rastgele_koltuk():
        bos_koltuklar = [k for k in koltuklar if k not in dolu_koltuklar and k in koltuk_butonlari]
        if secilen_koltuk.get() == "" and bos_koltuklar:
            rastgele = random.choice(bos_koltuklar)
            btn = koltuk_butonlari.get(rastgele)
            if btn:
                koltuk_tikla(rastgele, btn)
                Label(koltuk_penceresi, text=f"Rastgele seçilen koltuk: {rastgele}", font=("Arial", 14), fg="green").pack(pady=10)
        else:
            Label(koltuk_penceresi, text="Bütün koltuklar dolu!", font=("Arial", 14), fg="red").pack(pady=10)

    # Rastgele koltuk seçme butonu
    rastgele_button = Button(koltuk_penceresi, text="Rastgele Koltuk Seç", command=rastgele_koltuk, font=("Arial", 14), bg="yellow")
    rastgele_button.place(x=50,y=300)

    # Uçuş bilgileri butonunu düzelt
    ucus_bilgileri = Button(koltuk_penceresi, text="Uçuş Bilgileri", command=lambda: open_flight_details(flight_data), font=("Arial", 14), bg="yellow")
    ucus_bilgileri.place(x=50,y=350)  # Konumunu değiştirdim
"""

def open_flight_details(flight_data):
    print(flight_data)
    flight_window = Toplevel()  # 'screen' yerine 'koltuk_penceresi' kullanmanız gerekebilir
    flight_window.title("Uçuş Bilgileri")
    flight_window.geometry("500x400")

    airline = flight_data["airline"]["name"]
    flight_number = flight_data["flight"]["iata"]
    departure_airport = flight_data["departure"]["airport"]
    departure_time = flight_data["departure"]["scheduled"]
    arrival_airport = flight_data["arrival"]["airport"]
    arrival_time = flight_data["arrival"]["scheduled"]

    # Koltuk numarasını secilen_koltuk'tan alıyoruz
    koltuk_numara = secilen_koltuk.get()

    # Uçuş bilgilerini yazdırma
    Label(flight_window, text=f"Havayolu: {airline}", font=("Arial", 14)).pack(pady=5)
    Label(flight_window, text=f"Uçuş Numarası: {flight_number}", font=("Arial", 14)).pack(pady=5)
    Label(flight_window, text=f"Kalkış: {departure_airport}", font=("Arial", 14)).pack(pady=5)
    Label(flight_window, text=f"Kalkış Zamanı: {departure_time}", font=("Arial", 14)).pack(pady=5)
    Label(flight_window, text=f"Varış: {arrival_airport}", font=("Arial", 14)).pack(pady=5)
    Label(flight_window, text=f"Varış Zamanı: {arrival_time}", font=("Arial", 14)).pack(pady=5)
    Label(flight_window, text=f"Koltuk Numara: {koltuk_numara}", font=("Arial", 14)).pack(pady=5)

    #Button(flight_window, text="Koltuk Seç", command=koltuk_sec, font=("Arial", 14), bg="blue", fg="white").pack(pady=20)


    







# Menü
menuCubugu = Menu(screen)

anaMenu = Menu(menuCubugu, tearoff=0)
menuCubugu.add_cascade(label="Temel İşlemler", menu=anaMenu)
anaMenu.add_command(label="Çikis    ALT+F4", command=cikis)

hesapMenu = Menu(menuCubugu, tearoff=0)
menuCubugu.add_cascade(label="Hesap Bilgileri", menu=hesapMenu)
hesapMenu.add_command(label="Bilgileri Gör", command=bilgi_ekrani)

biletler = Menu(menuCubugu,tearoff=0)
menuCubugu.add_cascade(label="Biletler", menu=biletler)
biletler.add_command(label="Bilet Al",command=bilet_alma)

admin = Menu(menuCubugu,tearoff=0)
menuCubugu.add_cascade(label="Admin Control", menu=admin)
#biletler.add_command(label="Bilet Ekleme",command=admin_panel)


anaMenu.add_command(label="Hesap Ekle", command=kullanici_giris)
anaMenu.add_separator()

screen.config(menu=menuCubugu)
screen.mainloop()
