import pysubs2


class SubtitleParser:

    def parse(self, subtitle_file):
        """Parse subtitle file into transcript."""
        
        try:
            subs = pysubs2.load(subtitle_file)
        except Exception as e:
            # Try loading as VTT with different format
            print(f"[WARN] Standard load failed, trying VTT format: {e}")
            subs = pysubs2.load(subtitle_file, encoding="utf-8")

        transcript = []

        for line in subs:
            # Convert milliseconds to seconds
            timestamp = line.start / 1000
            # Clean text (remove ASS/SSA tags)
            text = pysubs2.ssaevent.plaintext(line)

            transcript.append({
                "timestamp": timestamp,
                "text": text
            })

        return transcript