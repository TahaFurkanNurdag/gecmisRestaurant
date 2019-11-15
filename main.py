from flask import *
from datetime import datetime
import sqlite3
import hashlib
import os  # hashlib sifreleme icin, os upload islemleri icin
# dosya upload işlemleri için dahil edildi
from werkzeug.utils import secure_filename
from datetime import date, timedelta
import calendar  # to check clients days
import shutil # Backup lib

app = Flask(__name__)
app.secret_key = 'random string'
# upload edilecek fotograflarin dosya konumu belirlendi
UPLOAD_FOLDER = 'static/uploads'
# upload edilecek fotograflarin uzantilari belirlendi
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def getLoginDetails():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        try:
            if 'email' not in session:  # emaile gore giris yapildi mi? yapilmadiysa alttaki satilar
                girildiMi = False  # girilmedigi icin false
                adi = '!'  # sitede isim goruntulenmeyec
                userId = '!'
            else:  # giris yapildiysa alttaki satirlar
                girildiMi = True  # giris yapildigi icin true
                cur.execute(
                    "SELECT userId, adi FROM kullanicilar WHERE email = ?", (session['email'], ))
                # yukaridaki sorgudan sirasiyla degiskenlere veri cekildi
                userId, adi = cur.fetchone()
        except Exception as e:
            print(e)
    conn.close()  # connection kapatildi
    return (userId, girildiMi,adi)  # fonksiyonun dondurdugu degiskenler


@app.route("/")
def root():
    if 'email' not in session:  # giris yapilmadiysa
        adminMi = 0  # admin mi degiskeni sifir olacak
        session['adminMi'] = adminMi  # bu session icine aktarilacak
    # yukarida olusturulan fonksiyondan degerler cekiliyor
    userId, girildiMi, adi = getLoginDetails()
    return render_template('root.html', girildiMi=girildiMi, adi=adi)


@app.route("/addcategory")  # kategori ekleme sayfasi
def addcategory():
    if 'email' not in session:  # kisi admin degilse yapilacaklar
        adminMi = 0
        session['adminMi'] = adminMi
    if session['adminMi'] == 1:  # kisi adminse yapilacaklar
        userId, girildiMi, adi = getLoginDetails()
        return render_template('package_add.html', girildiMi=girildiMi, adi=adi)
    else:
        return "Bu sayfaya sadece adminler erisebilir..."


# package_add.html icinden bu sayfa cagiriliyor
@app.route("/addcategoryitem", methods=["GET", "POST"])
def addcategoryitem():
    if request.method == "POST":
        paketadi = request.form['paketadi']
        paketfiyati = request.form['paketfiyati']
        paketaciklamasi = request.form['paketaciklamasi']

        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute('''INSERT INTO pakettipi (paketadi,paketfiyati,paketaciklamasi) VALUES (?,?,?)''',
                            (paketadi, paketfiyati, paketaciklamasi,))
                conn.commit()  # burada kategori veritabanina ekleniyor
                msg = "Basarili"
            except:
                msg = "Hata olustu"
                conn.rollback()
                return redirect(url_for('root'))
        conn.close()
        print(msg)
        return redirect(url_for('root'))
    else:
        return redirect(url_for('root'))


@app.route("/loginForm")  # giris sayfasi
def loginForm():
    if 'email' in session:  # kullanici giris yaptiysa anasayfa ekranina yonlendirir
        return redirect(url_for('root'))
    else:
        return render_template('login_page.html', error='')


# login_page.html sayfasindan cagirilir
@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        adminMi = 0
        session['adminMi'] = adminMi
        email = request.form['email']
        parola = request.form['parola']  # email ve parola htmlden alinir
        if is_valid(email, parola, adminMi):
            session['email'] = email
            # giris yapildiginda anasayfaya yonlendirme
            return redirect(url_for('root'))
        else:
            error = 'Geçersiz kullanıcı adı veya şifre!'
            return render_template('login_page.html', error=error)
    else:
        # url'ye login yazilirsa loginForm'a yonlendirme
        return redirect(url_for('loginForm'))


@app.route("/logout")  # cikis ekrani
def logout():
    if 'email' not in session:  # kisi eger giris yapmamissa anasayfaya yonlendirilir
        return redirect(url_for('root'))
    email = session['email']
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT userId FROM kullanicilar WHERE email = ?", (email, ))
        userId = cur.fetchone()[0]  # bu kisim usttekilerle ayni mantik
        try:
            cur.execute("DELETE FROM sepet WHERE sepet.userId = ?", (userId, ))
            conn.commit()  # cikis yaparken sepeti silme
        except:
            conn.rollback()
    conn.close()
    session.pop('email', None)  # giris yapan kisiyi hafizadan atma
    return redirect(url_for('root'))  # anasayfaya donus


def is_valid(email, parola, adminMi):  # email ve parola dogru mu kiyasi
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT email, parola, adminMi FROM kullanicilar')
    data = cur.fetchall()
    for row in data:
        if row[0] == email and row[1] == hashlib.md5(parola.encode()).hexdigest():
            adminMi = row[2]
            session['adminMi'] = adminMi
            return True
    return False


@app.route("/register", methods=['GET', 'POST'])  # sign_up.html'den cagirilir
def register():
    if request.method == 'POST':
        parola = request.form['parola']
        email = request.form['email']
        adi = request.form['adi']
        soyadi = request.form['soyadi']
        adres1 = request.form['adres1']
        adres2 = request.form['adres2']
        ilce = request.form['ilce']
        il = request.form['il']
        ulke = request.form['ulke']
        # html'de doldurulan alanlar degiskenlere aktarildi
        tel = request.form['tel']
        boy = request.form['boy']
        kilo = request.form['kilo']
        kayitgunu = request.form['kayitgunu']
        pakettipi = request.form['pakettipi']
        ekstrapaketler = request.form['ekstrapaketler']
        ogretmenMi = request.form['ogretmenMi']
        aktifmi = request.form['aktifmi']
        arkadassayisi = request.form['arkadassayisi']

        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute('INSERT INTO kullanicilar (parola, email, adi, soyadi, adres1, adres2, ilce, il, ulke, tel,boy,kilo,kayitgunu,pakettipi,ekstrapaketler,paketkalangunsayisi,aktifmi,katilim,arkadassayisi, odeme,ogretmenMi,adminMi) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,0, ?, 0, ?, 30,?,1)', (hashlib.md5(
                    parola.encode()).hexdigest(), email, adi, soyadi, adres1, adres2, ilce, il, ulke, tel, boy, kilo, kayitgunu, pakettipi,ekstrapaketler, aktifmi, arkadassayisi,ogretmenMi))
                con.commit()  # veritabanina kaydedildi

                msg = "Kayıt Başarılı"
            except Exception as e:
                con.rollback()
                msg = "Hata olustu"
                print(e)
        con.close()
        return render_template("login_page.html", error=msg)
    else:
        return redirect(url_for('root'))


@app.route("/registerationForm")  # kaydolma sayfasi
def registrationForm():
    if 'email' not in session:  # bu kisim usttekilerle ayni mantik
        adminMi = 0
        session['adminMi'] = adminMi
    if session['adminMi'] == 0:  # bu kisim usttekilerle ayni mantik
        return redirect(url_for('root'))
    userId, girildiMi, adi = getLoginDetails()
    with sqlite3.connect('database.db') as con:
        try:
            cur = con.cursor()
            cur.execute('SELECT paketadi FROM pakettipi')
            data = cur.fetchall()
        except Exception as e:
            con.rollback()
            msg = "Hata olustu"
            print(e)
    con.close()
    if session['adminMi'] == 1:
        return render_template("sign_up.html", userId=userId, girildiMi=girildiMi, adi=adi, data=data)
    else:
        # giris yaptiysa kaydolma sayfasi acilmaz anasayfaya yonlendirilir
        return redirect(url_for('root'))


def allowed_file(filename):  # fotograf isimlerini duzenli hale getirmek icin
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def parse(data):  # urunleri listelememizde kullandigimiz fonksiyon. birden fazla ayni satir olmasin diye yazildi
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans


@app.route("/clientsDetails")
def clientsDetails():
    if 'email' not in session:  # bu kisim usttekilerle ayni mantik
        adminMi = 0
        session['adminMi'] = adminMi
    if session['adminMi'] == 0:  # bu kisim usttekilerle ayni mantik
        return redirect(url_for('root'))
    if 'email' not in session:  # bu kisim usttekilerle ayni mantik
        return redirect(url_for('loginForm'))
    with sqlite3.connect('database.db') as con:
        try:
            cur = con.cursor()
            cur.execute('SELECT paketadi FROM pakettipi')
            pakettipleri = cur.fetchall()
        except Exception as e:
            con.rollback()
            msg = "Hata olustu"
            print(e)
    con.close()
    userId, girildiMi, adi = getLoginDetails()
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM kullanicilar ORDER BY odeme ASC")
    data = cur.fetchall()  # data from database
    return render_template("clients_details.html", value=data, userId=userId, girildiMi=girildiMi, adi=adi,pakettipleri=pakettipleri)


@app.route("/teachersDetails")
def teachersDetails():
    if 'email' not in session:  # bu kisim usttekilerle ayni mantik
        adminMi = 0
        session['adminMi'] = adminMi
    if session['adminMi'] == 0:  # bu kisim usttekilerle ayni mantik
        return redirect(url_for('root'))
    if 'email' not in session:  # bu kisim usttekilerle ayni mantik
        return redirect(url_for('loginForm'))
    msg=""
    with sqlite3.connect('database.db') as con:
        try:
            cur = con.cursor()
            cur.execute('SELECT paketadi FROM pakettipi')
            pakettipleri = cur.fetchall()
        except Exception as e:
            con.rollback()
            msg = "Hata olustu"
            print(e)
    con.close()
    with sqlite3.connect('database.db') as con:
        try:
            cur = con.cursor()
            cur.execute('SELECT adi FROM kullanicilar where ogretmenMi =1')
            ogretmenAdi = cur.fetchall()
        except Exception as e:
            con.rollback()
            msg = "Hata olustu"
            print(e)
    con.close()
    with sqlite3.connect('database.db') as con:
        try:
            cur = con.cursor()
            cur.execute('SELECT * FROM kullanicilar where ogretmenMi =1')
            ogretmenMi = cur.fetchall()
        except Exception as e:
            con.rollback()
            msg = "Hata olustu"
            print(e)
    con.close()
    userId, girildiMi, adi = getLoginDetails()
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM ogretmenler")
    data = cur.fetchall()  # data from database
    return render_template("teacher_details.html", ogretmenMi=ogretmenMi,ogretmenAdi=ogretmenAdi, value=data, userId=userId, girildiMi=girildiMi, adi=adi, pakettipleri=pakettipleri, msg=msg)


@app.route("/accountingDetails")
def accountingDetails():
    if 'email' not in session:  # bu kisim usttekilerle ayni mantik
        adminMi = 0
        session['adminMi'] = adminMi
    if session['adminMi'] == 0:  # bu kisim usttekilerle ayni mantik
        return redirect(url_for('root'))
    if 'email' not in session:  # bu kisim usttekilerle ayni mantik
        return redirect(url_for('loginForm'))
    userId, girildiMi, adi = getLoginDetails()
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("select * from muhasebe")
    data = cur.fetchall()  # data from database
    cur.execute("select price from muhasebe")
    temp_deger = cur.fetchall()
    con.close()
    deger = []
    for i in range(len(temp_deger)):
        deger.append(int(str(temp_deger[i])[1:-2]))
    deger = sum(deger)

    return render_template("accounting_details.html", value=data, sums=deger, userId=userId, girildiMi=girildiMi, adi=adi)

@app.route("/copyingPage")
def copyingPage():
    if 'email' not in session:  # bu kisim usttekilerle ayni mantik
        adminMi = 0
        session['adminMi'] = adminMi
    if session['adminMi'] == 0:  # bu kisim usttekilerle ayni mantik
        return redirect(url_for('root'))
    if 'email' not in session:  # bu kisim usttekilerle ayni mantik
        return redirect(url_for('loginForm'))
    userId, girildiMi, adi = getLoginDetails()
    return render_template('copyingPage.html', girildiMi=girildiMi, adi=adi)

@app.route("/backupProcedure")
def backupProcedure():
    if 'email' not in session:  # bu kisim usttekilerle ayni mantik
        adminMi = 0
        session['adminMi'] = adminMi
    if session['adminMi'] == 0:  # bu kisim usttekilerle ayni mantik
        return redirect(url_for('root'))
    if 'email' not in session:  # bu kisim usttekilerle ayni mantik
        return redirect(url_for('loginForm'))
    try:
        shutil.copyfile('./database.db', './database_backup.db')
    except Exception as e:
        print(f"Hata oluştu: {e}")
    userId, girildiMi, adi = getLoginDetails()
    return render_template('root.html', girildiMi=girildiMi, adi=adi)

@app.route("/backupAccounting")
def backupAccounting():
    if 'email' not in session:  # bu kisim usttekilerle ayni mantik
        adminMi = 0
        session['adminMi'] = adminMi
    if session['adminMi'] == 0:  # bu kisim usttekilerle ayni mantik
        return redirect(url_for('root'))
    if 'email' not in session:  # bu kisim usttekilerle ayni mantik
        return redirect(url_for('loginForm'))
    userId, girildiMi, adi = getLoginDetails()
    try:
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        cur.execute("select * from muhasebe")
        data = cur.fetchall()  # data from database
        cur.execute("select price from muhasebe")
        temp_deger = cur.fetchall()
        deger = []
        for i in range(len(temp_deger)):
            deger.append(int(str(temp_deger[i])[1:-2]))
        deger = sum(deger)
        textfile = open("accountingBackup.txt","w", encoding="utf-8")
        textfile.write(f"Toplam: {deger};")
        for i in data:
            textfile.write(f"\n{i}")
        textfile.close()
        cur.execute("DELETE FROM muhasebe") # Remove all data
        con.commit()
        con.close()

    except Exception as e:
        print(f"Hata oluştu: {e}")
    userId, girildiMi, adi = getLoginDetails()
    return render_template('root.html', girildiMi=girildiMi, adi=adi)

@app.route("/accountingForm")  # kaydolma sayfasi
def accountingForm():
    if 'email' not in session:  # bu kisim usttekilerle ayni mantik
        adminMi = 0
        session['adminMi'] = adminMi
    if session['adminMi'] == 0:  # bu kisim usttekilerle ayni mantik
        return redirect(url_for('root'))
    if 'email' not in session:  # bu kisim usttekilerle ayni mantik
        return redirect(url_for('loginForm'))
    userId, girildiMi, adi = getLoginDetails()
    return render_template("accounting.html", girildiMi=girildiMi, adi=adi)

@app.route("/accounting", methods=['GET', 'POST'])
def totalAmount():
    if 'email' not in session:  # bu kisim usttekilerle ayni mantik
        adminMi = 0
        session['adminMi'] = adminMi
    if session['adminMi'] == 0:  # bu kisim usttekilerle ayni mantik
        return redirect(url_for('root'))
    if 'email' not in session:  # bu kisim usttekilerle ayni mantik
        return redirect(url_for('loginForm'))
    userId, girildiMi, adi = getLoginDetails()
    if request.method == 'POST':
        price = request.form['price']
        date = request.form['date']
        explanation = request.form['explanation']
        if price and date:
            try:
                print(int(price))
            except Exception as e:
                print(f"Hata {e}, girdi integer değil muhtemelen.")
            with sqlite3.connect('database.db') as con:
                try:
                    cur = con.cursor()
                    cur.execute(
                        'INSERT INTO muhasebe (price,date,explanation) VALUES ( ?, ?,?)', (price, date, explanation))
                    con.commit()  # veritabanina kaydedildi
                    msg = "Kayıt Başarılı"
                except Exception as e:
                    con.rollback()
                    msg = "Hata olustu"
                    print(e)
            con.close()
        else:
            msg = "Kayıt bilgileri eksik"
        return render_template("accounting.html", error=msg, price=price, date=date, girildiMi=girildiMi, adi=adi)
    else:
        return redirect(url_for('root'))

@app.route("/increaseOneMonth", methods=['GET', 'POST'])
def addOneMonthToTheUser():
    if request.method == 'POST':
        no = request.form['no']
        gunsayisi = request.form['odemegunu']
        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute(
                    'update kullanicilar SET  odeme=odeme+ ? where userId = ?', (gunsayisi, no))
                con.commit()  # veritabanina kaydedildi
            except Exception as e:
                con.rollback()
                print(e)
        con.close()
        return redirect(url_for('clientsDetails'))
    else:
        return redirect(url_for('root'))

@app.route("/addExtraPacgage", methods=['GET', 'POST'])
def addExtraPacgage():
    if request.method == 'POST':
        no = request.form['no']
        ekstrapaketler = request.form['ekstrapaketler']
        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute(
                    'update kullanicilar SET  ekstrapaketler=? where userId = ?', (ekstrapaketler, no))
                con.commit()  # veritabanina kaydedildi
            except Exception as e:
                con.rollback()
                print(e)
        con.close()
        return redirect(url_for('clientsDetails'))
    else:
        return redirect(url_for('root'))
        
@app.route("/decreaseOneDay")
def decreaseOneDay():
    if True == True:
        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute(
                    'update kullanicilar SET  odeme=odeme-1 where userId > 1')
                con.commit()  # veritabanina kaydedildi
            except Exception as e:
                con.rollback()
                print(e)
        con.close()
        return redirect(url_for('clientsDetails'))
    else:
        print("error")
        return redirect(url_for('root'))
        
@app.route("/increaseOneDay")
def increaseOneDay():
    if True == True:
        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute(
                    'update kullanicilar SET  odeme=odeme+1 where userId > 1')
                con.commit()  # veritabanina kaydedildi
            except Exception as e:
                con.rollback()
                print(e)
        con.close()
        return redirect(url_for('clientsDetails'))
    else:
        print("error")
        return redirect(url_for('root'))

@app.route("/increaseOne", methods = ['GET', 'POST'])
def increaseOne():
    if request.method == 'POST':
        no = request.form['no']
        gunsayisi = request.form['odemegunu']
        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute('UPDATE kullanicilar SET katilim = katilim + ? WHERE userId = ?',(gunsayisi,no))
                con.commit() #veritabanina kaydedildi
            except  Exception as e:
                con.rollback()
                print (e)
        con.close()
        return redirect(url_for('clientsDetails'))
    else:
        return redirect(url_for('root'))

############################################################################# Teacher Functions ########
@app.route("/addTeacherDetails", methods = ['GET', 'POST'])
def addTeacherDetails():
    if request.method == 'POST':
        id = request.form ['uyeadi']
        ogretmenAdi = request.form['ogretmenAdi']
        date=request.form['date']
        pakettipi = request.form['pakettipi']
        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute('INSERT INTO ogretmenler (id,ogretmenAdi,date,pakettipi) VALUES ( ?,?, ?,?)', (id,ogretmenAdi,date,pakettipi))
                con.commit() #veritabanina kaydedildi
            except  Exception as e:
                con.rollback()
                print (e)
        con.close()
        return redirect(url_for('teachersDetails'))
    else:
        return redirect(url_for('root'))
		
############################################################################# Package Functions ########
@app.route("/increaseOneMonthForExtraPackage", methods=['GET', 'POST'])
def increaseOneMonthForExtraPackage():
    if request.method == 'POST':
        no = request.form['no']
        gunsayisi = request.form['odemegunu']
        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute(
                    'update kullanicilar SET  paketkalangunsayisi=paketkalangunsayisi+ ? where userId = ?', (gunsayisi, no))
                con.commit()  # veritabanina kaydedildi
            except Exception as e:
                con.rollback()
                print(e)
        con.close()
        return redirect(url_for('clientsDetails'))
    else:
        return redirect(url_for('root'))
		
@app.route("/decreaseOneDayForExtraPackage")
def decreaseOneDayForExtraPackage():
    if True == True:
        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute(
                    'update kullanicilar SET  paketkalangunsayisi=paketkalangunsayisi-1 where userId > 1')
                con.commit()  # veritabanina kaydedildi
            except Exception as e:
                con.rollback()
                print(e)
        con.close()
        return redirect(url_for('clientsDetails'))
    else:
        print("error")
        return redirect(url_for('root'))

@app.route("/increaseOneDayForExtraPackage")
def increaseOneDayForExtraPackage():
    if True == True:
        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute(
                    'update kullanicilar SET  paketkalangunsayisi=paketkalangunsayisi+1 where userId > 1')
                con.commit()  # veritabanina kaydedildi
            except Exception as e:
                con.rollback()
                print(e)
        con.close()
        return redirect(url_for('clientsDetails'))
    else:
        print("error")
        return redirect(url_for('root'))

############################################################################# Package Functions ########
@app.route("/accountingMain")
def accountingMain():
    if session['adminMi'] == 1:  # admin paneli eger admin mi degiskeni 1 ise goruntulenecek
        userId, girildiMi, adi = getLoginDetails()  # login detaylari cekildi
        return render_template('accountingMain.html', girildiMi=girildiMi, adi=adi)
    else:
        # eger kisi admin degilse bu yazi ile karsilasacak
        return "Bu sayfaya sadece adminler erisebilir..."


@app.route("/clientMain")
def clientMain():
    if session['adminMi'] == 1:  # admin paneli eger admin mi degiskeni 1 ise goruntulenecek
        userId, girildiMi, adi = getLoginDetails()  # login detaylari cekildi
        return render_template('clientMain.html', girildiMi=girildiMi, adi=adi)
    else:
        # eger kisi admin degilse bu yazi ile karsilasacak
        return "Bu sayfaya sadece adminler erisebilir..."


if __name__ == '__main__':
    # 0.0.0.0 localhostta açık sunmak için. Bilgisayarın ipsine 5000. porttan bağlanılıyor
    app.run(debug=True, host='0.0.0.0')
