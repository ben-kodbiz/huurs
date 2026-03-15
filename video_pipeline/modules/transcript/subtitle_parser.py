import re


class SubtitleParser:

    def parse(self, subtitle_file):
        """Parse subtitle file into transcript."""
        
        transcripts = []
        
        with open(subtitle_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Detect format (SRT or VTT)
        if content.startswith('WEBVTT'):
            transcripts = self._parse_vtt(content)
        else:
            transcripts = self._parse_srt(content)
        
        return transcripts
    
    def _parse_srt(self, content):
        """Parse SRT format subtitles."""
        
        transcripts = []
        blocks = content.strip().split('\n\n')
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                # Line 1: sequence number
                # Line 2: timestamp (00:00:00,000 --> 00:00:05,000)
                # Line 3+: text
                timestamp_str = lines[1].split(' --> ')[0].strip()
                text = ' '.join(lines[2:])
                
                # Convert timestamp to seconds
                timestamp = self._srt_time_to_seconds(timestamp_str)
                
                # Clean text (remove SRT tags)
                text = self._clean_text(text)
                
                transcripts.append({
                    "timestamp": timestamp,
                    "text": text
                })
        
        return transcripts
    
    def _parse_vtt(self, content):
        """Parse VTT format subtitles."""
        
        transcripts = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip WEBVTT header and metadata
            if line.startswith('WEBVTT') or line.startswith('Kind:') or line.startswith('Language:'):
                i += 1
                continue
            
            # Look for timestamp line
            if '-->' in line:
                timestamp_str = line.split(' --> ')[0].strip()
                timestamp = self._vtt_time_to_seconds(timestamp_str)
                
                # Collect text lines
                text_lines = []
                i += 1
                while i < len(lines) and lines[i].strip() and not '-->' in lines[i]:
                    text_lines.append(lines[i].strip())
                    i += 1
                
                text = ' '.join(text_lines)
                text = self._clean_text(text)
                
                transcripts.append({
                    "timestamp": timestamp,
                    "text": text
                })
            else:
                i += 1
        
        return transcripts
    
    def _srt_time_to_seconds(self, time_str):
        """Convert SRT timestamp (00:00:00,000) to seconds."""
        try:
            time_part, ms = time_str.replace(',', '.').split('.')
            h, m, s = map(int, time_part.split(':'))
            return h * 3600 + m * 60 + s + int(ms) / 1000
        except:
            return 0
    
    def _vtt_time_to_seconds(self, time_str):
        """Convert VTT timestamp (00:00:00.000) to seconds."""
        try:
            if '.' in time_str:
                time_part, ms = time_str.split('.')
                h, m, s = map(int, time_part.split(':'))
                return h * 3600 + m * 60 + s + int(ms) / 1000
            else:
                h, m, s = map(int, time_str.split(':'))
                return h * 3600 + m * 60 + s
        except:
            return 0
    
    def _clean_text(self, text):
        """Clean subtitle text from tags."""
        # Remove SRT/VTT tags
        text = re.sub(r'<[^>]+>', '', text)
        text = text.replace('{', '').replace('}', '')
        text = text.replace('\n', ' ')
        # Normalize whitespace
        text = ' '.join(text.split())
        return text