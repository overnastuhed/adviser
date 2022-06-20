class ActorNameExtractor:
    """Very simple NLU for the movie domain."""

    def __init__(self, placeholder):
        from transformers import AutoTokenizer, AutoModelForTokenClassification
        from transformers import pipeline

        self.placeholder = placeholder

        tokenizer = AutoTokenizer.from_pretrained("elastic/distilbert-base-uncased-finetuned-conll03-english")
        model = AutoModelForTokenClassification.from_pretrained("elastic/distilbert-base-uncased-finetuned-conll03-english")

        self.ner = pipeline("ner", model=model, tokenizer=tokenizer)

    def __call__(self, text):
        results = self.ner(text)
        actors = []
        current_entity_start = None
        current_entity_end = None
        for result in results:
            if result["entity"] == "B-PER":
                start = result["start"]
                end = result["end"]
                if current_entity_start is not None and current_entity_start != start:
                    actors.append(text[current_entity_start:current_entity_end])

                current_entity_start = start
                current_entity_end = end
            elif result["entity"] == "I-PER":
                current_entity_end = result["end"]
            else:
                if current_entity_start is not None:
                    actors.append(text[current_entity_start:current_entity_end])
                    current_entity_start = None
                    current_entity_end = None

        if current_entity_start is not None:
            actors.append(text[current_entity_start:current_entity_end])

        for actor in actors:
            text = text.replace(actor, self.placeholder)

        return text, actors