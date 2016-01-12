# -*- coding: utf-8 -*-

import JZ_Repozytorium as repository
import JZ_TworzBaze as baza
import sqlite3
import unittest

class RepositoryTest(unittest.TestCase):

    def setUp(self):
        baza.baza()

        conn = sqlite3.connect(baza.db_path)
        c = conn.cursor()
        c.execute('''INSERT INTO Klienci (klientId, imie, nazwisko, ulica, nrDomu, nrMieszkania, kodPocztowy, miasto, dataUr)
                                 VALUES  (1, "Anna", "Nowak", "Kolejowa", "12a", "11", "80-180", "Gdansk", '21-04-1974')''')
        c.execute('''INSERT INTO Kredyty (kredytId, kwota, oproc, klientId)
                                 VALUES  (1, 120000, 4.8, 1)''')
        c.execute('''INSERT INTO Kredyty (kredytId, kwota, oproc, klientId)
                                 VALUES  (2, 200000, 6.3, 1)''')

        c.execute('''INSERT INTO Klienci (klientId, imie, nazwisko, ulica, nrDomu, kodPocztowy, miasto, dataUr)
                                 VALUES  (2, "Agata", "Paciaciak", "Przemyska", "21", "87-100", "Torun", '21-01-1983')''')
        c.execute('''INSERT INTO Kredyty (kredytId, kwota, oproc, klientId)
                                 VALUES  (21, 300000, 1.8, 2)''')
        c.execute('''INSERT INTO Kredyty (kredytId, kwota, oproc, klientId)
                                 VALUES  (22, 400000, 14.6, 2)''')
        c.execute('''INSERT INTO Kredyty (kredytId, kwota, oproc, klientId)
                                 VALUES  (23, 500000, 11.1, 2)''')
        conn.commit()
        conn.close()

    def tearDown(self):
        conn = sqlite3.connect(baza.db_path)
        c = conn.cursor()
        c.execute('DELETE FROM Kredyty')
        c.execute('DELETE FROM Klienci')
        conn.commit()
        conn.close()

    def testGetByIdInstance(self):
        klient = repository.KlienciRepository().getKlientById(1)
        self.assertIsInstance(klient, repository.Klient, "Objekt nie jest klasy Klient")
        self.assertEqual(klient.imie, "Anna", "Imie dla klientId=1 powinno byc Anna ")
        self.assertEqual(len(klient.kredyty), 2, "Ilosc kredytow dla kliendId=1 powinna wynosic 2")

        klient = repository.KlienciRepository().getKlientById(2)
        self.assertIsInstance(klient, repository.Klient, "Objekt nie jest klasy Klient")
        self.assertEqual(klient.nrDomu, "21", "nrDomu dla klientId=2 powinien wynosic 21")
        self.assertIsNone(klient.nrMieszkania, "nrMieszkania dla klientId=2 powinien byc pusty")
        self.assertEqual(len(klient.kredyty), 3, "Ilosc kredytow dla kliendId=2 powinna wynosic 3")

    def testGetByIdNotFound(self):
        self.assertEqual(repository.KlienciRepository.getById(22), None, "Nie powinno byc klienta o ID=22")

    def testZapisOdczyt(self):
        klient_id = 10
        klient_imie = "Piotr"
        klientNazwisko = "Kowalski"
        klientNrDomu = "13"
        klientNrMieszkania = "2c"
        klientUlica = "Warszawska"
        klientKodPocz = "80-120"
        klientMiasto = "Gdansk"
        klientDataUr = '23-07-1984'

        kredytId = 20
        kredytKwota = 123000
        kredytOproc = 4.2


        klient = repository.Klient(klientId = klient_id, imie = klient_imie, nazwisko = klientNazwisko, ulica = klientUlica,
                                   nrDomu=klientNrDomu, nrMieszkania=klientNrMieszkania, kodPocztowy=klientKodPocz,
                                   miasto = klientMiasto, dataUr = klientDataUr,
                                   kredyty=[repository.Kredyt(kredytId=kredytId,kwota=kredytKwota, oproc=kredytOproc)])

        with repository.KlienciRepository() as kl_rep:
            kl_rep.add(klient)
            kl_rep.complete()

        klient2 = repository.KlienciRepository().getKlientById(klient_id)

        self.assertIsInstance(klient2, repository.Klient, "Objekt nie jest klasy Klient")
        self.assertEqual(klient2.imie, klient_imie, "Zly zapis/odczyt: imie")
        self.assertEqual(klient2.nazwisko, klientNazwisko, "Zly zapis/odczyt: nazwisko")
        self.assertEqual(klient2.nrDomu, klientNrDomu, "Zly zapis/odczyt: nrDomu")
        self.assertEqual(klient2.nrMieszkania, klientNrMieszkania, "Zly zapis/odczyt: nrMieszkania")
        self.assertEqual(klient2.kodPocztowy, klientKodPocz, "Zly zapis/odczyt: kodPocztowy")
        self.assertEqual(klient2.miasto, klientMiasto, "Zly zapis/odczyt: miasto")
        self.assertEqual(klient2.dataUr, klientDataUr, "Zly zapis/odczyt: dataUr")
        self.assertEqual(klient2.kredyty[0].kwota, kredytKwota, "Zly zapis/odczyt: kredytKwota")
        self.assertEqual(klient2.kredyty[0].oproc, kredytOproc, "Zly zapis/odczyt: kredytOproc")


    def testSredniaKredytowKlienta(self):
        oczekiwana = 160000;
        srednia = repository.KlienciRepository().sredniaKwotaKredytuKlienta(1)
        self.assertEqual(srednia, oczekiwana, "Srednia kredytow dla klientId=1 powinna wynosic " + str(oczekiwana) + " wynosi " + str(srednia) )

    def testSredniaWszystkichKredytow(self):
        oczekiwana = 304000;
        srednia = repository.KredytyRepository().sredniaKwotaWszystkichKredytow();
        self.assertEqual(srednia, oczekiwana, "Srednia wszystkich kredytow powinna wynosic " + str(oczekiwana) + ", wynosi " + str(srednia))


if __name__ == "__main__":
    unittest.main()