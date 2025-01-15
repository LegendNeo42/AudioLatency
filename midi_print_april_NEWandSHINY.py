#TO DO:
# Logging anpassen im Bezug auf runtime (rohe Time loggen)
# Cooldown auf die Fußpedale
# Callback-Methoden: bei Gitarre Code NOT ändern mit If abfrage
# GUI Bauen

import time # time delay
import RPi.GPIO as GPIO
import sys # for command line parameters
import threading
import random
import pandas as pd
import keyboard

# select broadcom pin numbers: https://pinout.xyz/#
GPIO.setmode(GPIO.BCM)

# set pins to output mode, Pin 18 ist für den Oscillator
GPIO.setup(18, GPIO.OUT)
#GPIO.setup(23, GPIO.OUT)

# set pins to input mode, Pin 2 und 3 sind jeweils für die Tasten E und F, aber auch nur für den elektrischen Current mit dem Kupfer
GPIO.setup(2, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(3, GPIO.IN, pull_up_down = GPIO.PUD_UP)

# diese Variable wird auf True gesetzt, sobald alle Versuche durchgelaufen sind, damit das Programm beendet wird
stop_loop = False

# initialize parameters
#pin_2_value = 1
#pin_3_value = 1

# constant parameter for decision
KEY_E = 1
KEY_F = 0

# counter for each press on key e and f
counter_e = 0
counter_f = 0

latency_e = 0
latency_f = 0
# latency_side ist der Key der Latenz drauf hat
latency_side = ""
# pb = personal_best
current_pb_latency = 0

# answer = 1

# random generator for key assignment
latency_keys = ["E"] * 40 + ["F"] * 40
random.shuffle(latency_keys)

# parameters for latency
latency = 0.128
latency_step = [0.064, 0.032, 0.016, 0.008, 0.004, 0.002, 0.001]

# Ein trial beschreibt eine 10er-Runde an reps. Nach jedem Trial wird die Latenz verändert. Insgesamt gibt es pro instrument 8 trials.
trial = 0
#trials per instrument
trials_per_instrument = 8

# number of instruments
number_of_instruments = 3
# rep beschreibt einen Unterscheidungs-Versuch. 10 reps ergeben einen trial.
rep = 0
#reps per trial
reps_per_trial = 10

# diese Anzahl an Antworten müssen mindestens korrekt sein
min_correct_answers = 8 #All Caps

# runtime beschreibt die Zeit für einen rep.
#runtime = 0
# In diesem Array werden die runtimes gespeichert
#runtime_results = []
# Am Ende wird die durchschnittliche runtime errechnet
#runtime_average = 0
# Hier werden die Gesamtzeiten pro Instrument gespeichert
#runtime_total = []
#final_result = 0

# Anzahl der richtigen Eingaben je 10ner-Runde. Sollten nach 10 Eingaben mind. 8 richtig sein (also percent größer gleich 8), dann yippie.
correct_answers = 0


last_key_press = 0
COOLDOWN = 0.1


# parameters for saving data
log_data_pair = []

# Warum ist das ein Array?
#latency_results = []


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
    global trial
    global runtime
    global runtime_results
    global rep
    global current_pb_latency
    global log_data_pair

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
        log_data_pair.append({"instrument" : current_instrument, "repetition" : rep, "trial" : trial, "counter_e" : counter_e, "counter_f" : counter_f, "latency_e" : latency_e, "latency_f" : latency_f, "key" : "e", "correct_side" : latency_side, "answer" : answer, "time" : runtime, "current_personal_best_latency" : current_pb_latency})
    else:
        # Logge den ganzen Stuff MIT DER TASTE F
        log_data_pair.append({"instrument" : current_instrument, "repetition" : rep, "trial" : trial, "counter_e" : counter_e, "counter_f" : counter_f, "latency_e" : latency_e, "latency_f" : latency_f, "key" : "f", "correct_side" : latency_side, "answer" : answer, "time" : runtime, "current_personal_best_latency" : current_pb_latency})
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
    global current_pb_latency
    global min_correct_answers
    
    print("Das ist "f'trial:   {trial}')
    print("Das ist "f"rep:     {rep}")

    rep += 1
    # randomized zwischen E und F
    setRandomKey()
    
    # Solange noch nicht der 10. Versuch war...
    if(rep < reps_per_trial):
        if answer == 1:
            percent +=1
            print("richtig")

        elif answer == 0:
            print("falsch")
    # ... und noch nicht die neunte Runde (PEST!), dann zeige einfach nur wahr oder falsch an und update ggf. den percent-(Anzahl richtiger Eingaben)-Tracker.
    elif (trial < trials_per_instrument):
        if answer == 1:
            percent += 1
            print("richtig")

        elif answer == 0:
            print("falsch")
        
        if(percent >= min_correct_answers):
            current_pb_latency = latency
            print(latency)
            print("minus")
            print(latency_step[trial])
            print("gleich")
            latency = latency - latency_step[trial]
            print(latency)
            latency = round(latency, 3)
            print(latency)
        else:
            print(latency)
            print("plus")
            print(latency_step[trial])
            print("gleich")
            latency = latency + latency_step[trial]
            print(latency)
            latency = round(latency, 3)
            print(latency)

        percent = 0
        # Sollte eine 10ner-Runde beendet sein, update die nötigen Counter und wende die 8/10-PEST plus oder minus an.
        trial += 1
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
        if(current_instrument_number < (number_of_instruments - 1)):
            current_instrument_number += 1
            print("CURRENT_INSTRUMENT_NUMBER: " + str(current_instrument_number))
            current_instrument = instrument_order[current_instrument_number]
            reset_values()
        else:
            saveLog()
            stop_loop = True
            

def reset_values():
    global latency
    global trial
    global rep
    global percent
    global current_pb_latency
    global latency_keys

    latency = 0.256
    trial = 0
    rep = 0
    percent = 0
    current_pb_latency = 0
    random.shuffle(latency_keys)




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
    global latency_keys
    global latency_e
    global latency_f
    global latency_side
    global trial
    global rep
    
    if(latency_keys[reps_per_trial*trial + rep] == "E"):
        latency_e = latency
        latency_f = 0
        latency_side = "e";
    else:
        latency_e = 0
        latency_f = latency
        latency_side = "f";
    


# sets random to 0 or 1
def setRandomKey():
    global random_key
    random_key = random.randint(0, 1)

# saves csv files
def saveLog():
    global log_data_pair

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


# DAS HIER SIND DIE CALLBACK METHODEN! HIER MUSS NOCH SHIT REIN! UND RAUS!
# callback key e
def callback_pin_2 (*args):
    #global pin_2_value
    global latency
    global e_timer
    
    state = not GPIO.input(2)
    #pin_2_value = state
    
    if (state == True and (time.time() - e_timer < 0.02)):
        return
    e_timer = time.time()
    
    if(random_key == 1):
        threading.Thread(target = play_tone, args = (state, latency,), daemon = True).start()
    else:
        threading.Thread(target = play_tone, args = (state, 0), daemon = True).start()
# callback key f
def callback_pin_3 (*args):
    #global pin_3_value
    global latency
    global f_timer
    
    state = not GPIO.input(3)
    #pin_3_value = state
    
    if (state == True and (time.time() - f_timer < 0.02)):
        return
    f_timer = time.time()
    
    if(random_key == 0):
        threading.Thread(target = play_tone, args = (state, latency,), daemon = True).start()
    else:
        threading.Thread(target = play_tone, args = (state, 0), daemon = True).start()


#KANN MAN WAHRSCHEINLICH UMSCHREIBEN, so dass nur bei der "correct_side" ein sleep passiert
# function for playing tone with different latency
def play_tone (state, latency):
    time.sleep(latency)
    GPIO.output(18, state)


# detect input from GPIO and keyboard note e1 and f1
GPIO.add_event_detect(2, edge = GPIO.BOTH, callback=callback_pin_2)
GPIO.add_event_detect(3, edge = GPIO.BOTH, callback=callback_pin_3)

keyboard.on_press_key("e", lambda _: on_e_pressed())
keyboard.on_press_key("f", lambda _: on_f_pressed())

while True:
    if stop_loop:
        sys.stdout.flush()
        break
