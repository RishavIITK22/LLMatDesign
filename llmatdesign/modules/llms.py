import os
import openai
from openai import OpenAI
import google.generativeai as genai
import groq
import requests
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
        openai_organization=None, 
    ) -> None:
        self.llm_model = llm_model
        self.api_key = api_key
        if self.llm_model.startswith('gpt'):
            api_key = api_key if api_key is not None else os.environ.get('OPENAI_API_KEY')

            if openai_organization is not None:
                self.client = openai.OpenAI(
                    organization=openai_organization,
                    api_key=api_key
                )
            else:
                self.client = openai.OpenAI(api_key=api_key)

            self.model_name = self.get_openai_model_name()
            
        elif self.llm_model.startswith('gemini'):

            api_key = api_key if api_key is not None else os.environ.get('GOOGLE_API_KEY')

            if api_key is None:
                raise ValueError('Please provide a valid Google API key.')
            
            genai.configure(api_key=api_key)
            self.model_name = self.get_gemini_model_name()

        elif self.llm_model.startswith('groq'):
            api_key = api_key if api_key is not None else os.environ.get('GROQ_API_KEY')
            if api_key is None:
                raise ValueError('Please provide a valid Groq API key.')
            self.url = "https://api.groq.com/openai/v1/chat/completions"
            self.client = groq.Groq(api_key=api_key)
            self.model_name = self.get_groq_model_name()
        elif self.llm_model.startswith('krutrim'):
            api_key = api_key if api_key is not None else os.environ.get('KRUTRIM_API_KEY')
            if not api_key:
                raise ValueError('Please provide a valid Krutrim API key')
            
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://cloud.olakrutrim.com/v1"
            )
            self.model_name = self.get_krutrim_model_name()
        else:
            raise ValueError('Supported models are GPT, Gemini, Groq , OLAKrutrim LLM models.')
        
    def get_openai_model_name(self):
        if self.llm_model == 'gpt-4':
            return "gpt-4-0125-preview"
        elif self.llm_model == 'gpt-4o':
            return "gpt-4o"
        elif self.llm_model == 'gpt-3.5':
            return "gpt-3.5-turbo-0125"
        else:
            raise ValueError('Supported OpenAI models are GPT-3.5 and GPT-4.')
    
    def get_gemini_model_name(self):
        if self.llm_model == 'gemini-2.0-flash':
            return "gemini-2.0-flash"
        else:
            raise ValueError('Supported Gemini models: Gemini-2.0-flash.')
    def get_groq_model_name(self):
        if self.llm_model == 'llama-3.3-70b-versatile':
            return "llama-3.3-70b-versatile"
        else:
            raise ValueError('Supported Groq models: llama3-70b.')
        
    def get_krutrim_model_name(self):
        """Extract model name from llm_model string (e.g. 'krutrim-ai/1')"""
        if '-' in self.llm_model:
            return self.llm_model.split('-', 1)[1]
        return "ai/1"  # default model

    def ask(self, prompt):
        if self.llm_model.startswith('gpt'):
            return self.ask_openai(prompt)
        elif self.llm_model.startswith('gemini'):
            return self.ask_google(prompt)
        elif self.llm_model.startswith('groq'):
            return self.ask_groq(prompt)
        elif self.llm_model.startswith('krutrim'):
            return self.ask_krutrim(prompt)
        else:
            raise ValueError('Supported models are GPT and Gemini LLM models.')
    
    def ask_openai(self, prompt):
        prompt_chat = [{"role": "user", "content": prompt.strip()}]
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=prompt_chat,
            temperature=0,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )
        return response.choices[0].message.content.strip()
        
    def ask_google(self, prompt):
        model = genai.GenerativeModel(self.model_name)
        response = model.generate_content(prompt, safety_settings=gemini_safety_settings)
        return response.text.strip()
    def ask_groq(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model_name,
            "messages": [{"role": "system", "content": "You are an AI assistant."},
                         {"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        response = requests.post(self.url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print("Error:", response.text)
            return None
        
    def ask_krutrim(self, prompt):
        prompt_chat = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt.strip()}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model="Llama-3.3-70B-Instruct",
                messages=prompt_chat,
                temperature=0,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                max_tokens=1024
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Krutrim API Error: {str(e)}")
            return None