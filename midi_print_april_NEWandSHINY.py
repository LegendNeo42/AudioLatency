#TO DO:
# Bei Tastendruck soll geloggt werden
# Entscheiden, ob man das Skript 3mal startet für die drei Instrumente, oder das intern macht
# den Code aus dem Pi übernehmen, mit Variationen für das Instrument 1,2 und 3
# Das Loggen um instrument etc erweitern
# Beim Loggen alles mit Base Latency rausnehmen
# current_instrument mitloggen


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
GPIO.setup(23, GPIO.OUT)

# set pins to input mode, Pin 2 und 3 sind jeweils für die Tasten E und F, aber auch nur für den elektrischen Current mit dem Kupfer
GPIO.setup(2, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(3, GPIO.IN, pull_up_down = GPIO.PUD_UP)

# initialize parameters
pin_2_value = 1
pin_3_value = 1

# constant parameter for decision
KEY_E = 1
KEY_F = 0

# counter for each press on key e and f
counter_e = 0
counter_f = 0

latency_e = 0
latency_f = 0
correct_side = ""

# sum of both counters
count = 0
answer = 1

# random generator for key assignment
random_key = random.randint(0, 1)

# parameters for latency
latency = 0.256
latency_step = 0 # starts with 128 -> 64 -> 32 -> 16 -> 8 -> 4 -> 2 -> 1

# describes the number of trys in one base round
# needed for latency_step
trial = 1

# rep describes the number of repetitions of one base
rep = 1

# time of each decision
runtime = 0
runtime_results = []
runtime_average = 0
runtime_total = 0
final_result = 0

# Anzahl der richtigen Eingaben je 10ner-Runde. Sollten nach 10 Eingaben mind. 8 richtig sein (also percent größer gleich 8), dann yippie.
percent = 0

e_timer = time.time()
f_timer = time.time()


# parameters for saving data
log_data_pair = []

# Warum ist das ein Array?
latency_results = []

# tracks the participant_id in the beginning, mit dem ersten Parameter nach invoken dieses Skripts
participant_id = sys.argv[1]

#Das aktuell genutzte Instrument. 1 ist Keyboard, 2 ist Drums, 3 ist Gitarre
current_instrument = sys.argv[2]


def on_e_pressed():
    handle_foot_input(KEY_E)

def on_f_pressed():
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
        log_data_pair.append({"instrument" : current_instrument, "repetition" : rep, "trial" : trial, "counter_e" : counter_e, "counter_f" : counter_f, "latency_e" : latency_e, "latency_f" : latency_f, "key" : "e", "correct_side" : correct_side, "answer" : answer, "time" : runtime})
    else:
        # Logge den ganzen Stuff MIT DER TASTE F
        log_data_pair.append({"instrument" : current_instrument, "repetition" : rep, "trial" : trial, "counter_e" : counter_e, "counter_f" : counter_f, "latency_e" : latency_e, "latency_f" : latency_f, "key" : "f", "correct_side" : correct_side, "answer" : answer, "time" : runtime})
    # Setze die Werte für E und F zurück
    resetCounter()
    # Setze die Latenzen neu, und lasse die Konsole das Ergebnis ausgeben. 
    # Sollte eine Runde oder der ganze Versuch beendet sein, agiere dementsprechend.
    setLatency(answer)

# KEINE ECHTE METHODE! Soll nur planen/darstellen, was alles bei nem Instrumenten-Press passieren soll.
def handle_Tastatur_input():
    global runtime
    if (KEY_E):
        if (count == 0):
            runtime = time.time()
        counter_e += 1
    if (KEY_F):
        if (count == 0):
            runtime = time.time()
        counter_f += 1


# sets new value for latency depending on answer and latency_step
# sets a new random key for the latency and calculates the latency_step
# answer = 1: input is true
# answer = 0: input is false
def setLatency(answer):
    global trial
    global latency_step
    global latency
    global latency_results
    global rep
    global runtime_total
    global percent
    global runtime_results
    
    print(f'trial;{trial}')
    print(f"rep;{rep}")

    rep += 1
    # randomized zwischen E und F
    setRandomKey()
    
    # Solange noch nicht der 10. Versuch war...
    if(rep <= 10):
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
        
        # Sollte eine 10ner-Runde beendet sein, update die nötigen Counter und wende die 8/10-PEST plus oder minus an.
        trial +=1
        rep = 1
        setLatencyStep(trial)
        
        # Warum wird percent nicht im else zurückgesetzt?
        if(percent >= 8):
            latency = latency - latency_step
        else:
            latency = latency + latency_step
        # Hier ausgeschachtelt, war vorher nur im if
        percent = 0
    
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
        saveLog()
    # Anstatt flush vielleicht beenden?    
    sys.stdout.flush()

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

# calculates and sets latency_step depending on trial
def setLatencyStep(trial):
    global latency_step
    latency_step = 0.256 / (2**trial)

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


# DAS HIER SIND DIE CALLBACK METHODEN! HIER MUSS NOCH SHIT REIN! UND RAUS!
# callback key e
def callback_pin_2 (*args):
    global pin_2_value
    global latency
    global e_timer
    
    state = not GPIO.input(2)
    pin_2_value = state
    
    if (state == True and (time.time() - e_timer < 0.02)):
        return
    e_timer = time.time()
    
    if(random_key == 1):
        threading.Thread(target = play_tone, args = (state, latency,), daemon = True).start()
    else:
        threading.Thread(target = play_tone, args = (state, 0), daemon = True).start()
# callback key f
def callback_pin_3 (*args):
    global pin_3_value
    global latency
    global f_timer
    
    state = not GPIO.input(3)
    pin_3_value = state
    
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
    continue
