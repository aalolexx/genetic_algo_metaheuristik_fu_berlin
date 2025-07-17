from metaheuristiken.genetic_mh.GeneticMetaheuristik import GeneticMetaheuristik
import os
from hashlib import md5
import time
import json
import shutil

def lade_konfiguration_aus_json(config_json):
    """
    Lädt Konfigurationsparameter aus einer JSON-String
    """
    return json.loads(config_json)


def lade_daten_aus_json(dateipfad):
    """
    Lädt Instanzdaten aus einer JSON-Datei
    """
    try:
        with open(dateipfad, 'r', encoding='utf-8') as f:
            tmp_eingabe_daten = json.load(f)
    except Exception as e:
        raise RuntimeError(f"Fehler beim Laden der Instanzdatei: {e}")
    return tmp_eingabe_daten

######################################################################################################################



INSTANZEN_VERZEICHNIS = os.path.join("data", "input")
OUTPUT_VERZEICHNIS = os.path.join("test", "output")
CONFIG_VERZEICHNIS = "config"

if os.path.exists(OUTPUT_VERZEICHNIS):
    shutil.rmtree(OUTPUT_VERZEICHNIS)  # Delete the entire directory and its contents
os.makedirs(OUTPUT_VERZEICHNIS)

def test_1_definition():
    eingabe_daten = lade_daten_aus_json(os.path.join(INSTANZEN_VERZEICHNIS, "example_evacuation_data.json"))
    CONFIG_DATEI = os.path.join(CONFIG_VERZEICHNIS, 'geneticMetaheuristic_small_config.json')

    with open(CONFIG_DATEI, 'r', encoding='utf-8') as f:
        file_content = ''.join(f.readlines())
        konfigurations_daten = lade_konfiguration_aus_json(file_content)
        config_hash = md5(file_content.encode('utf-8')).hexdigest()

    DURCHLAUF_VERZEICHNIS = os.path.join(OUTPUT_VERZEICHNIS, f'geneticMetaheuristic_TEST_1_')

    mh = GeneticMetaheuristik(
        eingabe_daten,
        konfigurations_daten,
        DURCHLAUF_VERZEICHNIS
    )

    assert mh != None

def test_2_saved_file_name():
    eingabe_daten = lade_daten_aus_json(os.path.join(INSTANZEN_VERZEICHNIS, "example_evacuation_data.json"))
    CONFIG_DATEI = os.path.join(CONFIG_VERZEICHNIS, 'geneticMetaheuristic_small_config.json')

    with open(CONFIG_DATEI, 'r', encoding='utf-8') as f:
        file_content = ''.join(f.readlines())
        konfigurations_daten = lade_konfiguration_aus_json(file_content)
        config_hash = md5(file_content.encode('utf-8')).hexdigest()

    DURCHLAUF_VERZEICHNIS = os.path.join(OUTPUT_VERZEICHNIS, f'geneticMetaheuristic_TEST_2_')

    mh = GeneticMetaheuristik(
        eingabe_daten,
        konfigurations_daten,
        DURCHLAUF_VERZEICHNIS
    )

    mh.initialisiere()
    mh.iteriere()
    mh.speichere_zwischenergebnis()

    assert os.path.exists(os.path.join(DURCHLAUF_VERZEICHNIS, "evacuation_result_iteration_1.json")) and \
           os.path.exists(os.path.join(DURCHLAUF_VERZEICHNIS, "evacuation_result_iteration_2.json"))

def test_3_number_of_people():
    eingabe_daten = lade_daten_aus_json(os.path.join(INSTANZEN_VERZEICHNIS, "middle_evacuation_data.json"))
    CONFIG_DATEI = os.path.join(CONFIG_VERZEICHNIS, 'geneticMetaheuristic_small_config.json')

    with open(CONFIG_DATEI, 'r', encoding='utf-8') as f:
        file_content = ''.join(f.readlines())

    DURCHLAUF_VERZEICHNIS = os.path.join(OUTPUT_VERZEICHNIS, f'geneticMetaheuristic_TEST_3_')

    mh = GeneticMetaheuristik(
        eingabe_daten,
        {
            "max_laufzeit": 999999999999,
            "max_iterationen": 100,
            "patience": 5,
            "route_group_size": 100,
            "population_size": 10,
            "street_capacity": 0.2,
            "num_clusters": 10
        },
        DURCHLAUF_VERZEICHNIS
    )

    print("foo")

    total_population_input = sum(area['population'] for area in eingabe_daten.get('residential_areas', []))

    print("this could take a little...")
    mh.initialisiere()
    mh.iteriere()
    mh.speichere_zwischenergebnis()
    lsg, loss = mh.gebe_endloesung_aus()

    total_persons_output = sum(flow['persons'] for flow in lsg.get('flows', []))

    assert total_population_input == total_persons_output

