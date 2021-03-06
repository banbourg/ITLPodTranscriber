#!/usr/bin/env python

# Copyright 2017 Google Inc. All Rights Reserved.
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

"""Google Cloud Speech API sample application using the REST API for async
batch processing.
Example usage:
    python transcribe_async.py resources/audio.raw
    python transcribe_async.py gs://cloud-samples-tests/speech/vr.flac
"""

import argparse
import io
import pandas


elements = ["lutz", "salchow", "toe-loop", "axel", "sal", "quad", "quad loop", "quad sal", "quad toe", "quad lutz"]

sr_skaters = ["Satoko", "Satoko Miyahara", "Evan", "Evan Lysacek", "Midori Ito", "Yuzuru", "Yuzuru Hanyu", "Alina Zagitova",
           "Torvill and Dean", "Evgeny Plushenko", "Shizuka Arakawa", "Elizaveta Tuktamysheva", "Alexandra Trusova",
           "Boyang Jin", "Boyang", "Miki Ando", "Miki", "Kana Muramoto", "Kana", "Tonya Harding", "Tonya",
           "Evgenia Medvedeva", "Evgenia", "Stephane Lambiel", "Stephane", "Deniss Vasiljevs", "Deniss", "Johnny Weir",
           "Kenji Miyamoto", "Kenji", "Shae-Lynn Bourne", "Jeffrey Buttle"]

sr_skaters_k = ["Brian Orser","Valentina Marchei","Ondrej Hotarek", "Yu Xiaoyu", "Xiaoyu", "Ondrej", "Wakaba Higuchi", "Mariah Bell",
                "Ashley Wagner","Josh Farris","Sofia Samodurova","Mako Yamashita","Kaori Sakamoto","Shoma Uno","Shoma","Dmitri Aliev","Kolyada",
                "Mikhail","Mikhail Kolyada","Andrei Lazukin","Mihoko Higuchi","Mihoko","Kazuki Tomono","Kazuki","Satoko Miyahara", "Satoko",
                "Eunsoo Lim","Eunsoo","Nam Nguyen","Nam","Michal Brezina","Jimmy Ma","Jimmy","Vincent Zhou","Vincent","Madison Hubbell",
                "Hubbell","Zachary Donohue","Donohue","Christina Carreira","Anthony Ponomarenko","Misato Komatsubara","Tim Koleto","KoKo",
                "Elladj Balde"]

jgps_1_2 = ["Anastasia Mishina", "Aleksandr Galliamov", "Apollinariia Panfilova", "Dmitry Rylov", "Kseniia Akhanteva",
            "Valerii Kolesov", "Brooke Mcintosh", "Brandon Toste", "Stephen Gogolev", "Mitsuki Sumoto", "Daniel Grassl",
            "Mitsuki", "Donovan", "Jaeseok Kyeong", "Deniss", "Mauro Calcagno", "Aleksa Rakic", "Andrew Torgashev",
            "Elizaveta Khudaiberdieva", "Nikita Nazarov", "Elizaveta Shanaeva", "Devid Naryznyy", "Eliana Gropman",
            "Ian Somerville", "Jeongeun Jeon", "Sungmin Choi", "Demougeot", "Le Mercier", "Delcamp", "Gart",
            "Alicia Fabbri", "Paul Ayer", "Anna Shcherbakova", "Anna Tarusina", "Young You", "Yi Christy Leung",
            "Tomoe Kawabata", "Ji Hun To", "Linz", "Polina Kostiukovich",
            "Dmitrii Ialin", "Anastasia Poluianova", "Dmitry Sopot", "Alina Pepeleva", "Roman Pleshkov",
            "Laiken Lockley", "Keenan Prochnow", "Motong Liu", "Tianze Wang", "Camden Pulkinen", "Koshiro Shimada",
            "Roman Savosin", "Conrad Orzel", "Darian Kaptich", "Sofia Shevchenko", "Igor Eremenko", "Marjorie Lajoie",
            "Zachary Lagha", "Eva Kuts", "Dmitrii Mikhailov", "Rognatik", "Barshak", "Alena Kostornaia", "Alena Kanysheva",
            "Shiika Yoshioka", "Ting Cui", "Anna Kuzmenko", "Misha Ge"]

jgps_3_4 = ["Yelim Kim", "Kseniia Sinitsyna","Kirill Iakovlev","Yuto Kishina","Arina Ushakova","Maxim Nekrasov","Avonley Nguyen",
            "Vadym Kolesnik","Darya Popova","Volodymyr Byelikov","Anastasia Tarakanova", "Rion Sumiyoshi", "Petr Gumennik","Tomoki Hiwatashi",
            "Adam Siao Him Fa","Yuma Kagiyama","Polina Ivanenko","Daniil Karpov","Ksenia Konkina","Alexander Vakhnov"]

hosts = ["Lae", "Kat", "Evie", "Clara", "Kite", "Kar", "Karly"]

hosts_k = ["Yogeeta","Andrea","Maryam"]

misc = ["GOE", "rippon", "Grand Prix", "sectionals", "hammer-toe", "leg wrap", "tano", "Gadbois"]

misc_k = ["Biellmann","Dana-Farber","Ondrej Nepela"]

usernames = ["cyberswansp", "daejangie", "quadlutze", "doubleflutz", "tequilda", "axelsandwich", "yogeeta", "liliorum"]

usernames_k = ["mossyzinc", "starryyuzu", "luckyyloopss"]

fiction = ["Yuri on Ice", "Ginban Kaleidoscope", "Yuuri"]

phrase_list = elements + hosts + usernames + misc + jgps_1_2 + sr_skaters_k + jgps_3_4 + hosts_k + usernames_k + misc_k



def transcribe_gcs(gcs_uri):
    """Asynchronously transcribes the audio file specified by the gcs_uri."""
    from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types
    client = speech.SpeechClient()

    audio = types.RecognitionAudio(uri=gcs_uri)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=44100,
        language_code='en-US',
        # enable_automatic_punctuation=True,
        # enable_speaker_diarization=True,
        # diarization_speaker_count=2,
        speech_contexts=[types.SpeechContext(
            phrases=phrase_list
        )]
    )

    operation = client.long_running_recognize(config, audio)

    print('Waiting for operation to complete...')

    response = operation.result(timeout=10000)


    # Basic genevieve
    for result in response.results:
        print(f"{result.alternatives[0].transcript}")

    # result = response.results[-1]
    # words_info = result.alternatives[0].words
    # words_with_tags = []
    # for word_info in words_info:
    #     words_with_tags.append((word_info.speaker_tag, word_info.word))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        'path', help='File or GCS path for audio file to be recognized')
    args = parser.parse_args()
    if args.path.startswith('gs://'):
        transcribe_gcs(args.path)
    else:
        transcribe_file(args.path)
