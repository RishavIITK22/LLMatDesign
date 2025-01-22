import os
import openai
import google.generativeai as genai
import requests
from groq import Groq
gemini_safety_settings = [
    {"category": "HARM_CATEGORY_DANGEROUS", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

class AskLLM:
    def __init__(
        self, 
        llm_model, 
        api_key=None,
    ) -> None:
        self.llm_model = llm_model
        self.api_key=api_key
        # if self.llm_model.startswith('gpt'):
        #     api_key = api_key if api_key is not None else os.environ.get('OPENAI_API_KEY')

        #     if openai_organization is not None:
        #         self.client = openai.OpenAI(
        #             organization=openai_organization,
        #             api_key=api_key
        #         )
        #     else:
        #         self.client = openai.OpenAI(api_key=api_key)

        #     self.model_name = self.get_openai_model_name()
        if self.llm_model.startswith('llama'):
            if self.api_key is None:
                raise ValueError('Please provide a valid API key for LLaMA via Groq.')
            self.client = Groq(api_key=self.api_key)
            self.model_name = self.get_llama_model_name()
            
        elif self.llm_model.startswith('gemini'):

            api_key = api_key if api_key is not None else os.environ.get('GOOGLE_API_KEY')

            if api_key is None:
                raise ValueError('Please provide a valid Google API key.')
            
            genai.configure(api_key=api_key)
            self.model_name = self.get_gemini_model_name()
        else:
            raise ValueError('Supported models are LLama and Gemini LLM models.')
        
    
    def get_gemini_model_name(self):
        if self.llm_model == 'gemini-1.5-pro':
            return "gemini-1.5-pro"
        if self.llm_model=='gemini-1.5-flash':
            return "gemini-1.5-flash"
        else:
            raise ValueError('Supported Gemini models: Gemini-1.5-pro')
    def get_llama_model_name(self):
        if self.llm_model=='llama-3.3-70b-versatile':
            return "llama-3.3-70b-versatile"
        if self.llm_model=='llama-3.1-8b-instant':
            return "llama-3.1-8b-instant"
        if self.llm_model=='llama-guard-3-8b':
            return "llama-guard-3-8b"
        if self.llm_model=='llama3-70b-8192':
            return "llama3-70b-8192"
        if self.llm_model=='llama3-8b-8192':
            return "llama3-8b-8192"
        else:
            raise ValueError('Out of bound of supported llama models')
    
    def ask(self, prompt):
        if self.llm_model.startswith('llama'):
            return self.ask_llama(prompt)
        elif self.llm_model.startswith('gemini'):
            return self.ask_google(prompt)
        else:
            raise ValueError('Supported models are GPT and Gemini LLM models.')
    def ask_llama(self, prompt):
        try:
            # Use the Groq client to create a completion request
            completion = self.client.chat.completions.create(
                model=self.llm_model,  # Model name
                messages=[{"role": "user", "content": prompt.strip()}],  # Prompt formatted for chat
                temperature=0.7,
                max_completion_tokens=200,
                top_p=1,
                stream=True,  # Streaming output
                stop=None
            )

            # Gather and return the full response
            response_text = ""
            for chunk in completion:
                response_text += chunk.choices[0].delta.content or ""

            return response_text.strip()

        except Exception as e:
            raise Exception(f"Error during Groq API call: {e}")
        
    def ask_google(self, prompt):
        model = genai.GenerativeModel(self.model_name)
        response = model.generate_content(prompt, safety_settings=gemini_safety_settings)
        return response.text.strip()
