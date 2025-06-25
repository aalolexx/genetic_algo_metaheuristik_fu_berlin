from abc import ABC, abstractmethod
import time
from copy import deepcopy
import json

class Metaheuristik(ABC):
    def __init__(self, instanz_daten, konfiguration, durchlauf_verzeichnis):
        self.loesung = None
        self.zwischenergebnisse = []
        self.durchlauf_verzeichnis = durchlauf_verzeichnis

        self.eingabe_daten = instanz_daten
        self.konfiguration = konfiguration

        self.beste_loesung = None

    @abstractmethod
    def initialisiere(self):
        """Initialisiert interne Strukturen der Metaheuristik"""
        raise NotImplementedError("Die Methode 'initialisiere()' muss in der Subklasse implementiert werden.")

    @abstractmethod
    def iteriere(self):
        """Führt eine Iteration des Metaheuristikverfahrens durch"""
        raise NotImplementedError("Die Methode 'iteriere()' muss in der Subklasse implementiert werden.")

    @abstractmethod
    def bewerte_loesung(self):
        """Bewertet die aktuelle Lösung anhand der Zielfunktion"""
        raise NotImplementedError("Die Methode 'bewerte_loesung()' muss in der Subklasse implementiert werden.")

    @abstractmethod
    def speichere_zwischenergebnis(self):
        """Speichert aktuelle Lösung und relevante Metriken"""
        raise NotImplementedError("Die Methode 'speichere_zwischenergebnis()' muss in der Subklasse implementiert werden.")

    def gebe_endloesung_aus(self):
        """Gibt die beste gefundene Lösung am Ende des Verfahrens aus"""
        return self.beste_loesung, self.bester_wert
