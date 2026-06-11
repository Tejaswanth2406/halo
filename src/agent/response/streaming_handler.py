class StreamingHandler:

    def __init__(self, llm, retriever, synthesizer):
        self.llm = llm
        self.retriever = retriever
        self.synthesizer = synthesizer

    async def stream(
        self,
        query: str
    ) -> AsyncGenerator[str, None]:

        # 1. Retrieve context
        context = await self.retriever.retrieve(query)

        # 2. Convert context into prompt
        prompt = await self.synthesizer.synthesize(context)

        # 3. Stream response
        async for token in self.llm.stream(prompt):
            yield token