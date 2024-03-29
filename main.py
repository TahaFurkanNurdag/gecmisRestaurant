from flask import *
from datetime import datetime
import sqlite3
import hashlib
import os  # hashlib sifreleme icin, os upload islemleri icin
# dosya upload işlemleri için dahil edildi
from werkzeug.utils import secure_filename
from datetime import date, timedelta
import calendar  # to check clients days
import shutil  # Backup lib

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
    return (userId, girildiMi, adi)  # fonksiyonun dondurdugu degiskenler


@app.route("/")
def root():
    if 'email' not in session:  # giris yapilmadiysa
        adminMi = 0  # admin mi degiskeni sifir olacak
        session['adminMi'] = adminMi  # bu session icine aktarilacak
    else:
        adminMi = session['adminMi']
    # yukarida olusturulan fonksiyondan degerler cekiliyor
    girildiMi, adi = getLoginDetails()[1:]
    return render_template('root.html', girildiMi=girildiMi, adi=adi, adminMi=adminMi)


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
    session.pop('email', None)  # giris yapan kisiyi hafizadan atma
    return redirect(url_for('root'))  # anasayfaya donus


def is_valid(email, parola, adminMi):  # email ve parola dogru mu kiyasi
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT email, parola, adminMi FROM kullanicilar')
    data = cur.fetchall()
    for row in data:
        if row[0] == email and row[1] == parola:
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
        adres = request.form['adres']
        # html'de doldurulan alanlar degiskenlere aktarildi
        tel = request.form['tel']
        kullaniciAdi = request.form['kullaniciAdi']
        adminMi = request.form['adminMi']

        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute('INSERT INTO kullanicilar (adi,soyadi,email,kullaniciAdi,parola,adres,tel,adminMi) VALUES ( ?,?,?,?,?,?,?,?)',
                            (adi, soyadi, email, kullaniciAdi, parola, adres, tel, adminMi))
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
    else:
        adminMi = session['adminMi']
    if session['adminMi'] == 0:  # bu kisim usttekilerle ayni mantik
        return redirect(url_for('root'))
    userId, girildiMi, adi = getLoginDetails()
    if session['adminMi'] == 1:
        return render_template("sign_up.html", userId=userId, girildiMi=girildiMi, adi=adi, adminMi=adminMi)
    else:
        # giris yaptiysa kaydolma sayfasi acilmaz anasayfaya yonlendirilir
        return redirect(url_for('root'))


def allowed_file(filename):  # fotograf isimlerini duzenli hale getirmek icin
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route("/orderScreenAll")
def orderScreenAll():
    if 'email' not in session:  # giris yapilmadiysa
        adminMi = 0  # admin mi degiskeni sifir olacak
        session['adminMi'] = adminMi  # bu session icine aktarilacak
    else:
        adminMi = session['adminMi']
    if session['adminMi'] == 0:  # bu kisim usttekilerle ayni mantik
        return redirect(url_for('root'))
    if 'email' not in session:  # bu kisim usttekilerle ayni mantik
        return redirect(url_for('loginForm'))
    msg = ""
    userId, girildiMi, adi = getLoginDetails()
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM genelsiparis")
    data = cur.fetchall()  # data from database
    return render_template("all_order_details.html", value=data, userId=userId, girildiMi=girildiMi, adi=adi, msg=msg, adminMi=adminMi)

############## LIST OF PEOPLE ############################
@app.route("/listOfPeople")
def listOfPeople():
    if 'email' not in session:  # giris yapilmadiysa
        adminMi = 0  # admin mi degiskeni sifir olacak
        session['adminMi'] = adminMi  # bu session icine aktarilacak
    else:
        adminMi = session['adminMi']
    if session['adminMi'] == 0:  # bu kisim usttekilerle ayni mantik
        return redirect(url_for('root'))
    if 'email' not in session:  # bu kisim usttekilerle ayni mantik
        return redirect(url_for('loginForm'))
    msg = ""
    userId, girildiMi, adi = getLoginDetails()
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM kullanicilar")
    data = cur.fetchall()  # data from database
    return render_template("list_Of_People.html", value=data, userId=userId, girildiMi=girildiMi, adi=adi, msg=msg, adminMi=adminMi)


@app.route("/deletePersonal", methods=['GET', 'POST'])
def deletePersonal():
    if request.method == "POST":
        id = request.form['id']
        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute(
                    'delete  from kullanicilar where userId=?', (id, ))
                con.commit()  # veritabanina kaydedildi
            except Exception as e:
                con.rollback()
                print(e)
        con.close()
        return redirect(url_for('listOfPeople'))
    else:
        print("error")
        return redirect(url_for('root'))

############## LIST OF FOODS ############################
@app.route("/listOfFoods")
def listOfFoods():
    if 'email' not in session:  # bu kisim usttekilerle ayni mantik
        adminMi = 0
        session['adminMi'] = adminMi
    else:
        adminMi = session['adminMi']
    if 'email' not in session:  # bu kisim usttekilerle ayni mantik
        return redirect(url_for('loginForm'))
    msg = ""
    userId, girildiMi, adi = getLoginDetails()
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM urunler where kategori=1 ")
    data = cur.fetchall()  # data from database
    cur.execute("SELECT * FROM urunler where kategori=2")
    tatlilar = cur.fetchall()
    cur.execute("SELECT * FROM urunler where kategori=3")
    icecekler = cur.fetchall()
    cur.execute("SELECT id FROM kategoriler")
    kategori = cur.fetchall() 

    return render_template("list_Of_foods.html", kategori=kategori,tatlilar=tatlilar, icecekler=icecekler, value=data, userId=userId, girildiMi=girildiMi, adi=adi, msg=msg, adminMi=adminMi)


@app.route("/addItemFood", methods=["GET", "POST"])
def addItemFood():
    if request.method == "POST":
        yemeginAdi = request.form['yemeginAdi']
        yemeginFiyati = request.form['yemeginFiyati']

        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute('''INSERT INTO urunler (isim,fiyat,kategori) VALUES (?,?,1)''',
                            (yemeginAdi, yemeginFiyati))
                conn.commit()  # burada kategori veritabanina ekleniyor
                msg = "Basarili"
            except:
                msg = "Hata olustu"
                conn.rollback()
                return redirect(url_for('root'))
        conn.close()
        print(msg)
        return redirect(url_for('listOfFoods'))
    else:
        return redirect(url_for('root'))


@app.route("/deleteFood", methods=['GET', 'POST'])
def deleteFood():
    if request.method == "POST":
        id = request.form['id']
        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute(
                    'delete  from yemekler where categoryId=?', (id, ))
                con.commit()  # veritabanina kaydedildi
            except Exception as e:
                con.rollback()
                print(e)
        con.close()
        return redirect(url_for('listOfFoods'))
    else:
        print("error")
        return redirect(url_for('root'))


@app.route("/addItemDesert", methods=["GET", "POST"])
def addItemDesert():
    if request.method == "POST":
        tatliniAdi = request.form['tatliniAdi']
        tatliniFiyati = request.form['tatliniFiyati']

        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute('''INSERT INTO tatlilar (isim,fiyat) VALUES (?,?)''',
                            (tatliniAdi, tatliniFiyati))
                conn.commit()  # burada kategori veritabanina ekleniyor
                msg = "Basarili"
            except:
                msg = "Hata olustu"
                conn.rollback()
                return redirect(url_for('root'))
        conn.close()
        print(msg)
        return redirect(url_for('listOfFoods'))
    else:
        return redirect(url_for('root'))


@app.route("/deleteDesert", methods=['GET', 'POST'])
def deleteDesert():
    if request.method == "POST":
        id = request.form['id']
        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute(
                    'delete  from tatlilar where categoryId=?', (id, ))
                con.commit()  # veritabanina kaydedildi
            except Exception as e:
                con.rollback()
                print(e)
        con.close()
        return redirect(url_for('listOfFoods'))
    else:
        print("error")
        return redirect(url_for('root'))


@app.route("/addItemDrinks", methods=["GET", "POST"])
def addItemDrinks():
    if request.method == "POST":
        iceceginAdi = request.form['iceceginAdi']
        iceceginFiyati = request.form['iceceginFiyati']

        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute('''INSERT INTO icecekler (isim,fiyat) VALUES (?,?)''',
                            (iceceginAdi, iceceginFiyati))
                conn.commit()  # burada kategori veritabanina ekleniyor
                msg = "Basarili"
            except:
                msg = "Hata olustu"
                conn.rollback()
                return redirect(url_for('root'))
        conn.close()
        print(msg)
        return redirect(url_for('listOfFoods'))
    else:
        return redirect(url_for('root'))


@app.route("/deleteDrinks", methods=['GET', 'POST'])
def deleteDrinks():
    if request.method == "POST":
        id = request.form['id']
        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute(
                    'delete  from icecekler where categoryId=?', (id, ))
                con.commit()  # veritabanina kaydedildi
            except Exception as e:
                con.rollback()
                print(e)
        con.close()
        return redirect(url_for('listOfFoods'))
    else:
        print("error")
        return redirect(url_for('root'))

############## LIST OF FOODS ############################



############################################# MASALAR 5.12.2019 #####################

@app.route("/tablesScreen")
def tablesScreen():
    if 'email' not in session:  # giris yapilmadiysa
        adminMi = 0  # admin mi degiskeni sifir olacak
        session['adminMi'] = adminMi  # bu session icine aktarilacak
    else:
        adminMi = session['adminMi']
    # yukarida olusturulan fonksiyondan degerler cekiliyor
    girildiMi, adi = getLoginDetails()[1:]
    with sqlite3.connect('database.db') as con:
        try:
            cur = con.cursor()
            cur.execute("SELECT * FROM  masalar")
            allTables = cur.fetchall()
        except:
            msg = "Error occured"
    con.close()

    return render_template('tablesScreen.html', allTables=allTables, girildiMi=girildiMi, adi=adi, adminMi=adminMi)

@app.route("/table")
def table():
    if 'email' not in session:  # giris yapilmadiysa
        adminMi = 0  # admin mi degiskeni sifir olacak
        session['adminMi'] = adminMi  # bu session icine aktarilacak
    else:
        adminMi = session['adminMi']
    # yukarida olusturulan fonksiyondan degerler cekiliyor
    girildiMi, adi = getLoginDetails()[1:]
    with sqlite3.connect('database.db') as con:
        try:
            id_ = request.args.get('id')
            cur = con.cursor()
            print("a")
            cur.execute("select * from (select * from anliksiparis join urunler where urunler.id = anliksiparis.urunId ) where masaId = ? ;", (id_))
            isimler = cur.fetchall() #sipraisid, masaid, urunid, aciklama, id, isim, fiyat, kategori
            print("b")
            cur.execute("SELECT isim, id FROM kategoriler")
            kategoriler = cur.fetchall()
            print("c")
            cur.execute("select max(id) from kategoriler")
            kategori_sayisi = cur.fetchone()
            food_data=[]
            current_sum=sum([i[6] for i in isimler])
            for i in range(1,kategori_sayisi[0]+1):
                cur.execute("SELECT isim,id FROM urunler WHERE kategori=?",(str(i)))
                result = cur.fetchall()
                food_data.append(result)
            print(f"Food Data is: {food_data}")

            cur.execute("SELECT masaIsmi FROM masalar WHERE id=?",(id_))
            masa_adi = str(cur.fetchone())[2:-3]
        except Exception as e:
            print(f"XXXXXXXXXXXXXXXXXXXX: {e}")
    con.close()
    print(f"""Current Sum: {current_sum}
    Kategori Sayısı: {kategori_sayisi}
    ID: {id_}
    Food Data: {food_data}
    Kategoriler: {kategoriler}
    Masa Adı: {masa_adi}
    Isimler: {isimler}""")
    return render_template('table.html', current_sum=current_sum, kategori_sayisi=kategori_sayisi, id_=id_, food_data=food_data, kategoriler=kategoriler, masa_adi=masa_adi, girildiMi=girildiMi, adi=adi, adminMi=adminMi , isimler=isimler)


@app.route("/addToTable", methods=['GET', 'POST'])
def addToTable():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    elif request.method == "POST":
        id_ = request.args.get('id')
        urunId = request.args.get('urunId')
        aciklama = request.form['aciklama']
        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                print(id_ , urunId, aciklama)
                cur.execute("INSERT INTO anliksiparis (masaId, urunId, aciklama) VALUES (?, ?, ?)", (id_ , urunId, aciklama))
            except Exception as e:
                con.rollback()
                print(f"Error occured: {e}")
        con.close()
    else:
        return redirect(url_for('root'))
    return redirect(url_for('table', id=id_))


@app.route("/removeFromTable", methods=['GET', 'POST'])
def removeFromTable():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    id_ = request.args.get('id')
    rowNum = request.args.get('rowNum')
    with sqlite3.connect('database.db') as con:
        try:
            cur = con.cursor()
            print(f"rowNum is: {rowNum}, {type(rowNum)}")
            print(f"List-wise: {list(rowNum)}")
            cur.execute("DELETE FROM anliksiparis WHERE siparisId = ?", [rowNum])
            con.commit()
        except Exception as e:
            con.rollback()
            print(f"Error: {e}")
    con.close()
    return redirect(url_for('table', id=id_))


@app.route("/clearTable", methods=['GET', 'POST'])
def clearTable():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    id_ = request.args.get('id')
    with sqlite3.connect('database.db') as con:
        try:
            cur = con.cursor()
            cur.execute("DELETE FROM anliksiparis WHERE masaId = ?", id_)
            con.commit()
        except Exception as e:
            con.rollback()
            print(f"Error: {e}")
    con.close()
    return redirect(url_for('tablesScreen'))


@app.route("/mutfak")
def mutfak():
    if 'email' not in session:  # giris yapilmadiysa
        adminMi = 0  # admin mi degiskeni sifir olacak
        session['adminMi'] = adminMi  # bu session icine aktarilacak
    else:
        adminMi = session['adminMi']
    # yukarida olusturulan fonksiyondan degerler cekiliyor
    girildiMi, adi = getLoginDetails()[1:]
    with sqlite3.connect('database.db') as con:
        try:
            cur = con.cursor()
            cur.execute("select siparisId,masaId , isim , aciklama  from (select * from anliksiparis join urunler where anliksiparis.urunId = urunler.id) ")
            value = cur.fetchall()
        except Exception as e:
            print(f"Error: {e}")
    con.close()
    return render_template('mutfak.html', value=value, girildiMi=girildiMi, adi=adi, adminMi=adminMi)


@app.route("/checkout")
def checkout():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    email = session['email']
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = ?", (email, ))
        userId = cur.fetchone()[0]
        try:
            cur.execute("DELETE FROM kart;")
            conn.commit()
            msg = "removed successfully"
        except:
            conn.rollback()
            msg = "error occured"
    conn.close()
    return redirect(url_for('cart'))


@app.route("/stockTracker")
def stockTracker():
    if 'email' not in session:  # giris yapilmadiysa
        adminMi = 0  # admin mi degiskeni sifir olacak
        session['adminMi'] = adminMi  # bu session icine aktarilacak
    else:
        adminMi = session['adminMi']
    # yukarida olusturulan fonksiyondan degerler cekiliyor
    girildiMi, adi = getLoginDetails()[1:]
    return render_template('stockTracker.html', girildiMi=girildiMi, adi=adi, adminMi=adminMi)


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


if __name__ == '__main__':
    # 0.0.0.0 localhostta açık sunmak için. Bilgisayarın ipsine 5000. porttan bağlanılıyor
    app.run(debug=True, host='0.0.0.0' , port=5000)
