# Participant ID eingeben
participant_id = input("Gib die Participant ID ein: ")

# Instrument auswählen
instrument = input("Welches Instrument wird verwendet? (gitarre, keyboard, drums): ")

# Eingaben bestätigen
print(f"Participant ID: {participant_id}")
print(f"Instrument: {instrument}")

# Python-Logik basierend auf den Eingaben
if instrument == "gitarre":
    print("Du spielst Gitarre.")
elif instrument == "keyboard":
    print("Du spielst Keyboard.")
elif instrument == "drums":
    print("Du spielst Drums.")
else:
    print("Unbekanntes Instrument.")