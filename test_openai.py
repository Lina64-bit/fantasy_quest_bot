from image_generator import generate_character_image

path = generate_character_image(
    user_id=1,
    appearance="эльфийка с серебряными волосами и зелёным плащом"
)

print("Картинка создана:", path)