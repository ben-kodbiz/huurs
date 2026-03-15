import pysubs2


class SubtitleParser:

    def parse(self, subtitle_file):

        subs = pysubs2.load(subtitle_file)

        transcript = []

        for line in subs:

            timestamp = line.start / 1000
            text = line.text.replace("\n"," ")

            transcript.append({
                "timestamp": timestamp,
                "text": text
            })

        return transcript