SCENES = {
    "start": {
        "text": "Ты стоишь у ворот древнего замка. Что сделаешь?",
        "choices": [
            {"text": "Войти в замок", "next": "castle"},
            {"text": "Пойти в лес", "next": "forest"}
        ]
    },
    "castle": {
        "text": "Ты входишь в замок и видишь старого мага.",
        "choices": [
            {"text": "Поговорить с магом", "next": "wizard"},
            {"text": "Осмотреть зал", "next": "hall"}
        ]
    },
    "forest": {
        "text": "В лесу ты слышишь рык чудовища.",
        "choices": [
            {"text": "Спрятаться", "next": "hide"},
            {"text": "Идти на звук", "next": "monster"}
        ]
    }
}