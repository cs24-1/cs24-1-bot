import dataclasses
import json

from openai import NotFoundError, OpenAI

from models.ai.response import CodeTranslateResponse
from utils.ai import system_data
from utils.constants import Constants


class AIUtils:

    def __init__(self):
        self.client = OpenAI(api_key=Constants.SECRETS.OPENAI_TOKEN)

    def code_translate(self, language: str, code: str) -> CodeTranslateResponse:
        response = self.client.chat.completions.create(
            model=Constants.AI.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_data.code_translate_system_message},
                {"role": "user", "content": f"{{\"code\": \"{code}\", \"language\": \"{language}\"}}"}
            ],
            response_format=system_data.code_translate_response_format, # type: ignore
            temperature=1,
            max_completion_tokens=1400,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        if response.choices[0].message.content is None:
            raise ValueError(
                "There was error getting the data from the OpenAI API."
            )

        json_data = json.loads(response.choices[0].message.content)

        return CodeTranslateResponse(
            detected_language=json_data["detected_language"],
            translated_language=json_data["translated_language"],
            translated_code=json_data["translated_code"],
            humorous_comment=json_data["humorous_comment"],
            tokens_used=response.usage.total_tokens
        )
