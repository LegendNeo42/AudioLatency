import keyboard
import sys
import random

answer = 0

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
latency_keys = ["E"] * 12 + ["F"] * 12
# Mische die Liste zufällig
random.shuffle(latency_keys)
# Zeige die ersten 10 Werte zur Kontrolle
print(latency_keys[:10])
# Gesamte Liste durchlaufen
for i, key in enumerate(latency_keys):
    print(f"Trial {i+1}: Latenz liegt auf Taste {key}")



instrument_order = combinations[participant_id % 6]

# Eingaben bestätigen
print(f"Participant ID: {participant_id}")
def on_e_pressed():
    global answer 
    answer = 4
    print(instrument_order)
    print(instrument_order[0])
    print(answer)

def on_f_pressed():
    print(answer)

keyboard.on_press_key("e", lambda _: on_e_pressed())
keyboard.on_press_key("f", lambda _: on_f_pressed())
while True:
    continue