class TranscriptChunker:

    def chunk(self, transcript, size=8):

        chunks = []
        block = []

        for line in transcript:

            block.append(line)

            if len(block) >= size:
                chunks.append(block)
                block = []

        if block:
            chunks.append(block)

        return chunks