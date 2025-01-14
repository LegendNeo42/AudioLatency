#TO DO:
# Gewichtete Randomness bei e unf f Taste Latenz 50/50
# runtime_total muss noch geloggt werden
# count muss noch geloggt werden
# runtime_average muss noch geloggt werden (und ein Array werden, 1 Wert pro Instrument)
# runtime_total muss noch geloggt werden (und ein Array werden, 1 Wert pro Instrument)
# latency_results muss noch geloggt werden
# Logging anpassen

import time # time delay
import sys # for command line parameters
import random
import pandas as pd
import keyboard

# diese Variable wird auf True gesetzt, sobald alle Versuche durchgelaufen sind, damit das Programm beendet wird
stop_loop = False

# constant parameter for decision
KEY_E = 1
KEY_F = 0

# counter for each press on key e and f
counter_e = 0
counter_f = 0

latency_e = 0
latency_f = 0
correct_side = ""
last_correct_answer = 0.256

# sum of both counters
count = 0
# answer = 1

# random generator for key assignment
random_key = random.randint(0, 1)

# parameters for latency
latency = 0.256
latency_step = [0.128, 0.064, 0.032, 0.016, 0.008, 0.004, 0.002, 0.001] # starts with 128 -> 64 -> 32 -> 16 -> 8 -> 4 -> 2 -> 1


# Ein trial beschreibt eine 10er-Runde an reps. Nach jedem Trial wird die Latenz verändert. Insgesamt gibt es pro instrument 8 trials.
trial = 0

# rep beschreibt einen Unterscheidungs-Versuch. 10 reps ergeben einen trial.
rep = 0

# runtime beschreibt die Zeit für einen rep.
runtime = 0
# In diesem Array werden die runtimes gespeichert
runtime_results = []
# Am Ende wird die durchschnittliche runtime errechnet
runtime_average = 0
# Hier werden die Gesamtzeiten pro Instrument gespeichert
runtime_total = []
#final_result = 0

# Anzahl der richtigen Eingaben je 10ner-Runde. Sollten nach 10 Eingaben mind. 8 richtig sein (also percent größer gleich 8), dann yippie.
percent = 0

e_timer = time.time()
f_timer = time.time()


# parameters for saving data
log_data_pair = []

# Warum ist das ein Array?
latency_results = []


# verschiedene Kombinationsmöglichkeiten (latin square)
combinations = [
    ["Keyboard", "Gitarre", "Drums"],
    ["Keyboard", "Drums", "Gitarre"],
    ["Gitarre", "Keyboard", "Drums"],
    ["Gitarre", "Drums", "Keyboard"],
    ["Drums", "Keyboard", "Gitarre"],
    ["Drums", "Gitarre", "Keyboard"],
]

# tracks the participant_id in the beginning, mit dem ersten Parameter nach invoken dieses Skripts
participant_id = int(sys.argv[1])


# instrument order abhängig von Participant ID
instrument_order = combinations[participant_id % 6]
# Beschreibt den ganzen Versuch für ein Instrument, bestehend aus 8 trials. Nach diesen wird das Instrument "erhöht"
current_instrument_number = 0
# Das aktuelle Instrument als String fürs Logging
current_instrument = instrument_order[current_instrument_number]

def on_e_pressed():
    print("Key pressed:     E")
    handle_foot_input(KEY_E)

def on_f_pressed():
    print("Key pressed:     F")
    handle_foot_input(KEY_F)

# Bekomme hier den gepressten Fußpedal-Key übergeben
def handle_foot_input(key):
    global counter_e
    global counter_f
    global count
    global trial
    global runtime
    global runtime_results
    global rep
    global last_correct_answer

    #Prüfe, ob die Eingabe richtig war (KEY_E oder KEY_F)
    answer = checkInput(key)
    #Errechne die Zeit seit dem letzten Versuch
    setRuntime()
    #Füge die Zeit ins Zeiten-Array hinzu
    runtime_results.append(runtime)
    # Setze die globalen Variablen für die Latenz von E und F, und der correctSide.
    getLatencies()

    if (key == KEY_E):
        # Logge den ganzen Stuff MIT DER TASTE E
        log_data_pair.append({"instrument" : current_instrument, "repetition" : rep, "trial" : trial, "counter_e" : counter_e, "counter_f" : counter_f, "latency_e" : latency_e, "latency_f" : latency_f, "key" : "e", "correct_side" : correct_side, "answer" : answer, "time" : runtime, "last_correct_answer" : last_correct_answer})
    else:
        # Logge den ganzen Stuff MIT DER TASTE F
        log_data_pair.append({"instrument" : current_instrument, "repetition" : rep, "trial" : trial, "counter_e" : counter_e, "counter_f" : counter_f, "latency_e" : latency_e, "latency_f" : latency_f, "key" : "f", "correct_side" : correct_side, "answer" : answer, "time" : runtime, "last_correct_answer" : last_correct_answer})
    # Setze die Werte für E und F zurück
    resetCounter()
    # Setze die Latenzen neu, und lasse die Konsole das Ergebnis ausgeben. 
    # Sollte eine Runde oder der ganze Versuch beendet sein, agiere dementsprechend.
    setLatency(answer)

# sets new value for latency depending on answer and latency_step
# sets a new random key for the latency and calculates the latency_step
# answer = 1: input is true
# answer = 0: input is false
def setLatency(answer):
    global stop_loop
    global trial
    global latency_step
    global latency
    global latency_results
    global rep
    global runtime_total
    global percent
    global runtime_results
    global current_instrument
    global current_instrument_number
    global last_correct_answer
    
    print("Das ist "f'trial:   {trial}')
    print("Das ist "f"rep:     {rep}")

    rep += 1
    # randomized zwischen E und F
    setRandomKey()
    
    # Solange noch nicht der 10. Versuch war...
    if(rep < 10):
        if answer == 1:
            percent +=1
            print("richtig")

        elif answer == 0:
            print("falsch")
    # ... und noch nicht die neunte Runde (PEST!), dann zeige einfach nur wahr oder falsch an und update ggf. den percent-(Anzahl richtiger Eingaben)-Tracker.
    elif (trial < 8):
        if answer == 1:
            percent +=1
            print("richtig")

        elif answer == 0:
            print("falsch")
    
        
        # Warum wird percent nicht im else zurückgesetzt?
        if(percent >= 8):
            latency = latency - latency_step[trial]
            last_correct_answer = latency
        else:
            latency = latency + latency_step[trial]
        # Hier ausgeschachtelt, war vorher nur im if
        percent = 0
        # Sollte eine 10ner-Runde beendet sein, update die nötigen Counter und wende die 8/10-PEST plus oder minus an.
        trial +=1
        rep = 0
    
    # Im Falle der letzten Runde der letzten Runde
    else:
        # Logge alles notwendige
        # Warum ist das ein Array?
        latency_results.append(latency)
        calcRuntimeTotal()
        # runtime_total woanders loggen
        # Ist es nötig, die Werte zu resetten wenn das Programm eh beendet wird?
        runtime_total = 0
        runtime_results = []
        
        if(current_instrument_number < 2):
            print("CURRENT_INSTRUMENT_NUMBER: " + str(current_instrument_number))
            current_instrument_number += 1
            current_instrument = instrument_order[current_instrument_number]
            reset_values()
        else:
            saveLog()
            stop_loop = True


def reset_values():
    global latency
    global count
    global trial
    global rep
    global percent

    latency = 0.256
    count = 0
    trial = 0
    rep = 0
    percent = 0




# Die durchschnittliche Dauer pro individuellem Versuch
def calcRuntimeAverage():
    global runtime_results
    global runtime_average
    runtime_average = sum(runtime_results) / len(runtime_results)

# Die gesamte Zeit für den Versuch
def calcRuntimeTotal():
    global runtime_results
    global runtime_total
    runtime_total = sum(runtime_results)
    
# Setzt die runtime auf die aktuelle Zeit minus sich selbst auf 2 Dezimalen. Runtime wird nach dem erstmaligen Drücken von E oder F mit time.time initialisiert.
def setRuntime():
    global runtime
    runtime = round((time.time() - runtime), 2)


# gets e and f latency for dataframe, Setze die Latenzen für die Tasten E und F
def getLatencies():
    global random_key
    global latency_e
    global latency_f
    global correct_side
    
    if(random_key == 1):
        latency_e = latency
        latency_f = 0
        correct_side = "e";
    else:
        latency_e = 0
        latency_f = latency
        correct_side = "f";
    


# sets random to 0 or 1
def setRandomKey():
    global random_key
    random_key = random.randint(0, 1)


# saves csv files
def saveLog():
    log = pd.DataFrame(log_data_pair)
    log['participant_id'] = participant_id
    log.to_csv(f"{participant_id}.csv")

# checks if the users choice was true or false
# uses latency and base_latency to find the right answer
# sets answer to true(1) or false(0)
def checkInput(note):
    if(random_key == note):
        answer = 1
    else:
        answer = 0
    return answer

# resets counter for e and f
def resetCounter():
    global counter_e, counter_f
    counter_e = 0
    counter_f = 0


keyboard.on_press_key("e", lambda _: on_e_pressed())
keyboard.on_press_key("f", lambda _: on_f_pressed())

while True:
    if stop_loop:
        sys.stdout.flush()
        break
