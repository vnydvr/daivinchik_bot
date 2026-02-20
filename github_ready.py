import asyncio
from telethon import TelegramClient, events
import winsound
import re

api_id = 1234 #вставь своё
api_hash = 'qwerty123' #вставь своё

BOT_USERNAME = 'leomatchbot'

client = TelegramClient('session', api_id, api_hash)

# ------------------ ИЗМЕНЯЕМЫЕ ПАРАМЕТРЫ -------------
GREENWORDS = ["example_1", "example_2"] #корни слов

BANWORDS = ["example_1", "example_2"]#корни слов

min_age = example
max_age = example

town = ["example_1", "example_2"] #ОБЯЗАТЕЛЬНО С МАЛЕНЬКОЙ БУКВЫ И БЕЗ ОКОНЧАНИЯ (пример: Москва -> москв) {учитывайте что некоторые ебланы пишут название города с ошибками либо писать район вместо города}

words_in_profile = example # минимальная длина анкеты по словам(без учёта блока до длинного тире)

# ------------------ ВСПОМОГАТЕЛЬНЫЕ ------------------

def decision(text: str) -> str:
    if '–' not in text:
        print('► Нету длинного тире- анкета без описания.')
        return "dislike"

    elif not age_fine(text):
        print('► Не подходит под возрастной фильтр.')
        return 'dislike'

    elif '–' in text:
        if is_in_blacklist(text):
            print('► Анкета в чёрном списке.')
            return ("dislike")
        else:
            if has_greenword(text):
                print('► Есть гринфлаги.')
                winsound.Beep(1000, 300)
                return 'wait'
            if has_banword(text):
                print('► Есть редфлаги.')
                return 'dislike'
            profile = text.split('–', 1)[1].strip()
            words = re.findall(r'\w+', profile)
            if len(words) < words_in_profile:
                print('► Слишком короткая анкета')
                return "dislike"
        winsound.Beep(1000,300)
        return "wait"


def add_to_blacklist(text: str):
    with open("blacklist.txt", "a", encoding="utf-8") as f:
        f.write(text.replace("\n", " ") + "\n")



async def send_dislike(event):
    await event.reply("👎")


async def send_like(event):
    await event.reply("❤️")


def is_in_blacklist(text: str) -> bool:
    text = text.replace('\n',' ')

    try:
        with open("blacklist.txt", "r", encoding="utf-8") as z:
            for line in z:
                if text == line.strip():
                    return True
    except FileNotFoundError:
        return False

    return False


def age_fine(text: str) -> bool:
    header = text.split("–", 1)[0]
    for i in range(min_age, max_age + 1):
        if f', {i},' in header:
            return True
    return False


def is_profile(text: str) -> bool:
    text = text.lower()
    for i in range(0,100):
        pattern = f', {i},'
        if pattern in text and any(t in text for t in town):
            return True
    return False


def has_greenword(text: str) -> bool:
    text = text.lower()
    return any(word in text for word in GREENWORDS)


def has_banword(text: str) -> bool:
    text = text.lower()
    return any(word in text for word in BANWORDS)

# ------------------ ОБРАБОТЧИК ------------------

@client.on(events.NewMessage(from_users=BOT_USERNAME))
async def handler(event):
    if not event.raw_text:
        return
    if event.raw_text.strip() == '✨🔍': #фикс чтобы программа не орала при выходе из спящего режима
        return
    #await asyncio.sleep(3)
    text = event.raw_text


    if not is_profile(text):
        print('НЕ АНКЕТА! ТРЕБУЕТСЯ РУЧНАЯ ПРОВЕРКА')
        winsound.Beep(1500, 1000)
        return

    print("\nНовая анкета:\n", text)

    result = decision(text)

    if result == "dislike":
        print("Авто: дизлайк")
        await send_dislike(event)
        return

    print("Ожидание решения: like / blacklist / skip")

    # ждём ввод пользователя в консоли
    loop = asyncio.get_event_loop()
    user_input = await loop.run_in_executor(None, input, "> ")

    user_input = user_input.strip().lower()

    if user_input == "like":
        await send_like(event)

    elif user_input == "blacklist":
        add_to_blacklist(text)
        await send_dislike(event)
        print("Добавлено в blacklist.txt")

    elif user_input == "skip":
        await send_dislike(event)

    else:
        print("Неизвестная команда")


# ------------------ ЗАПУСК ------------------

async def main():
    await client.start()
    print("Бот запущен. Отправь любое сообщение чтобы в ответ пришла анкета")
    await client.run_until_disconnected()

asyncio.run(main())