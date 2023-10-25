import multiprocessing
import os
import soundcard as sc
import soundfile as sf
import speech_recognition as sr
from os import path
import io
# import re
import time
from datetime import datetime, timedelta
# from deep_translator import GoogleTranslator

# TRANS_SOURCE = 'english'
# TRANS_TARGET = 'russian'

samplerate = 48000
record_len = 10
speaker_name = str(sc.default_speaker().name)
device = sc.get_microphone( id = speaker_name,
                            include_loopback = True)
recognizer = sr.Recognizer()
# expr = ":.*\"(.*)\""

def record_worker(record_queue):
    format = "%M:%S"
    def get_silence_duration(silence_start, silence_duration):
        silence_delta = timedelta(seconds = silence_duration)
        silence_start = end_time
        silence_end = silence_start + silence_delta
        return f'{silence_start.strftime(format)}-{silence_end.strftime(format)}: ...'
    with device.recorder(samplerate = samplerate) as mic:
        clula = io.BytesIO()
        silence = 0
        end_time = datetime.now()
        while True:
            start_time = datetime.now()
            data = mic.record(numframes = samplerate * record_len)
            if data[0][0] == 0:
                time.sleep(0.2)
                silence += 0.2
                if silence >= record_len:
                    print(get_silence_duration(end_time, silence))
                    end_time = datetime.now()
                    silence = 0
                continue
            if silence > 0:
                print(get_silence_duration(end_time, silence))
                end_time = datetime.now()
                silence = 0
            end_time = datetime.now()
            sf.write(   file = clula,
                        data = data,
                        samplerate = samplerate,
                        format = "WAV")
            clula.seek(0)
            record_time, recording = (f'{start_time.strftime(format)}-{end_time.strftime(format)}: ', clula)
            # record_queue.put(item)
            recognizing_process = multiprocessing.Process(target=recognize_worker, args=(record_time, recording))
            recognizing_process.start()

def recognize_worker(record_time, recording):
    with sr.AudioFile(recording) as source:
        audio = recognizer.record(source)
        res = recognizer.recognize_whisper( audio_data = audio,
                                                model = "base")
            # "base"    =  1GB RAM ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            # "small"   =  2GB RAM
            # "medium"  =  5GB RAM
            # larger models are slower!
        print(record_time, res)

# def recognize_worker(record_queue, recognize_queue):
#     recognizer = sr.Recognizer()
#     while True:
#         if not record_queue.empty():
#             # get the output from the queue as soon as it becomes available
#             record_time, recording = record_queue.get()
#             # process the output
#             with sr.AudioFile(recording) as source:
#                 audio = recognizer.record(source)
#             res = recognizer.recognize_whisper( audio_data = audio,
#                                                 model = "base")
#             # "base"    =  1GB RAM ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#             # "small"   =  2GB RAM
#             # "medium"  =  5GB RAM
#             # larger model is slower!
#             print(record_time, res)
#             # item = (record_time, res)
#             # recognize_queue.put(item)
#         else:
#             time.sleep(0.2)

# def trans_worker(recognize_queue):
#     # record_time, text = recognize_queue.get()
#     # trans = GoogleTranslator(source = SOURCE, target = TARGET).translate(text = text)
#     # print("text: " + res + '\n' + 'translation: ' + trans)
#     pass

if __name__ == "__main__":
    # create a queue to share data between processes
    record_queue = multiprocessing.Queue()
    # recognize_queue = multiprocessing.Queue()
    # trans_queue = multiprocessing.Queue()

    # create two processes, one for each worker function
    recording = multiprocessing.Process(target = record_worker, args = (record_queue, ))
    # recognizing = multiprocessing.Process(target = recognize_worker, args = (record_queue, recognize_queue))
    # translating = multiprocessing.Process(target = trans_worker, args = (recognize_queue))

    # start the processes
    recording.start()
    # recognizing.start()