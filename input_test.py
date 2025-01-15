import keyboard
import sys
import random

answer = 0
trial = 0
rep = 0

# Participant ID eingeben
participant_id =  int(sys.argv[1])

combinations = [
    ["Keyboard", "Gitarre", "Drums"],
    ["Keyboard", "Drums", "Gitarre"],
    ["Gitarre", "Keyboard", "Drums"],
    ["Gitarre", "Drums", "Keyboard"],
    ["Drums", "Keyboard", "Gitarre"],
    ["Drums", "Gitarre", "Keyboard"],
]

# RANDOMTEST
# Erstelle eine Liste mit 120 mal "E" und 120 mal "F"
latency_keys = ["E"] * 40 + ["F"] * 40
# Mische die Liste zufällig
random.shuffle(latency_keys)
print(latency_keys)
# Zeige die ersten 10 Werte zur Kontrolle
#print(latency_keys[:10])
# Gesamte Liste durchlaufen
#for i, key in enumerate(latency_keys):
    #print(f"Trial {i+1}: Latenz liegt auf Taste {key}")



instrument_order = combinations[participant_id % 6]

# Eingaben bestätigen
print(f"Participant ID: {participant_id}")
def on_e_pressed():
    global rep
    global trial
    global latency_keys

    print("E")
    print(latency_keys[10*trial + rep])
    print("Das Ergabnis ist:")
    if(latency_keys[10*trial + rep] == "E"):
        print("Das war richtig!")
    else:
        print("Das war falsch :(")
    rep += 1
    if(rep >= 10):
        trial += 1
        rep = 0
    print("------------------------------")

def on_f_pressed():
    global rep
    global trial
    global latency_keys
    
    print("F")
    print(latency_keys[10*trial + rep])
    print("Das Ergabnis ist:")
    if(latency_keys[10*trial + rep] == "F"):
        print("Das war richtig!")
    else:
        print("Das war falsch :(")
    rep += 1
    if(rep >= 10):
        trial += 1
        rep = 0
    print("------------------------------")

keyboard.on_press_key("e", lambda _: on_e_pressed())
keyboard.on_press_key("f", lambda _: on_f_pressed())
while True:
    continue