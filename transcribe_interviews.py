#!/usr/bin/env python

# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Cloud Speech API that takes audio file and transcribes it with timings.
based upon https://cloud.google.com/speech-to-text/docs/async-recognize#speech-async-recognize-gcs-python
Example usage:
    python transcribe_interviews.py gs://bucket_name/file_name.wav
"""

import argparse
import io
import time


def transcribe_interviews(gcs_uri):
    """Asynchronously transcribes the audio file specified by the gcs_uri."""
    from google.cloud import speech_v1p1beta1 as speech
    from google.cloud.speech_v1p1beta1 import enums
    from google.cloud.speech_v1p1beta1 import types
    client = speech.SpeechClient()

    audio = types.RecognitionAudio(uri=gcs_uri)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,    #this is for WAV files, you can use multiple types
        sample_rate_hertz=44100,
        language_code='en-US',
        #use_enhanced=True, #can only use if your ethics allows sending data offsite
        enable_word_time_offsets=True,
        enable_automatic_punctuation=True,
        model='Video')   # change this if you're doing focus groups

    operation = client.long_running_recognize(config, audio)

    print('A little man is now listening and transcribing...')
    response = operation.result(timeout=90000000)
    f = open("Interview 1.txt", "w")          #can change the file name that the text gets written to
    for i, result in enumerate(response.results):
        alternative = result.alternatives[0]
        f.write(str(i) + '\n')
        f.write('{}'.format(str(time.strftime('%H:%M:%S',time.gmtime(int(alternative.words[0].start_time.seconds))))))
        f.write('  -->  ')
        f.write('{}'.format(str(time.strftime('%H:%M:%S',time.gmtime(int(alternative.words[-1].end_time.seconds))))) + '\n')
        
        #f.write('speaker {} :'.format(alternative.words[0].speaker_tag))
        f.write(u'{}'.format(alternative.transcript)+ '\n\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('path', help='File to stream to the API')

    args = parser.parse_args()

    transcribe_interviews(args.path)