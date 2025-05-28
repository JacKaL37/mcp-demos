
from langfuse import Langfuse
langfuse = Langfuse(
  secret_key="sk-lf-65750551-4c80-4935-a31f-93b5d506125b",
  public_key="pk-lf-b86b1f59-ae6f-4d57-8f54-cc1708816346",
  host="http://localhost:3000"
)

from langfuse.decorators import observe
from langfuse.openai import openai # OpenAI integration

import dotenv

dotenv.load_dotenv()
 
@observe()
def story():
    return openai.chat.completions.create(
        model="gpt-4o",
        messages=[
          {"role": "system", "content": "You are a great storyteller."},
          {"role": "user", "content": "Once upon a time in a galaxy far, far away..."}
        ],
    ).choices[0].message.content
 
@observe()
def main():
    return story()
 
main()