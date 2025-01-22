def ask_openai(self, prompt):
    #     prompt_chat = [{"role": "user", "content": prompt.strip()}]
    #     response = self.client.chat.completions.create(
    #         model=self.model_name,
    #         messages=prompt_chat,
    #         temperature=0,
    #         top_p=1,
    #         frequency_penalty=0.0,
    #         presence_penalty=0.0,
    #     )
    #     return response.choices[0].message.content.strip()