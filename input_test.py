import keyboard
import sys

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