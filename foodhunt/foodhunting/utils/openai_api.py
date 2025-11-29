# # chatbot/utils/openai_api.py

# import openai
# from django.conf import settings
# from openai  import OpenAIError  # For error handling

# # Set OpenAI API key from Django settings
# openai.api_key = settings.OPENAI_API_KEY

# def get_chatgpt_response(prompt, model="gpt-4-turbo"):
#     """
#     Send a prompt to OpenAI ChatCompletion API and return the assistant's response.

#     Args:
#         prompt (str): The user's input prompt.
#         model (str): The OpenAI model to use. Defaults to "gpt-4-turbo".

#     Returns:
#         str: The text response from the model.

#     Raises:
#         ValueError: If prompt is empty.
#         OpenAIError: If the API call fails.
#     """
#     if not prompt:
#         raise ValueError("Prompt cannot be empty.")

#     try:
#         response = openai.ChatCompletion.create(
#             model=model,
#             messages=[
#                 {"role": "user", "content": prompt}
#             ]
#         )
#         return response.choices[0].message["content"]

#     except OpenAIError as e:
#         # You can log the error here if you want
#         raise OpenAIError(f"OpenAI API error: {e}")

#     except Exception as e:
#         # Handle other unexpected errors
#         raise Exception(f"Unexpected error: {e}")
