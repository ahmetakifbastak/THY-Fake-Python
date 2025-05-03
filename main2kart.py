from tkinter import *
from tkinter import messagebox
import sqlite3
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

screen = Tk()
screen.title("Türk Hava Yolları")


def gönder_şifre(eposta_adresi, sifre):
    try:
        # E-posta gönderme işlemi
        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.starttls()
        mail.login("youremail@gmail.com", "yourpassword")  # Giriş bilgilerinizi buraya yazın
        mesaj = MIMEMultipart()
        mesaj['From'] = "youremail@gmail.com"  # Gönderen e-posta adresi
        mesaj['To'] = eposta_adresi
        mesaj['Subject'] = "Türk Hava Yolları - Şifre Doğrulama"

        body = f"Merhaba, \n\nGirdiğiniz işlem için doğrulama şifreniz: {sifre}\n\nTeşekkürler!"
        mesaj.attach(MIMEText(body, 'plain'))

        mail.sendmail("youremail@gmail.com", eposta_adresi, mesaj.as_string())  # Gönderme işlemi
        mail.quit()
    except Exception as e:
        print(f"E-posta gönderme hatası: {e}")
        messagebox.showerror("Hata", "E-posta gönderilemedi.")


def ödeme_kontrol():
    ödeme_screen = Toplevel(screen)
    ödeme_screen.title("Kullanıcı Ödeme Bölümü")
    ödeme_screen.geometry("400x400")

    def limit_kart_num(entry_text):
        return len(entry_text) <= 16  # En fazla 16 karaktere izin ver

    vcmd = ödeme_screen.register(limit_kart_num)

    label_font = ("Arial", 12)
    entry_width = 250
    entry_height = 30
    x_label = 20
    x_entry = 150

    # Kart Numarası
    Label(ödeme_screen, text="Kart Numarası", font=label_font).place(x=x_label, y=20)
    entry_kartnum = Entry(ödeme_screen, font=label_font, validate="key", validatecommand=(vcmd, "%P"))
    entry_kartnum.place(x=x_entry, y=20, width=entry_width, height=entry_height)

    # Kart Sahibi Adı
    Label(ödeme_screen, text="Kart Sahibi Adı", font=label_font).place(x=x_label, y=70)
    entry_kartisim = Entry(ödeme_screen, font=label_font)
    entry_kartisim.place(x=x_entry, y=70, width=entry_width, height=entry_height)

    # Son Kullanma Tarihi
    Label(ödeme_screen, text="Son Kullanma Tarihi", font=label_font).place(x=x_label, y=120)
    entry_karttarih = Entry(ödeme_screen, font=label_font)
    entry_karttarih.place(x=x_entry, y=120, width=entry_width, height=entry_height)

    # CVV
    Label(ödeme_screen, text="CVV (Güvenlik Kodu)", font=label_font).place(x=x_label, y=170)
    entry_kartsecurity = Entry(ödeme_screen, font=label_font)
    entry_kartsecurity.place(x=x_entry, y=170, width=entry_width, height=entry_height)

    # E-posta
    Label(ödeme_screen, text="E-Posta Adresi", font=label_font).place(x=x_label, y=220)
    entry_eposta = Entry(ödeme_screen, font=label_font)
    entry_eposta.place(x=x_entry, y=220, width=entry_width, height=entry_height)

    def şifre_doğrulama():
        eposta = entry_eposta.get()

        # 6 basamaklı rastgele şifre oluştur
        sifre = str(random.randint(100000, 999999))

        # Şifreyi e-posta adresine gönder
        gönder_şifre(eposta, sifre)

        # Kullanıcıdan şifreyi girmesini iste
        Label(ödeme_screen, text="Doğrulama Şifresi", font=label_font).place(x=x_label, y=270)
        entry_sifre = Entry(ödeme_screen, font=label_font)
        entry_sifre.place(x=x_entry, y=270, width=entry_width, height=entry_height)

        def şifreyi_doğrula():
            if entry_sifre.get() == sifre:
                messagebox.showinfo("Başarılı", "Ödeme başarılı!")
            else:
                messagebox.showerror("Hata", "Yanlış şifre!")

        Button(ödeme_screen, text="Şifreyi Doğrula", font=label_font, command=şifreyi_doğrula).place(x=150, y=310)

    Button(ödeme_screen, text="Şifre Gönder", font=label_font, command=şifre_doğrulama).place(x=150, y=250)


test = Button(screen, text="Ödeme Kontrol", command=ödeme_kontrol)
test.pack()

screen.mainloop()
