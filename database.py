import sqlite3

#Veri tabani acma
conn = sqlite3.connect('database.db')

#Tablolari olusturma
conn.execute('''CREATE TABLE `kullanicilar` (
	`userId`	INTEGER,
	`parola`	TEXT,
	`email`	TEXT,
	`adi`	TEXT,
	`soyadi`	TEXT,
	`adres1`	TEXT,
	`adres2`	TEXT,
	`il`	TEXT,
	`ilce`	TEXT,
	`ulke`	TEXT,
	`tel`	TEXT,
	`boy`   INTEGER,
	`kilo`  INTEGER,
	`kayitgunu` DATE,
	`pakettipi` TEXT,
	`ekstrapaketler` TEXT,
	`paketkalangunsayisi` INTEGER,
	`aktifmi`   INTEGER,
	`katilim`   INTEGER,
	`arkadassayisi` INTEGER,
	`odeme`    INTEGER,
	`ogretmenMi`	INTEGER,
	`adminMi`	INTEGER,
	PRIMARY KEY(`userId`)
		)''')

conn.execute('''CREATE TABLE `muhasebe` (
	`id`	INTEGER,
	`price` INTEGER,
	`date`  DATE,
	`explanation` TEXT,
	PRIMARY KEY(`id`)
		)''')
		
conn.execute('''CREATE TABLE `ogretmenler` (
	`id`	INTEGER,
	`ogretmenAdi` TEXT,
	`date`  DATE,
	`pakettipi` TEXT
		)''')
		
conn.execute('''CREATE TABLE `hareketler` (
	`id`	INTEGER,
	`name`	TEXT,
	`description`	TEXT,
	`video`	TEXT,
	PRIMARY KEY(`id`)
		)''')
		
conn.execute('''CREATE TABLE `pakettipi` (
	`id`	INTEGER,
	`paketadi`	TEXT,
	`paketfiyati`	INTEGER,
	`paketaciklamasi` TEXT,
	PRIMARY KEY(`id`)
		)''')

conn.execute('''CREATE TABLE `kategoriler` (
	`categoryId`	INTEGER,
	`isim`	TEXT,
	PRIMARY KEY(`categoryId`)
		)''')

conn.commit()

conn.close()