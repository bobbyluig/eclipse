import time
from pydub import AudioSegment
from pydub.playback import play
from threading import Thread
import sched
from agility.main import Agility
from cerebral.pack1.hippocampus import Android

song = AudioSegment.from_mp3('tiger.mp3')
song = song[570:] # 570

agility = Agility(Android.robot)
s = sched.scheduler()

# Punch.
punch = [(0, 0, -15), (0, 0, -7)]

# Sequence single.
QUARTER = 552
EIGHTH = 276
SIXTEENTH = 138

sequence = [
    (1, EIGHTH, punch),
    (None, EIGHTH + QUARTER, None),
    (1, SIXTEENTH, punch),
    (None, EIGHTH, None),
    (1, SIXTEENTH, punch),
    (None, EIGHTH, None),
    (1, EIGHTH, punch),
    (None, QUARTER * 2, None),
    (1, SIXTEENTH, punch),
    (None, EIGHTH, None),
    (1, SIXTEENTH, punch),
    (None, EIGHTH, None),
    (1, EIGHTH, punch),
    (None, QUARTER * 2, None),
    (1, SIXTEENTH, punch),
    (None, EIGHTH, None),
    (1, SIXTEENTH, punch),
    (None, EIGHTH, None),
    (1, EIGHTH + QUARTER * 4, punch),
    (None, 80, None),
]

sequence2 = [
    (1, EIGHTH, punch),
    (None, EIGHTH + QUARTER, None),
    (1, SIXTEENTH, punch),
    (None, EIGHTH, None),
    (1, SIXTEENTH, punch),
    (None, EIGHTH, None),
    (1, EIGHTH, punch),
    (None, QUARTER * 2 + EIGHTH, None),
    (1, SIXTEENTH, punch),
    (None, EIGHTH, None),
    (1, SIXTEENTH, punch),
    (None, EIGHTH, None),
    (1, EIGHTH, punch),
    (None, EIGHTH + QUARTER, None),
    (1, SIXTEENTH, punch),
    (None, EIGHTH, None),
    (1, SIXTEENTH, punch),
    (None, EIGHTH, None),
    (1, EIGHTH + QUARTER * 4, punch),
    (None, 80, None),
]

t = Thread(target=play, args=(song,))
t.start()

input('Go, musician.')

agility.animate_single(sequence + sequence2 + sequence + sequence)



