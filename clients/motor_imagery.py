import json
import time
from psychopy import visual, core, event, gui
import random
import threading
from client_sub import ClientSub
from utils import get_unique_filename
import numpy as np
import csv
import queue

# Setup experiment window
win = visual.Window(fullscr=False, color="black", units="norm")

# Create stimuli
instructions = visual.TextStim(win, text="Imagine performing the action shown.\n\nPress space to start and q to stop.", color="white")
fixation = visual.TextStim(win, text="+", color="white")

cue_left = visual.TextStim(win, text="Left Hand", color="white", pos=(-0.5, 0))
left_hand_image = visual.ImageStim(win, image="photos/left_hand.jpg", pos=(-0.5, 0.25), size=(0.7, 0.7), ori=90)

cue_right = visual.TextStim(win, text="Right Hand", color="white", pos=(0.5, 0))
right_hand_image = visual.ImageStim(win, image="photos/right_hand.jpg", pos=(0.5, 0.25), size=(0.7, 0.7), ori=90)

# Experiment parameters
n_trials = 30
trial_duration = 3  # seconds
rest_duration = 2  # seconds

DATA_LOG_FILE = 'logs/motor_imagery/data.csv'
csv_file = get_unique_filename(DATA_LOG_FILE)

subscriber = ClientSub()
subscriber.get_channel_names()
ch_names = subscriber.ch_names

data_lock = threading.Lock()
# data = {"samplestamps": [], "samples" : [], "stimuli": [], "ch_names": subscriber.ch_names}
data = {}

q = queue.Queue()

stimuli = None

def get_data():
    global data, stimuli

    while True:
        try:
            samplestamps, samples, _ = subscriber.get_data()
            with data_lock:
                data["samplestamps"] = samplestamps.tolist()
                data["stim"] = [stimuli] * len(samplestamps)
                for ch in subscriber.ch_names:
                    data[ch] = samples[:, subscriber.ch_names.index(ch)].tolist()
                q.put(data)
        except Exception as e:
            raise e
        
        time.sleep(0.1)  # Adjust this sleep interval as needed

def save_data_log():
    csv_file = get_unique_filename(DATA_LOG_FILE)

    with open(csv_file, "w", newline='') as file:
        fieldnames = ["samplestamps", "stim"]
        fieldnames.extend(ch_names)

        # Create a CSV DictWriter object
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        while True:
            data = q.get()
            if data is None:
                break
            
            num_rows = len(next(iter(data.values())))
            for i in range(num_rows):
                row = {key: value[i] for key, value in data.items()}
                writer.writerow(row)

            q.task_done()

# Start the data acquisition thread
data_thread = threading.Thread(target=get_data)
data_thread.daemon = True
data_thread.start()

writer_thread = threading.Thread(target=save_data_log)
writer_thread.daemon = True
writer_thread.start()


# Show instructions
instructions.draw()
win.flip()
event.waitKeys(keyList=['space'])

# Create a list of cue pairs (image, text)
cues = [
    (left_hand_image, cue_left),
    (right_hand_image, cue_right)
]

# Main experiment loop
for trial in range(n_trials):
    # Show fixation
    fixation.draw()
    win.flip()
    stimuli = "fixation"
    core.wait(rest_duration)
    
    # Show cue
    cue_image, cue_text = random.choice(cues)
    cue_image.draw()
    cue_text.draw()
    win.flip()
    stimuli = cue_text.text
    trial_clock = core.Clock()

    # Wait for trial duration or key press
    keys = event.waitKeys(maxWait=trial_duration, keyList=['q', 'space'])

    # Check for quit signal
    if keys and 'q' in keys:
        break

    # Record response time if space was pressed
    if keys and 'space' in keys:
        rt = trial_clock.getTime()    
        print(f"Trial {trial+1}: Time elapsed {rt:.2f}s")
    else:
        print(f"Trial {trial+1}: Trial Finished")

# Clean up
q.put(None)
q.join()

win.close()
core.quit()
