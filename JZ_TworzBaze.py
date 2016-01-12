__author__ = 'laptop1'
import sqlite3


db_path = 'kredyty_hip.db'

def baza():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    #
    # czyszczenie
    #
    try:
        c.execute('''
              DROP TABLE Kredyty
              ''')
    except sqlite3.OperationalError as e:
        print "Blad usuwania tabeli: " + e.message

    try:
        c.execute('''
              DROP TABLE Klienci
              ''')
    except sqlite3.OperationalError as e:
        print "Blad usuwania tabeli: " + e.message

    #
    # Tabele
    #
    c.execute('''
              CREATE TABLE Klienci
              ( klientId INTEGER PRIMARY KEY,
                imie VARCHAR(25) NOT NULL,
                nazwisko VARCHAR(30),
                ulica VARCHAR(30),
                nrDomu VARCHAR(30),
                nrMieszkania VARCHAR(30),
                kodPocztowy VARCHAR(6),
                miasto VARCHAR(30),
                dataUr DATE NOT NULL
              )
              ''')
    c.execute('''
              CREATE TABLE Kredyty
              ( kredytId INTEGER PRIMARY KEY,
                kwota NUMERIC NOT NULL,
                oproc NUMERIC NOT NULL,
                klientId INTEGER,
               FOREIGN KEY(klientId) REFERENCES Klienci(klientId))
              ''')
    conn.close()

baza()