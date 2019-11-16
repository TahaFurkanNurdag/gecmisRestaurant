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
	`yemekAdi`	TEXT,
	`yemekAdedi`	INTEGER,
	`icecekAdi`	TEXT,
	`icecekAdedi`	INTEGER,
	`tatliAdi`	TEXT,
	`tatliAdedi`	INTEGER,
	`salataAdi`	TEXT,
	`salataAdedi`	INTEGER,
	`fiyat` INTEGER,
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
		
		
conn.execute('''CREATE TABLE `yemekler` (
	`categoryId`	INTEGER,
	`isim`	TEXT,
	`fiyat` INTEGER,
	PRIMARY KEY(`categoryId`)
		)''')

conn.execute('''CREATE TABLE `tatlilar` (
	`categoryId`	INTEGER,
	`isim`	TEXT,
	`fiyat` INTEGER,
	PRIMARY KEY(`categoryId`)
		)''')

conn.execute('''CREATE TABLE `icecekler` (
	`categoryId`	INTEGER,
	`isim`	TEXT,
	`fiyat` INTEGER,
	PRIMARY KEY(`categoryId`)
		)''')
		
		
conn.execute('INSERT INTO kullanicilar (adi,soyadi,email,kullaniciAdi,parola,adres,tel,adminMi) VALUES ( "a","a","a@a","a","a","a",123,1)')



conn.commit()

conn.close()