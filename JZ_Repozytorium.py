from numpy.lib.function_base import kaiser

__author__ = 'laptop1'
# -*- coding: utf-8 -*-

import sqlite3
import numpy
import JZ_TworzBaze
from datetime import datetime
#
#
db_path = 'kredyty_hip.db'

##
class RepositoryException(Exception):
    def __init__(self, message, *errors):
        Exception.__init__(self, message)
        self.errors = errors

#
class Klient():


    def __init__(self, klientId, imie=None, nazwisko=None, ulica=None, nrDomu=None, nrMieszkania=None, kodPocztowy=None, miasto=None, dataUr=None, kredyty=[]):
        self.klientId = klientId
        self.imie = imie
        self.nazwisko = nazwisko
        self.ulica = ulica
        self.nrDomu = nrDomu
        self.nrMieszkania = nrMieszkania
        self.kodPocztowy = kodPocztowy
        self.miasto = miasto
        self.dataUr = dataUr
        self.kredyty = kredyty

    def __repr__(self):
        return "<Klient(kilentId='%s', imie='%s', nazwisko='%s', ulica=%s, nrDomu=%s, nrMieszkania=%s, kodPocztowy=%s, miasto='%s, data_ur='%s', kredyty='%s')>" % (
                    self.klientId, str(self.imie), str(self.nazwisko), str(self.ulica), str(self.nrDomu), str(self.nrMieszkania),
                    str(self.kodPocztowy), str(self.miasto), str(self.dataUr), str(self.kredyty)
                )


class Kredyt():

    def __init__(self, kredytId, kwota, oproc, klientId=None):
        self.kredytId = kredytId
        self.kwota = kwota
        self.oproc = oproc
        self.klientId = klientId

    def __repr__(self):
        return "<Kredyty(kredytId='%s', kwota='%s', oproc='%s', idkl='%s')>" % (
                    self.kredytId, str(self.kwota), str(self.oproc), str(self.klientId)
                )



class Repository():
    def __init__(self):
        try:
            self.conn = self.get_connection()
        except Exception as e:
            raise RepositoryException('GET CONNECTION:', *e.args)
        self._complete = False

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        self.close()

    def complete(self):
        self._complete = True

    def get_connection(self):
        return sqlite3.connect(db_path)

    def close(self):
        if self.conn:
            try:
                if self._complete:
                    self.conn.commit()
                else:
                    self.conn.rollback()
            except Exception as e:
                raise RepositoryException(*e.args)
            finally:
                try:
                    self.conn.close()
                except Exception as e:
                    raise RepositoryException(*e.args)

class KlienciRepository(Repository):

    def add(self, klient):
        try:
            c = self.conn.cursor()
            c.execute('''INSERT INTO Klienci (klientId, imie, nazwisko, ulica, nrDomu, nrMieszkania, kodPocztowy, miasto, dataUr)
                         VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (
                            klient.klientId, str(klient.imie), str(klient.nazwisko), str(klient.ulica),
                            klient.nrDomu, klient.nrMieszkania, klient.kodPocztowy, klient.miasto, klient.dataUr
                        )
                    )
            if klient.kredyty:
                for kredyt in klient.kredyty:
                    try:
                        c.execute('INSERT INTO Kredyty ( kwota, oproc, klientId) VALUES(?,?,?)',
                                        ( kredyt.kwota, kredyt.oproc, klient.klientId)
                                )
                    except Exception as e:
                        print(e.message)
                        raise RepositoryException('blad dodawania kredytu: %s, Dla klienta: %s' %
                                                    (str(kredyt), str(klient.klientId))
                                                )

        except Exception as e:

            raise RepositoryException('blad dodawania klienta %s: %s' % (str(klient), e.message))

    def delete(self, klient):
        try:
            c = self.conn.cursor()
            c.execute('DELETE FROM Kredyty WHERE klientId=?', (klient.klientId,))
            c.execute('DELETE FROM Klienci WHERE klientId=?', (klient.klientId,))
        except Exception as e:
            raise RepositoryException('blad usuwania klienta %s' % str(klient))

    def getKlientById(self, klientId):
        try:
            c = self.conn.cursor()
            c.execute("SELECT * FROM Klienci WHERE klientId=?", (klientId,))
            kl_row = c.fetchone()
            klient = Klient(klientId=klientId)
            if kl_row == None:
                klient=None
            else:
                klient.imie = kl_row[1]
                klient.nazwisko = kl_row[2]
                klient.ulica = kl_row[3]
                klient.nrDomu = kl_row[4]
                klient.nrMieszkania = kl_row[5]
                klient.kodPocztowy = kl_row[6]
                klient.miasto = kl_row[7]
                klient.dataUr = kl_row[8]
                c.execute("SELECT * FROM Kredyty WHERE klientId=? order by kredytId", (klientId,))
                kl_items_rows = c.fetchall()
                items_list = []
                for item_row in kl_items_rows:
                    item = Kredyt(kredytId=item_row[0], kwota=item_row[1], oproc=item_row[2], klientId=item_row[3])
                    items_list.append(item)
                klient.kredyty=items_list
        except Exception as e:
            raise RepositoryException('blad pobierania klienta po ID: %s %s' % (str(klientId), e.message))
        return klient

    def update(self, klient):
        try:
            istniejacy = self.getKlientById(klient.klientId)
            if istniejacy != None:
                self.delete(istniejacy)
            self.add(klient)
        except Exception as e:
            raise RepositoryException('Blad aktualizowania klienta %s' % str(klient))

    def sredniaKwotaKredytuKlienta(self, klientId):

        klient = self.getKlientById(klientId)
        if klient==None or klient.kredyty==None or len(klient.kredyty)==0:
            return None

        kwoty = []
        for kredyt in klient.kredyty:
            kwoty.append(kredyt.kwota)

        return numpy.mean(kwoty)

class KredytyRepository(Repository):

    def sredniaKwotaWszystkichKredytow(self):
        try:
            c = self.conn.cursor()
            c.execute("SELECT kwota FROM Kredyty")
            kwoty_rows = c.fetchall()
            kwoty_list = []
            for row in kwoty_rows:
                    kwoty_list.append(row[0]),

            if len(kwoty_list)==0:
                return None
            else:
                return numpy.mean(kwoty_list)

        except Exception as e:
            raise RepositoryException('blad pobierania kwot kredytow po ID: %s' % e.message)


if __name__ == '__main__':

    try:
        JZ_TworzBaze.baza()
    except Exception as e:
        print("Blad tworzenia bazy %s " % e.message)

    try:
        with KlienciRepository() as klient_repository:
            print("###### DODAWANIE KLIENTOW - START ######")
            klient_repository.add(
                Klient(klientId = 1, imie = "Anna", nazwisko = "Nowak", ulica = "Kolejowa", nrDomu="12a", nrMieszkania="11",
                       kodPocztowy="80-180",  miasto = "Gdansk", dataUr = '21-04-1974',
                       kredyty = [
                            Kredyt(kredytId=None, kwota=250000, oproc=5.1 ),
                            Kredyt(kredytId=None, kwota=15400, oproc=14.1 ),
                            Kredyt(kredytId=None, kwota=2700, oproc=18.3 )
                       ]
                    )
                )
            klient_repository.add(
                Klient(klientId = 2, imie = "Tomasz", nazwisko = "Kowalski", ulica = "Piotrkowska", nrDomu="1", nrMieszkania="8b",
                       kodPocztowy="82-300",  miasto = "Elblag", dataUr = '11-11-1982',
                       kredyty = [
                            Kredyt(kredytId=None, kwota=310000, oproc=4.14 )
                       ]
                    )
                )
            klient_repository.add(
                Klient(klientId = 3, imie = "Agata", nazwisko = "Paciaciak", ulica = "Przemyska", nrDomu="21", nrMieszkania=None,
                       kodPocztowy="87-100",  miasto = "Torun", dataUr = '21-01-1983',
                       kredyty = [
                            Kredyt(kredytId=None, kwota=3600, oproc=24.8 ),
                            Kredyt(kredytId=None, kwota=2400, oproc=19.14 ),
                            Kredyt(kredytId=None, kwota=1800, oproc=17.83 ),
                            Kredyt(kredytId=None, kwota=1650, oproc=21.03 )
                       ]
                    )
                )
            klient_repository.complete()
            print("###### DODAWANIE KLIENTOW - ZAKONCZONE POMYSLNIE ######")
    except RepositoryException as e:
        print(e)

    try:
        print("");
        print("###### POBIERANIE KLIENTA - START ######")
        print KlienciRepository().getKlientById(1)
        print("###### POBIERANIE KLIENTA - ZAKONCZONE POMYSLNIE ######")
    except Exception as e:
        print(e)

    try:
        print("");
        print("###### AKTUALIZOWANIE KLIENTA - START ######")
        klientId = 1
        klient = KlienciRepository().getKlientById(klientId)
        klient.nrDomu = "33"
        klient.nrMieszkania = "8c"
        klient.kredyty.append(Kredyt(kredytId=None, kwota=3721, oproc=16.9 ))
        with KlienciRepository() as klienci_repository:
            klienci_repository.update(klient)
            klienci_repository.complete()
        print("Klient po aktualizacji: %s " % KlienciRepository().getKlientById(klientId))
        print("###### AKTUALIZOWANIE KLIENTA - ZAKONCZONE POMYSLNIE ######")
    except Exception as e:
        print(e)


    try:
        print("");
        print("###### USUWANIE KLIENTA - START ######")
        klientId = 2
        klient = KlienciRepository().getKlientById(klientId)
        with KlienciRepository() as klienci_repository:
            klienci_repository.delete(klient)
            klienci_repository.complete()
        print("###### USUWANIE KLIENTA - ZAKONCZONE POMYSLNIE ######")
    except Exception as e:
        print(e)



    try:
        print("");
        print("###### SREDNIA KWOTA KREDYTU KLIENTA - START ######")
        klientId = 3
        srednia = KlienciRepository().sredniaKwotaKredytuKlienta(klientId)
        print("klientId: %d srednia kw kred: %.2f" % (klientId, srednia) )
        print("###### SREDNIA KWOTA KREDYTU KLIENTA - ZAKONCZONE POMYSLNIE ######")
    except Exception as e:
        print(e)

    try:
        print("");
        print("###### SREDNIA KWOTA WSZYSTKICH KREDYTOW - START ######")
        print("Srednia kwota kredytow: %.2f" % KredytyRepository().sredniaKwotaWszystkichKredytow())
        print("###### SREDNIA KWOTA WSZYSTKICH KREDYTOW - ZAKONCZONE POMYSLNIE ######")
    except Exception as e:
        print(e)
