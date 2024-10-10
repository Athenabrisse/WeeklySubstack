from openai import OpenAI
import yaml
from get_mails import get_email
import json

with open('credentials.yaml', 'r') as file:
    credentials = yaml.safe_load(file)
    api_key = credentials['openai']


def get_gpt4_response(prompt):
    """Send the prompt to GPT-4 and return the response along with the price."""

    client = OpenAI(api_key=api_key)
    # Send the prompt to GPT-4
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        response_format={ "type": "json_object" },
    )
    
    # Extract the response text
    completion_text = response.choices[0].message.content
    
    # Extract the token usage information
    tokens_in = response.usage.prompt_tokens
    tokens_out = response.usage.completion_tokens
    price_in = tokens_in / 1000000 * 0.075
    price_out = tokens_out / 1000000 * 0.3
    print(f'Price : {price_in + price_out:.7f}$')
    
    return completion_text
    
mails = get_email()

text_test =f"""Donne moi un json contenant les trois thèmes principaux abordés dans ces newsletters :{mails}.
Le json contiendra une clé "themes" qui contiendra une liste de 3 strings qui correspondent aux themes."""

ans = get_gpt4_response(text_test)

themes = json.loads(ans)['themes']

for i,theme in enumerate(themes):
    print(f'Theme {i+1}: {theme}')