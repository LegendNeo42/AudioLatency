import mido # midi stuff, kommuniziert mit dem Keyboard
import time # time delay
import RPi.GPIO as GPIO # access raspi pins
import sys # for command line parameters
import threading
import random
import pandas as pd

# select broadcom pin numbers: https://pinout.xyz/#
GPIO.setmode(GPIO.BCM)

# set pins to output mode, Pin 18 ist für den Oscillator
GPIO.setup(18, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)

# set pins to input mode, Pin 2 und 3 sind jeweils für die Tasten E und F, aber auch nur für den elektrischen Current mit dem Kupfer
GPIO.setup(2, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(3, GPIO.IN, pull_up_down = GPIO.PUD_UP)

# list of all available MIDI input devices, sollte nur das Keyboard sein
inputs = mido.get_input_names()

# let user select a device
counter = 0


# Verstehe noch nicht was das macht
for device in inputs:
    print(f'[{counter}] {device}')
    counter += 1
#selection = input('select device: '), war früher geplant mehrere Instrumente anzubieten, und das ist ein Überbleibsel?
selection = 1

#Öffnet für mido den input, quasi einen Listener für das Keyboard, selectiion ist immer 1, weil immer Keyboard
p = mido.open_input(inputs[int(selection)]) 



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
# base_elements = [0, 0.064, 0.512], denn das brauchen wir nicht mehr
# base_latency = 0, denn das brauchen wir nichht mehr
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
log_data_base = []

base_average = 0
latency_results = []
average_results = []

# tracks the participant_id in the beginning
participant_id = sys.argv[1]
    

# gets keyboard's midi input from user
# handles input
def midi_input():
    global counter_e
    global counter_f
    global count
    global trial
    global runtime
    global runtime_results
    global rep
    
    for msg in p:
        count = counter_e + counter_f
        
        if(msg.type == 'note_on'):
            
            # Taste Nummer 52 scheint die E-Taste zu sein, also ist dies hier zum Bestätigen der E-Taste. Diese if brauchen wir nicht, da wir die Peddals nehmen?
            # Können den Code wohl reusen?
            if(msg.note < 52):
                # Prüft, ob die Eingabe richtig war
                answer = checkInput(KEY_E)
                # Errechne die Zeit seit dem letzten Versuch. Also messe die Zeit die diese Entscheidung brauchte.
                setRuntime()
                # Füge die Zeit ins Zeiten-Array hinzu
                runtime_results.append(runtime)
                # Setze die globalen Variablen für die Latenz von E und F, und der correctSide.
                getLatencies()
                # Logge den ganzen Stuff
                log_data_pair.append({"condition" : base_latency, "repetition" : rep, "trial" : trial, "counter_e" : counter_e, "counter_f" : counter_f, "latency_e" : latency_e, "latency_f" : latency_f, "base_latency" : base_latency, "key" : "e", "correct_side" : correct_side, "answer" : answer, "time" : runtime})
                # Setze die Counter für E und F zurück
                resetCounter()
                # Setze die Latenzen neu, und lasse die Konsole das Ergebnis ausgeben. Sollte eine Runde oder der ganze Versuch beendet sein, agiere dementsprechend.
                setLatency(answer)
                
            # Taste Nummer 53 scheint die F-Taste zu sein, also ist dies hier zum Bestätigen der F-Taste. Diese elif brauchen wir nicht, da wir die Peddals nehmen?
            # Können den Code wohl reusen?
            elif(msg.note > 53):
                
                answer = checkInput(KEY_F)
                setRuntime()
                runtime_results.append(runtime)
                getLatencies()
                log_data_pair.append({"condition" : base_latency, "repetition" : rep, "trial" : trial, "counter_e" : counter_e, "counter_f" : counter_f,"latency_e" : latency_e, "latency_f" : latency_f, "base_latency" : base_latency, "key" : "f", "correct_side" : correct_side, "answer" : answer, "time" : runtime})
                resetCounter()
                setLatency(answer)

            # 
            if(msg.note == 52):
                if(count == 0):
                    runtime = time.time()
                counter_e += 1
                
            elif(msg.note == 53):
                if(count == 0):
                    runtime = time.time()
                counter_f += 1
        else:
            pass

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
    global base_average
    global base_elements
    global runtime_total
    global percent
    
    print(f'trial;{trial}')
    print(f"rep;{rep}")
    print(f"base;{3 - len(base_elements)}")

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
    elif (trial < 9):
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
            percent = 0
        else:
            latency = latency + latency_step
    
    # Im Falle der letzten Runde der letzten Runde
    else:
        # Logge alles notwenidige
        latency_results.append(latency - base_latency)
        calcLatencyAverage()
        calcRuntimeTotal()
        log_data_base.append({"condition" : base_latency, "base_average" : base_average, "runtime_total" : runtime_total})
        runtime_total = 0
        runtime_results = []
        print (f"Pause;{base_average}")
        average_results.append(base_average)
        saveLog()
        setBase()
    sys.stdout.flush()
    
# Die durchschnittliche Dauer pro individuellem Versuch
def calcRuntimeAverage():
    global runtime_results
    global runtime_average
    runtime_average = sum(runtime_results) / len(runtime_results)
    runtime_results = []

# Die gesamte Zeit für den Versuch
def calcRuntimeTotal():
    global runtime_results
    global runtime_total
    runtime_total = sum(runtime_results)
    
# Bin ich blöd oder ist base_average immer 0?
def calcLatencyAverage():
    global latency_results
    global base_average
    base_average = round(sum(latency_results) / len(latency_results), 3)
   
def calcFinalResult():
    global average_results
    global final_result
    
    final_result = sum(average_results) / len(average_results)
    
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
        latency_f = base_latency
        correct_side = "e";
    else:
        latency_e = base_latency
        latency_f = latency
        correct_side = "f";
    
    
# sets base_latency to one of the base elements from list
# deletes selected base from list
# sets latency dependent on base_latency
# for no base_latency left the experiment is over
def setBase():
    global base_latency
    global latency
    global base_elements
    global rep
    global base_average
    global latency_results
    global final_result
    
    rep = 1
    base_average = 0
    latency_results = []
    
    if (len(base_elements) > 0):
        resetValues()
        base_latency = random.choice(base_elements)
        base_elements.remove(base_latency)
        latency += base_latency
        print (base_latency, latency)
        
    else: 
        print("danke")
        calcFinalResult()
        saveLog()
        print(f"result;{final_result}")
        

# sets random to 0 or 1
def setRandomKey():
    global random_key
    random_key = random.randint(0, 1)

# calculates and sets latency_step depending on trial
def setLatencyStep(trial):
    global latency_step
    latency_step = 0.512 / (2**trial)

# saves csv files
def saveLog():
    log_rep = pd.DataFrame(log_data_base)
    log_rep['participant_id'] = participant_id
    log_rep.to_csv(f"{participant_id}_base.csv")
    
    log = pd.DataFrame(log_data_pair)
    log['participant_id'] = participant_id
    log.to_csv(f"{participant_id}.csv")

# resets latency, trial and latency_step
def resetValues():
    global latency
    global latency_step
    global trial
    
    latency = 0.256
    latency_step = 0
    trial = 1

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
    

# callback key e
def callback_pin_2 (*args):
    global pin_2_value
    global last_time
    global latency
    global base_latency
    global e_timer
    
    state = not GPIO.input(2)
    pin_2_value = state
    
    if (state == True and (time.time() - e_timer < 0.02)):
        return
    e_timer = time.time()
    
    if(random_key == 1):
        threading.Thread(target = play_tone, args = (state, latency,), daemon = True).start()
    else:
        threading.Thread(target = play_tone, args = (state, base_latency,), daemon = True).start()
        
# callback key f
def callback_pin_3 (*args):
    global pin_3_value
    global last_time
    global latency
    global base_latency
    global f_timer
    
    state = not GPIO.input(3)
    pin_3_value = state
    
    if (state == True and (time.time() - f_timer < 0.02)):
        return
    f_timer = time.time()
    
    if(random_key == 0):
        threading.Thread(target = play_tone, args = (state, latency,), daemon = True).start()
    else:
        threading.Thread(target = play_tone, args = (state, base_latency,), daemon = True).start()

# function for playing tone with diffferent latency
def play_tone (state, latency):
    time.sleep(latency)
    GPIO.output(18, state)

# START
setBase()

# detect input from GPIO and keyboard note e1 and f1
GPIO.add_event_detect(2, edge = GPIO.BOTH, callback=callback_pin_2)
GPIO.add_event_detect(3, edge = GPIO.BOTH, callback=callback_pin_3)
lastButtonState = 0

input_thread = threading.Thread(target = midi_input, daemon = True)
input_thread.start()


while True:
    continue
    #pin_2_value = GPIO.input(2)
    
    if pin_2_value == 0:
        #print("pin2value:", pin_2_value)
        if lastButtonState == 0:
            lastButtonState = 1
    else:
        lastButtonState = 0

sys.exit()


try:
    # listen to input from selected device and print MIDI messages
        for msg in p:
            if(msg.type == 'note_on'):
                if(msg.note == 59):
                    time.sleep(latency1)
                elif(msg.note == 60):
                    time.sleep(latency2)
                GPIO.output(23, GPIO.HIGH)
            else:
                GPIO.output(23, GPIO.LOW)
            print(msg)

except (ValueError, IndexError) as e:
    print(f'invalid device number: {selection} - must be between 0 and {len(inputs)-1}')
except KeyboardInterrupt:
    pass
