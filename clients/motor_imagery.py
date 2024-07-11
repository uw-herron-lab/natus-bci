import json
import time
from psychopy import visual, core, event, gui
import random
import threading
from client_sub import ClientSub
from utils import get_unique_filename

# Setup experiment window
win = visual.Window(fullscr=False, color="black", units="norm")

# Create stimuli
instructions = visual.TextStim(win, text="Imagine performing the action shown.\n\nPress space to start and q to stop.", color="white")
fixation = visual.TextStim(win, text="+", color="white")
cue_left = visual.TextStim(win, text="Left Hand", color="white", pos=(-0.5, 0))
cue_right = visual.TextStim(win, text="Right Hand", color="white", pos=(0.5, 0))
cue_foot = visual.TextStim(win, text="Foot", color="white", pos=(0, -0.5))

# Experiment parameters
n_trials = 30
trial_duration = 4  # seconds
rest_duration = 2  # seconds
# cues = [cue_left, cue_right, cue_foot]
cues = [cue_left, cue_right]

DATA_LOG_FILE = 'logs/motor_imagery/data.json'
unique_data_log_file = get_unique_filename(DATA_LOG_FILE)
subscriber = ClientSub(sub_ip="localhost", sub_port=1000, sub_topic="ProcessedData")

data_lock = threading.Lock()
data = {"samplestamps": [], "samples" : [], "cues": []}

collect_data = False
current_cue_text = None

def get_data():
    global data, collect_data, current_cue_text
    get_channels = True

    trial_samplestamps = []
    trial_samples = []

    save_trial_data = False

    while True:
        try:
            samplestamps, samples, _ = subscriber.get_data()
        except Exception as e:
            raise e
        
        if collect_data:
            # if get_channels:
            #     for i in range(samples.shape[1]):
            #         data_samples[f"channel_{i+1}"] = []
            #     get_channels = False

            with data_lock:
                trial_samplestamps.extend(samplestamps.tolist())
                trial_samples.extend(samples.tolist())

                # for i in range(samples.shape[1]):
                #     data_samples[f"channel_{i+1}"].extend(samples[:, i].tolist())
            
            save_trial_data = True

        else:
            if save_trial_data:
                data["samplestamps"].append(trial_samplestamps)
                data["samples"].append(trial_samples)
                data["cues"].append(current_cue_text)
            
                trial_samplestamps = []
                trial_samples = []
                current_cue_text = None

                save_trial_data = False
        
        time.sleep(0.1)  # Adjust this sleep interval as needed

def save_data():
    global data
    with data_lock:
        with open(unique_data_log_file, "w") as json_file:
            json.dump(data, json_file, indent=4)

# Start the data acquisition thread
data_thread = threading.Thread(target=get_data)
data_thread.daemon = True
data_thread.start()

# Show instructions
instructions.draw()
win.flip()
event.waitKeys(keyList=['space'])

# Main experiment loop
for trial in range(n_trials):
    # Show fixation
    fixation.draw()
    win.flip()
    core.wait(rest_duration)
    
    # Show cue
    cue = random.choice(cues)
    cue.draw()
    win.flip()
    collect_data = True
    current_cue_text = cue.text
    trial_clock = core.Clock()

    # Wait for trial duration or key press
    keys = event.waitKeys(maxWait=trial_duration, keyList=['q', 'space'])
    collect_data = False

    # Check for quit signal
    if keys and 'q' in keys:
        break

    # Record response time if space was pressed
    if keys and 'space' in keys:
        rt = trial_clock.getTime()    
        print(f"Trial {trial+1}: Response time = {rt:.2f}s")
    else:
        print(f"Trial {trial+1}: No response")

# Clean up
save_data()
win.close()
core.quit()
