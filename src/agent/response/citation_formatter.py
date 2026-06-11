class CitationFormatter:

    def format_citations(
        self,
        response: str,
        sources: list
    ) -> str:

        if not sources:
            return response

        # Build doc reference map
        doc_map = {
            src.get("document_id"): i + 1
            for i, src in enumerate(sources)
        }

        # naive sentence split
        sentences = [
            s.strip()
            for s in response.split(".")
            if s.strip()
        ]

        formatted_sentences = []

        for sentence in sentences:

            # naive matching: check which doc supports sentence
            matched = False

            for src in sources:

                doc_text = src.get("content", "").lower()

                if sentence.lower()[:20] in doc_text:
                    doc_id = src.get("document_id")
                    idx = doc_map.get(doc_id, None)

                    if idx:
                        sentence += f" [{idx}]"
                        matched = True
                        break

            if not matched:
                sentence += " [uncited]"

            formatted_sentences.append(sentence)

        return ". ".join(formatted_sentences)