from database.distributore_DAO import DistributoreDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """
        risultato = []
        if self._distributori is None:
            return risultato

        for distributore in self._distributori:
            prezzi = distributore.get_prezzi()
            if not prezzi:
                continue
            prezzi_mese = []
            for p in prezzi:
                if p.data.month == mese:
                    prezzi_mese.append(p.prezzo_litro)
            if len(prezzi_mese) > 0:
                # 3. Calcolo la media con passaggi ben separati
                somma_prezzi = sum(prezzi_mese)
                numero_prezzi = len(prezzi_mese)
                media = somma_prezzi / numero_prezzi
                risultato.append((distributore.nome, media))

        return risultato

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """
        if giorno>7:
            if self.__costo_ottimo>costo_corrente or self.__costo_ottimo == -1:
                self.__costo_ottimo=costo_corrente
                self.__sequenza_ottima = list(sequenza_parziale)
            return
        for id_distributore in prezzi_settimana:
            costo_giorno = prezzi_settimana[id_distributore][giorno - 1] * 100
            if ultimo_distributore is not None and ultimo_distributore != id_distributore:
                costo_giorno += 5
            nuovo_costo = costo_corrente + costo_giorno

            if self.__costo_ottimo == -1 or nuovo_costo < self.__costo_ottimo:
                sequenza_parziale.append(id_distributore)
                self.__ricorsione(sequenza_parziale, giorno + 1, id_distributore, nuovo_costo, prezzi_settimana)
                sequenza_parziale.pop()

    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        prezzi_settimana = {}
        for distributore in self._distributori:
            prezzi = distributore.get_prezzi()
            if prezzi is None:
                prezzi = []
            prezzi_filtrati = []
            for p in prezzi:
                if p.data.month == mese and p.data.day <= 7:
                    prezzi_filtrati.append(p)
            prezzi_ordinati = sorted(prezzi_filtrati, key=lambda p: p.data)
            prezzi_finali = []
            for p in prezzi_ordinati:
                prezzi_finali.append(p.prezzo_litro)
            prezzi_settimana[distributore.id] = prezzi_finali

        return prezzi_settimana
