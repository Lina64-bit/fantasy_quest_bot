import base64
import os

from bs4 import BeautifulSoup
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

from config import GIGACHAT_AUTH_KEY


def build_character_prompt(user_description: str) -> str:
    return (
        "Создай атмосферный портрет персонажа для тёмного фэнтези RPG "
        "в качественной пиксельной стилистике. "
        "Персонаж должен выглядеть серьёзно, героически и не карикатурно. "
        "Композиция: персонаж по центру, портрет или поясной портрет. "
        "Добавь выразительный фэнтези-фон: древний замок, лес, руины, "
        "магическое свечение, туман или ночное небо. "
        "Стиль: detailed pixel art, dark fantasy, cinematic lighting, "
        "dramatic shadows, medieval fantasy, high quality game art. "
        "Без текста, без логотипов, без водяных знаков. "
        f"Описание персонажа: {user_description}"
    )


def generate_character_image(user_id: int, appearance: str) -> str:
    os.makedirs("generated_images", exist_ok=True)

    giga = GigaChat(
        credentials=GIGACHAT_AUTH_KEY,
        verify_ssl_certs=False
    )

    payload = Chat(
        messages=[
            Messages(
                role=MessagesRole.SYSTEM,
               content=(
                 "Ты — профессиональный художник по концепт-арту для тёмного фэнтези RPG. "
                  "Создавай атмосферные пиксельные портреты персонажей с фоном. "
                  "Избегай мультяшного, шуточного и карикатурного стиля."
                )
            ),
            Messages(
                role=MessagesRole.USER,
                content=build_character_prompt(appearance)
            )
        ],
        function_call="auto"
    )

    response = giga.chat(payload)
    content = response.choices[0].message.content

    img_tag = BeautifulSoup(content, "html.parser").find("img")

    if img_tag is None:
        raise ValueError(f"GigaChat не вернул изображение. Ответ: {content}")

    file_id = img_tag.get("src")

    image = giga.get_image(file_id)

    file_path = f"generated_images/character_{user_id}.jpg"

    with open(file_path, "wb") as file:
        file.write(base64.b64decode(image.content))

    return file_path