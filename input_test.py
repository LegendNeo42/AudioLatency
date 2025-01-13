import keyboard

answer = 0

# Participant ID eingeben
participant_id = input("Gib die Participant ID ein: ")


# Eingaben bestätigen
print(f"Participant ID: {participant_id}")
def on_e_pressed():
    global answer 
    answer = 4
    print("InMtehodE")
    print(answer)

def on_f_pressed():
    print(answer)

keyboard.on_press_key("e", lambda _: on_e_pressed())
keyboard.on_press_key("f", lambda _: on_f_pressed())
while True:
    continue