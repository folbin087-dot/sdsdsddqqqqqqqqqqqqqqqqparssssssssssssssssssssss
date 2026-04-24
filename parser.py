import asyncio
import json
import logging
import os
import warnings
from datetime import datetime
from logging.handlers import RotatingFileHandler

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage

from telethon import TelegramClient
from telethon.tl.functions.payments import GetStarGiftsRequest, GetResaleStarGiftsRequest
from telethon.errors import FloodWaitError, RPCError

# ================= ТВОИ ДАННЫЕ =================
BOT_TOKEN = "8697087057:AAGejOvXLVFJM8N1znxH9VeBUMFJpKTF6WI"
KANAL_LOGOV = -5131005896

API_ID = '23748926'
API_HASH = "f933830a116df1bece5ee84cba540b01"
SESSION_NAME = "session1"  # sessions/session1.session
# ===============================================

GIFTS = [
    ("1-may", "1 May"),
    ("brick", "Artisan Brick"),
    ("astral-shard", "Astral Shard"),
    ("backpack", "Backpack"),
    ("berry-box", "Berry Box"),
    ("big-year", "Big Year"),
    ("gold-nipples", "Bling Binky"),
    ("bonded-ring", "Bonded Ring"),
    ("book", "Book"),
    ("bow-tie", "Bow Tie"),
    ("bunny-muffin", "Bunny Muffin"),
    ("candle-lamp", "Candle Lamp"),
    ("case", "Case"),
    ("crystal-ball", "Crystal Ball"),
    ("crystal-eagle", "Crystal Eagle"),
    ("cupid-charm", "Cupid Charm"),
    ("desk-calendar", "Desk Calendar"),
    ("diamond-ring", "Diamond Ring"),
    ("dove-peace", "Dove of Peace"),
    ("durovs-boots", "Durov's Boots"),
    ("durovs-cap", "Durov's Cap"),
    ("durovs-coat", "Durov's Coat"),
    ("durovs-figurine", "Durov's Figurine"),
    ("durovs-sunglasses", "Durov's Sunglasses"),
    ("easter-cake", "Easter Cake"),
    ("easter-egg", "Easter Egg"),
    ("electric-skull", "Electric Skull"),
    ("eternal-candle", "Eternal Candle"),
    ("eternal-rose", "Eternal Rose"),
    ("evil-eye", "Evil Eye"),
    ("mosque", "Faith Amulet"),
    ("flying-broom", "Flying Broom"),
    ("gem-signet", "Gem Signet"),
    ("genie-lamp", "Genie Lamp"),
    ("gravestone", "Gravestone"),
    ("heart-locket", "Heart Locket"),
    ("heroic-helmet", "Heroic Helmet"),
    ("ion-gem", "Ion Gem"),
    ("ionic-dryer", "Ionic Dryer"),
    ("jelly-bunny", "Jelly Bunny"),
    ("jingle-bells", "Jingle Bells"),
    ("jolly-chimp", "Jolly Chimp"),
    ("joyful-bundle", "Joyful Bundle"),
    ("papakha", "Khabib's Papakha"),
    ("kissed-frog", "Kissed Frog"),
    ("kitty-medallion", "Kitty Medallion"),
    ("loot-bag", "Loot Bag"),
    ("love-candle", "Love Candle"),
    ("love-potion", "Love Potion"),
    ("low-rider", "Low Rider"),
    ("lush-bouquet", "Lush Bouquet"),
    ("mad-pumpkin", "Mad Pumpkin"),
    ("magic-potion", "Magic Potion"),
    ("mask", "Mask"),
    ("golden-biceps", "Mighty Arm"),
    ("mini-oscar", "Mini Oscar"),
    ("gold-pot", "Money Pot"),
    ("nail-bracelet", "Nail Bracelet"),
    ("neko-helmet", "Neko Helmet"),
    ("bear-new-year", "New Year's Bear"),
    ("pen", "Pen"),
    ("perfume-bottle", "Perfume Bottle"),
    ("pink-flamingo", "Pink Flamingo"),
    ("plush-pepe", "Plush Pepe"),
    ("precious-peach", "Precious Peach"),
    ("rare-bird", "Rare Bird"),
    ("record-player", "Record Player"),
    ("red-star", "Red Star"),
    ("resistance-dog", "Resistance Dog"),
    ("roses", "Roses"),
    ("sakura-flower", "Sakura Flower"),
    ("sandcastle", "Sandcastle"),
    ("santa-hat", "Santa Hat"),
    ("scared-cat", "Scared Cat"),
    ("sharp-tongue", "Sharp Tongue"),
    ("signet-ring", "Signet Ring"),
    ("skull-flower", "Skull Flower"),
    ("heels", "Sky Stilettos"),
    ("sleigh-bell", "Sleigh Bell"),
    ("snoop-cigar", "Snoop Cigar"),
    ("snow-globe", "Snow Globe"),
    ("snow-mittens", "Snow Mittens"),
    ("easter-backet", "Spring Basket"),
    ("spy-agaric", "Spy Agaric"),
    ("star-notepad", "Star Notepad"),
    ("statue-of-liberty", "Statue of Liberty"),
    ("surfboard", "Surfboard"),
    ("swiss-watch", "Swiss Watch"),
    ("plane", "Telegram Pin"),
    ("top-hat", "Top Hat"),
    ("torch-freedom", "Torch of Freedom"),
    ("toy-bear", "Toy Bear"),
    ("trapped-heart", "Trapped Heart"),
    ("trojan-horse", "Trojan Horse"),
    ("ufc-mystery-box", "UFC Strike"),
    ("valentine-box", "Valentine Box"),
    ("medal", "Victory Medal"),
    ("vintage-sigar", "Vintage Cigar"),
    ("voodoo-doll", "Voodoo Doll"),
    ("westside-sign", "Westside Sign"),
    ("witch-hat", "Witch Hat"),
]


# ====== НАСТРОЙКИ СКОРОСТИ (для 1 сессии) ======
POLL_DELAY = 0.7              
RESALE_LIMIT = 15
RESALE_CONCURRENCY = 1     
DISCOVERY_CONCURRENCY = 4  
DISCOVERY_RETRY_EVERY = 180       
# ===============================================

# ====== PERSISTENCE ======
SEEN_FILE = "seen.json"
SEEN_AUTOSAVE_EVERY = 30
# ========================

# ====== AUTO-RESTART ======
WORKER_RESTART_BASE_DELAY = 2
WORKER_RESTART_MAX_DELAY = 60
# ==========================

warnings.filterwarnings("ignore", category=UserWarning)

os.makedirs("sessions", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# ----- ЛОГИ -----
logger = logging.getLogger("gift_parser")
logger.setLevel(logging.INFO)

fmt = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

file_handler = RotatingFileHandler(
    "logs/app.log",
    maxBytes=3 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8"
)
file_handler.setFormatter(fmt)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(fmt)
logger.addHandler(console_handler)
# ----------------

bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

running = False
client: TelegramClient | None = None
tasks: list[asyncio.Task] = []

seen: set[str] = set()
seen_lock = asyncio.Lock()

# key -> gift_id (находим через discovery)
gift_id_map: dict[str, int] = {}
gift_map_lock = asyncio.Lock()

last_discovery_ts = 0


def log_ok(gift, link):
    msg = f"✅ {gift} | {link}"
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    logger.info(msg)


def log_err(text):
    msg = f"❌ {text}"
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    logger.warning(msg)


# --------- SEEN LOAD/SAVE ----------
def load_seen_from_file() -> set[str]:
    if not os.path.exists(SEEN_FILE):
        return set()
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return set(str(x) for x in data)
        return set()
    except Exception as e:
        logger.warning(f"Failed to load {SEEN_FILE}: {e}")
        return set()


async def save_seen_to_file():
    async with seen_lock:
        data = list(seen)

    tmp = SEEN_FILE + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        os.replace(tmp, SEEN_FILE)
        logger.info(f"seen saved: {len(data)}")
    except Exception as e:
        logger.warning(f"Failed to save {SEEN_FILE}: {e}")


async def autosave_seen_loop():
    while running:
        await asyncio.sleep(SEEN_AUTOSAVE_EVERY)
        await save_seen_to_file()
# ----------------------------------


@dp.message(Command("start"))
async def start_cmd(msg: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🟢 Старт", callback_data="on"),
        InlineKeyboardButton(text="🔴 Стоп", callback_data="off"),
    ]])
    await msg.answer("🚀 Парсер готов (1 сессия)", reply_markup=kb)


async def fetch_resale(tg: TelegramClient, gift_id: int):
    try:
        return await tg(GetResaleStarGiftsRequest(
            gift_id=gift_id,
            offset="",
            limit=RESALE_LIMIT,
            sort_by_price=False,
            sort_by_num=False,
            attributes_hash=0
        ))
    except FloodWaitError as e:
        log_err(f"FloodWait {e.seconds}s")
        await asyncio.sleep(e.seconds)
        return None
    except RPCError as e:
        log_err(f"RPCError: {e}")
        return None
    except Exception as e:
        log_err(f"Resale error: {e}")
        return None


async def discover_gift_ids(tg: TelegramClient):
    """
    Discovery: находит key -> gift_id через title подарков.
    """
    global last_discovery_ts

    stars = await tg(GetStarGiftsRequest(hash=0))
    
    # какие ключи ещё не найдены
    async with gift_map_lock:
        already = set(gift_id_map.keys())
    needed = [k for (k, _n) in GIFTS if k not in already]

    if not needed:
        logger.info("✅ Все подарки уже найдены, discovery пропущен")
        return

    logger.info(f"discovery: need {len(needed)}/{len(GIFTS)}, total_gifts={len(stars.gifts)}")
    print(f"   ⏳ Ищу {len(needed)} подарков в {len(stars.gifts)} доступных...")

    found_local: dict[str, int] = {}
    
    # Маппинг display_name (lower) -> key для быстрого точного поиска
    name_to_key = {name.lower(): key for key, name in GIFTS}
    # Маппинг key (с дефисами заменёнными на пробелы) -> key
    slug_to_key = {key.replace("-", " "): key for key, _name in GIFTS}

    for gift in stars.gifts:
        gift_id = gift.id
        title = getattr(gift, "title", None)

        if not title:
            continue

        title_lower = title.lower().strip()

        # Точное совпадение по display_name
        matched_key = name_to_key.get(title_lower)
        # Точное совпадение по slug-key (с пробелами вместо дефисов)
        if not matched_key:
            matched_key = slug_to_key.get(title_lower)

        if matched_key and matched_key not in found_local:
            found_local[matched_key] = gift_id
            print(f"      ✅ Найден: {matched_key} -> {title} (ID: {gift_id})")
            logger.info(f"Found: {matched_key} -> {title} (ID: {gift_id})")

    if found_local:
        async with gift_map_lock:
            gift_id_map.update(found_local)
        print(f"   ✅ Discovery завершен: найдено {len(found_local)} подарков")
        logger.info(f"✅ Discovery завершен: найдено {len(found_local)} подарков")
        logger.info(f"gift_id_map: {gift_id_map}")
    else:
        print(f"   ⚠️  Discovery: подарки не найдены")
        logger.info("⚠️  discovery: found nothing")

    last_discovery_ts = int(datetime.now().timestamp())


@dp.callback_query(F.data == "on")
async def start_parse(cb: CallbackQuery):
    global running, client, seen

    if running:
        await cb.answer("Уже работает")
        return

    running = True
    await cb.answer("🔥 Запущено")
    
    print("\n" + "="*60)
    print("🔥 ЗАПУСК ПАРСЕРА")
    print("="*60)
    logger.info("="*60)
    logger.info("🔥 ЗАПУСК ПАРСЕРА")
    logger.info("="*60)

    # грузим seen
    print("📂 Загрузка виденных подарков...")
    seen = load_seen_from_file()
    print(f"   ✅ Загружено: {len(seen)} подарков")
    logger.info(f"✅ Seen loaded: {len(seen)}")

    # telethon client
    session_path = f"sessions/{SESSION_NAME}"
    print(f"\n🔐 Подключение к Telegram...")
    print(f"   Сессия: {session_path}.session")
    logger.info(f"Подключение к Telegram (сессия: {session_path})")
    
    tg = TelegramClient(session_path, API_ID, API_HASH)

    try:
        print("   ⏳ Подключение...")
        await tg.connect()
        print("   ✅ Подключено к Telegram")
        logger.info("✅ Подключено к Telegram")

        print("   ⏳ Проверка авторизации...")
        if not await tg.is_user_authorized():
            print("   ❌ Сессия не авторизована")
            await cb.message.answer(
                "❌ Сессия не авторизована.\n\n"
                "Решение:\n"
                "1. Запусти login.py для регистрации сессии\n"
                "2. Введи номер телефона и код подтверждения\n"
                "3. После успешной авторизации запусти парсер снова"
            )
            await tg.disconnect()
            running = False
            logger.warning("❌ Session not authorized")
            return

        print("   ✅ Авторизация успешна")
        me = await tg.get_me()
        client = tg
        print(f"   👤 Пользователь: {me.first_name} (@{me.username or 'нет'})")
        logger.info(f"✅ Авторизован: {me.first_name} (@{me.username or 'нет'})")
        await cb.message.answer(f"✅ Авторизован как @{me.username or me.first_name}")

        # первичный discovery
        print(f"\n🔍 Поиск ID подарков (discovery)...")
        logger.info("🔍 Начало discovery")
        try:
            await discover_gift_ids(tg)
            print(f"   ✅ Discovery завершен")
            logger.info(f"✅ Discovery завершен, найдено: {len(gift_id_map)} подарков")
        except Exception as e:
            print(f"   ⚠️  Ошибка discovery: {e}")
            logger.warning(f"⚠️  Discovery error: {e}")

        # автосейв seen
        print(f"\n⏱️  Запуск автосохранения (каждые {SEEN_AUTOSAVE_EVERY}с)...")
        tasks.append(asyncio.create_task(autosave_seen_loop()))
        logger.info(f"✅ Автосохранение запущено")

        # воркер под супервизором
        print(f"👷 Запуск воркера (опрос каждые {POLL_DELAY}с)...")
        tasks.append(asyncio.create_task(worker_supervisor()))
        logger.info(f"✅ Воркер запущен")
        
        print("="*60)
        print("✅ ПАРСЕР РАБОТАЕТ")
        print("="*60 + "\n")
        logger.info("="*60)
        logger.info("✅ ПАРСЕР РАБОТАЕТ")
        logger.info("="*60)

    except Exception as e:
        print(f"   ❌ Ошибка подключения: {e}")
        await cb.message.answer(f"❌ Ошибка подключения: {e}")
        await tg.disconnect()
        running = False
        logger.error(f"❌ Connection error: {e}")


@dp.callback_query(F.data == "off")
async def stop_parse(cb: CallbackQuery):
    global running, client
    running = False

    for t in tasks:
        t.cancel()
    tasks.clear()

    if client:
        try:
            await client.disconnect()
        except Exception:
            pass
        client = None

    await save_seen_to_file()

    await cb.answer("🛑 Остановлено")
    logger.info("Stopped by user")


async def worker():
    """
    Основной цикл: работает только по найденным gift_id.
    Если чего-то не нашли — раз в DISCOVERY_RETRY_EVERY секунд пробуем дорискаверить.
    """
    global last_discovery_ts
    assert client is not None
    sem = asyncio.Semaphore(RESALE_CONCURRENCY)

    while running:
        # если не все gifts найдены — периодически делаем discovery
        async with gift_map_lock:
            have = set(gift_id_map.keys())
        want = set(k for k, _n in GIFTS)

        now_ts = int(datetime.now().timestamp())
        if have != want and (now_ts - last_discovery_ts) >= DISCOVERY_RETRY_EVERY:
            try:
                await discover_gift_ids(client)
            except Exception as e:
                log_err(f"discovery retry err: {e}")

        # строим targets только по найденным gift_id
        async with gift_map_lock:
            targets = [(k, n, gift_id_map.get(k)) for k, n in GIFTS if gift_id_map.get(k)]

        if not targets:
            logger.info("No targets yet (gift_id_map empty). Waiting...")
            await asyncio.sleep(2)
            continue

        async def job(key, name, gid):
            async with sem:
                resale = await fetch_resale(client, gid)
            if not resale:
                return

            for item in resale.gifts:
                slug = getattr(item, "slug", "")
                if not slug:
                    continue

                item_title = getattr(item, "title", "").lower().strip()
                key_normalized = key.replace("-", " ")
                name_lower = name.lower()

                # Точное совпадение: title == display_name ИЛИ title == key (с пробелами)
                if item_title != name_lower and item_title != key_normalized:
                    continue

                async with seen_lock:
                    if slug in seen:
                        continue
                    seen.add(slug)

                # Получаем информацию о цене (Stars и TON)
                resell_amount = getattr(item, "resell_amount", None)
                price_stars = None
                price_ton = None

                if resell_amount and isinstance(resell_amount, list):
                    for amount_obj in resell_amount:
                        obj_type = type(amount_obj).__name__
                        amount = getattr(amount_obj, "amount", None)
                        if amount is None:
                            continue

                        if obj_type == "StarsAmount":
                            price_stars = int(amount)
                        elif obj_type == "StarsTonAmount":
                            price_ton = amount / 1_000_000_000

                elif resell_amount and not isinstance(resell_amount, list):
                    obj_type = type(resell_amount).__name__
                    amount = getattr(resell_amount, "amount", None)
                    if amount is not None:
                        if obj_type == "StarsAmount":
                            price_stars = int(amount)
                        elif obj_type == "StarsTonAmount":
                            price_ton = amount / 1_000_000_000

                # Формируем строку цены
                if price_stars is not None and price_ton is not None:
                    price_str = f"{price_stars} ⭐ / {price_ton:.2f} TON"
                elif price_stars is not None:
                    price_str = f"{price_stars} ⭐"
                elif price_ton is not None:
                    price_str = f"{price_ton:.2f} TON"
                else:
                    price_str = "N/A"
                
                # Получаем информацию о продавце
                seller_name = "Unknown"
                owner_id = getattr(item, "owner_id", None)
                owner_name = getattr(item, "owner_name", None)
                
                if owner_name:
                    seller_name = owner_name
                elif owner_id:
                    # Пробуем получить информацию о пользователе по ID
                    try:
                        user = await client.get_entity(owner_id)
                        if hasattr(user, 'username') and user.username:
                            seller_name = f"@{user.username}"
                        elif hasattr(user, 'first_name') and user.first_name:
                            seller_name = user.first_name
                        else:
                            seller_name = f"ID:{owner_id}"
                    except Exception as e:
                        logger.debug(f"Failed to get user {owner_id}: {e}")
                        seller_name = f"ID:{owner_id}"
                
                title = getattr(item, "title", name)
                
                link = f"https://t.me/nft/{slug}"
                
                # Форматируем сообщение
                message = (
                    f"🆕 НОВЫЙ ЛИСТИНГ!\n\n"
                    f"🎁 Гифт: {title}\n"
                    f"💰 Цена: {price_str}\n"
                    f"🖼 Модель: {name}\n"
                    f"👤 Продавец: {seller_name}\n"
                    f"✨ Статус: ⭐ Premium\n"
                    f"🔗 {slug} ({link})\n"
                    f"🕐 {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n\n"
                    f"Creator By @Blessin"
                )
                
                await client.send_message(KANAL_LOGOV, message)
                log_ok(name, link)

        await asyncio.gather(*(job(k, n, gid) for k, n, gid in targets))
        await asyncio.sleep(POLL_DELAY)


async def worker_supervisor():
    """
    Если воркер упал — перезапуск с backoff.
    """
    delay = WORKER_RESTART_BASE_DELAY
    while running:
        try:
            await worker()
            return
        except asyncio.CancelledError:
            return
        except Exception as e:
            log_err(f"WORKER CRASH: {e} | restart in {delay}s")
            await asyncio.sleep(delay)
            delay = min(delay * 2, WORKER_RESTART_MAX_DELAY)


async def main():
    print("\n" + "="*60)
    print("🚀 ЗАПУСК ПАРСЕРА ПОДАРКОВ TELEGRAM")
    print("="*60)
    
    logger.info("="*60)
    logger.info("🚀 ЗАПУСК ПАРСЕРА")
    logger.info("="*60)
    
    # Проверка конфигурации
    print(f"📋 Конфигурация:")
    print(f"   • BOT_TOKEN: {'✅ заполнен' if BOT_TOKEN else '❌ не заполнен'}")
    print(f"   • API_ID: {'✅ заполнен' if API_ID else '❌ не заполнен'}")
    print(f"   • API_HASH: {'✅ заполнен' if API_HASH else '❌ не заполнен'}")
    print(f"   • Канал логов: {KANAL_LOGOV}")
    print(f"   • Отслеживаемых подарков: {len(GIFTS)}")
    
    logger.info(f"BOT_TOKEN: {'✅' if BOT_TOKEN else '❌'}")
    logger.info(f"API_ID: {'✅' if API_ID else '❌'}")
    logger.info(f"API_HASH: {'✅' if API_HASH else '❌'}")
    logger.info(f"Отслеживаемых подарков: {len(GIFTS)}")
    
    # Проверка файлов
    print(f"\n📁 Файлы:")
    session_file = f"sessions/{SESSION_NAME}.session"
    print(f"   • Сессия: {session_file} {'✅' if os.path.exists(session_file) else '❌'}")
    print(f"   • Seen.json: seen.json {'✅' if os.path.exists(SEEN_FILE) else '❌'}")
    
    logger.info(f"Сессия существует: {os.path.exists(session_file)}")
    logger.info(f"Seen.json существует: {os.path.exists(SEEN_FILE)}")
    
    # Инициализация бота
    print(f"\n🤖 Инициализация бота...")
    try:
        bot_info = await bot.get_me()
        print(f"   ✅ Бот: @{bot_info.username}")
        logger.info(f"✅ Бот инициализирован: @{bot_info.username}")
    except Exception as e:
        print(f"   ❌ Ошибка инициализации бота: {e}")
        logger.error(f"❌ Ошибка инициализации бота: {e}")
        return
    
    print(f"\n⏳ Ожидание команд от пользователя...")
    print(f"   Отправь /start в чат с ботом для управления парсером")
    print("="*60 + "\n")
    
    logger.info("✅ Парсер готов к работе")
    logger.info("Ожидание команд...")
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("⏳ Инициализация парсера...")
    print("="*60 + "\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Парсер остановлен пользователем")
        logger.info("🛑 Парсер остановлен пользователем")
    except Exception as e:
        print(f"\n\n❌ Критическая ошибка: {e}")
        logger.critical(f"❌ Критическая ошибка: {e}")
