from llama_cpp import Llama

llm = Llama(
    model_path="storage/models/pegon-ai-text.gguf",
    n_ctx=2048,
    n_threads=4,
    temperature=0.3,
    top_p=0.8,
    repeat_penalty=1.2,
    verbose=False
)

def text_transliterate(text):
    user_input = text

    prompt = f"""<|im_start|>system
    Convert the following Latin-script text into Pegon (Arabic script for Javanese or Indonesian) based on phonetic transcription. Follow Pegon writing rules including appropriate vowel markings, consonant representation, and word separation. Do not translate or change the meaning, simply transcribe the pronunciation accurately into Arabic script. Output only the Pegon text.
    <|im_end|>
    <|im_start|>user
    {user_input}
    <|im_end|>
    <|im_start|>assistant
    """

    output = llm(prompt, max_tokens=360)
    pegon_text = output["choices"][0]["text"].strip()
    return pegon_text