import tiktoken

def chunk_text(text, chunk_size=500, overlap=50, model='gpt-3.5-turbo'):
        """Chunk the text into smaller parts for processing."""
        
        if not text:
              raise ValueError("Input text cannot be empty.")
        
        encoding = tiktoken.encoding_for_model(model)
        tokens =encoding.encode(text)

        chunks = []
        start = 0

        while start < len(tokens):
             end = start + chunk_size
             chunk = tokens[start:end]
             chunks.append(encoding.decode(chunk)) #  decode the chunk back to text
             start += chunk_size - overlap  # Move start forward by chunk size minus overlap
        
        return chunks