import sqlite3

#Veri tabani acma
conn = sqlite3.connect('database.db')

#Tablolari olusturma
conn.execute('''CREATE TABLE `kullanicilar` (
	`userId`	INTEGER,
	`adi`	TEXT,
	`soyadi`	TEXT,
	`email`	TEXT,
	`kullaniciAdi` TEXT,
	`parola`	TEXT,
	`adres`	TEXT,
	`tel`	TEXT,
	`adminMi`	INTEGER,
	PRIMARY KEY(`userId`)
		)''')

conn.execute('''CREATE TABLE `anliksiparis` (
	`masaId` INTEGER,
	`urunId`	INTEGER,
	`aciklama` TEXT,
	PRIMARY KEY(`masaId`)
		)''')
		
conn.execute('''CREATE TABLE `genelsiparis` (
	`id` INTEGER,
	`urunAdi`	TEXT,
	`urunAdedi`	INTEGER,
	`gelir` INTEGER,
	PRIMARY KEY(`id`)
		)''')
		
		
conn.execute('''CREATE TABLE `urunler` (
	`id`	INTEGER,
	`isim`	TEXT,
	`fiyat` INTEGER,
    `kategori` INTEGER,
	PRIMARY KEY(`id`)
		)''')

conn.execute('''CREATE TABLE `kategoriler` (
	`id`	INTEGER,
    `isim` INTEGER,
	PRIMARY KEY(`id`)
		)''')


		
		
conn.execute('INSERT INTO "main"."kullanicilar" ("userId", "adi", "soyadi", "email", "kullaniciAdi", "parola", "adres", "tel", "adminMi") VALUES (1, "Özgür", "Özbek", "ozgurozbek1@yandex.com", "Admin", "122333", "-" , "05062545050", 1)')
conn.execute('INSERT INTO "main"."kullanicilar" ("userId", "adi", "soyadi", "email", "kullaniciAdi", "parola", "adres", "tel", "adminMi") VALUES (2, "Taha Furkan", "Nurdağ", "tfn@tfn.com","TFN", "tfn", "TFN", "05350363646", 1)')
conn.execute('INSERT INTO "main"."urunler" ("id", "isim", "fiyat", "kategori") VALUES (1, "Makarna", "5.00", 1)')
conn.execute('INSERT INTO "main"."urunler" ("id", "isim", "fiyat", "kategori") VALUES (2, "Baklava", "3.00", 2)')
conn.execute('INSERT INTO "main"."urunler" ("id", "isim", "fiyat", "kategori") VALUES (3, "Su", 1.00, 3)')
conn.execute('INSERT INTO "main"."kategoriler" ("id", "isim") VALUES (1, "Yemekler")')
conn.execute('INSERT INTO "main"."kategoriler" ("id", "isim") VALUES (2, "Tatlilar")')
conn.execute('INSERT INTO "main"."kategoriler" ("id", "isim") VALUES (3, "Icecekler")')
conn.commit()

conn.close()