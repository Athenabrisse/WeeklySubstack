from openai import OpenAI
import yaml

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
        ]
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
    

text_test =1000*"Ceci est une phrase de test de quelques mots"
print(len(text_test))
print(get_gpt4_response(text_test))