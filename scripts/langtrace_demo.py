from langtrace_python_sdk import langtrace
from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span
# Paste this code after your langtrace init function

from openai import OpenAI

langtrace.init(
    api_key="91e4463648736881178851e555131b0776b03d79b6d4fe8e4eef9e5a6363f49d"
)

@with_langtrace_root_span()
def example():
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "How many states of matter are there?"
            }
        ],
    )
    print(response.choices[0].message.content)

example()