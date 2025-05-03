from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from decouple import config

import aiohttp

from create_bot import DialogStates
from assets.get_vacansies import fetch_vacancies
from assets.json import save_candidate_data
router = Router()

from decouple import config
import json
import os

HR_IDS = [998992278]

router = Router()


def build_yes_no_menu() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="Да", callback_data="yes"),
        types.InlineKeyboardButton(text="Нет", callback_data="no")
    )
    return builder.as_markup()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.set_state(DialogStates.waiting_for_name)
    await message.answer(
        "Добрый день, я HR бот для помощи по интересующим вакансиям.\nКак я могу к Вам обращаться?"
    )

@router.message(DialogStates.waiting_for_name)
async def process_get_name(message: types.Message, state: FSMContext):
    candidate_name = message.text.strip()
    await state.update_data(candidate_name=candidate_name)
    await state.set_state(DialogStates.greeting)
    text = (
        f"Здравствуйте {candidate_name}!\n"
        "Я помощник менеджера по персоналу компании «Роданика», производителя натуральных безалкогольных напитков.\n"
        "Я увидел Ваше резюме на работном сайте (Авито, НН, Работа в России) и нас заинтересовала Ваша кандидатура.\n"
        "Скажите, актуален для Вас еще поиск работы? Вам удобно сейчас говорить?"
    )
    await message.answer(text, reply_markup=build_yes_no_menu())

@router.callback_query(lambda c: c.data in ["yes", "no"], DialogStates.greeting)
async def process_greeting(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    candidate_name = user_data.get("candidate_name", "Кандидат")
    if callback.data == "yes":
        await state.set_state(DialogStates.company_presentation)
        text = (
            "Хорошо!\nПару слов скажу о нас.\n"
            "Мы производители натуральных безалкогольных напитков.\n"
            "Работа оператора линии заключается:\n"
            "- на узлах подачи бутылок, промывки, розлива и укупорки;\n"
            "- на узле наклеивания этикеток и упаковки.\n"
            f"{candidate_name}, скажите, что для Вас важно при выборе работы?"
        )
        await callback.message.reply(text)
    else:
        await callback.message.reply("Понял Вас! Желаю Вам отличного дня!")
        data = {
            "id": callback.from_user.id,
            "name": candidate_name,
            "vacancy": "Оператор линии",
            "status": "Отказ",
            "stage": "Приветствие",
            "reason": "Не ищет работу",
            "date": "2023-10-01"
        }
        save_candidate_data(data)
        await state.clear()
    await callback.answer()

@router.message(DialogStates.company_presentation)
async def process_company_presentation(message: types.Message, state: FSMContext):
    await state.update_data(candidate_priorities=message.text)
    await state.set_state(DialogStates.training_question)
    user_data = await state.get_data()
    candidate_name = user_data.get("candidate_name", "Кандидат")
    text = (
        f"Мы предлагаем:\n"
        "- акция: 4 мес работы и 13-я зарплата в кармане;\n"
        "- соц.пакет, 28 дней отпуска, можно отпроситься, найдя себе подмену;\n"
        "- теплый, чистый цех;\n"
        "- корпоративное такси (оговаривается отдельно);\n"
        "- внутренняя система бонусов и поощрений;\n"
        "- быстрый рост от новичка до опытного сотрудника (от 39 000 до 45 000 руб.);\n"
        "- оплачиваем мед.книжки;\n"
        "- премия за акцию «Приведи друга» 20 000 руб.\n"
        f"{candidate_name}, Вы готовы к обучению?"
    )
    await message.answer(text, reply_markup=build_yes_no_menu())

# Training question response
@router.callback_query(lambda c: c.data in ["yes", "no"], DialogStates.training_question)
async def process_training_question(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "yes":
        await state.set_state(DialogStates.interest_check)
        text = (
            "На каждый разряд есть наставник, простая система обучения, молодой и дружный коллектив.\n"
            "Вам интересна компания и условия?"
        )
        await callback.message.reply(text, reply_markup=build_yes_no_menu())
    else:
        await callback.message.reply("Поняла. Спасибо за уделенное время. До свидания!")
        user_data = await state.get_data()
        data = {
            "id": callback.from_user.id,
            "name": user_data.get("candidate_name", "Кандидат"),
            "vacancy": "Оператор линии",
            "status": "Отказ",
            "stage": "Вопрос об обучении",
            "reason": "Не готов к обучению",
            "date": "2023-10-01"
        }
        save_candidate_data(data)
        await state.clear()
    await callback.answer()

@router.callback_query(lambda c: c.data in ["yes", "no"], DialogStates.interest_check)
async def process_interest_check(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "yes":
        await state.set_state(DialogStates.interview_invitation)

        text = (
            "Хорошо! Мы находимся по адресу: ул. Радиозаводское шоссе 23.\n"
            "Удобно ли Вам подойти завтра или послезавтра?"
        )
        await callback.message.reply(text, reply_markup=build_yes_no_menu())
    else:
        await callback.message.reply("Поняла. Спасибо за уделенное время. До свидания!")
        user_data = await state.get_data()
        data = {
            "id": callback.from_user.id,
            "name": user_data.get("candidate_name", "Кандидат"),
            "vacancy": "Оператор линии",
            "status": "Отказ",
            "stage": "Проверка интереса",
            "reason": "Не заинтересован",
            "date": "2023-10-01"
        }
        save_candidate_data(data)
        await state.clear()
    await callback.answer()

# Interview invitation response
@router.callback_query(lambda c: c.data in ["yes", "no"], DialogStates.interview_invitation)
async def process_interview_invitation(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "yes":
        await state.set_state(DialogStates.whatsapp_check)
        text = (
            "У вас есть на этом номере WhatsApp?\n"
            "Я вышлю приглашение с адресом и датой встречи."
        )
        await callback.message.reply(text, reply_markup=build_yes_no_menu())
    else:
        await callback.message.reply("Поняла, желаю хорошего дня, до свидания!")
        user_data = await state.get_data()
        data = {
            "id": callback.from_user.id,
            "name": user_data.get("candidate_name", "Кандидат"),
            "vacancy": "Оператор линии",
            "status": "Отказ",
            "stage": "Приглашение",
            "reason": "Не может подойти",
            "date": "2023-10-01"
        }
        save_candidate_data(data)
        await state.clear()
    await callback.answer()

@router.callback_query(lambda c: c.data in ["yes", "no"], DialogStates.whatsapp_check)
async def process_whatsapp_check(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    data = {
        "id": callback.from_user.id,
        "name": user_data.get("candidate_name", "Кандидат"),
        "vacancy": "Оператор линии",
        "status": "Приглашен на собеседование",
        "stage": "Телефонное интервью",
        "reason": None,
        "date": "2023-10-01",
        "priorities": user_data.get("candidate_priorities", "")
    }
    save_candidate_data(data)
    await callback.message.reply(
        callback.from_user.id,
        "Хорошо! Я вышлю приглашение через WhatsApp. Спасибо за уделенное время, до встречи!"
    )
    await state.clear()
    await callback.answer()

@router.message(Command("вакансии"))
async def vacancies(message: types.Message):
    await message.answer("Ищем активные вакансии компании на hh.ru... ⏳")
    async with aiohttp.ClientSession() as session:
        try:
            items = await fetch_vacancies(session, config("EMPLOYER_ID"))
        except Exception as e:
            print(e)
            await message.answer("Не удалось получить вакансии. Попробуйте позже.")
            return
    if not items:
        await message.answer("Сейчас нет активных вакансий.")
        return
    texts = []
    for vac in items:
        title = vac.get('name')
        url = vac.get('alternate_url')
        salary = vac.get('salary')
        salary_str = (
            f"{salary.get('from', '')}–{salary.get('to', '')} {salary.get('currency', '')}".strip('– ')
            if salary else "не указана"
        )
        texts.append(f"• <a href=\"{url}\">{title}</a> — {salary_str}")
    reply = "\n".join(texts)
    await message.answer(reply, parse_mode="HTML")

@router.message(Command("candidates"))
async def list_candidates(message: types.Message):
    if message.from_user.id not in HR_IDS:
        await message.answer("Эта команда доступна только HR.")
        return
    if not os.path.exists('candidates.json'):
        await message.answer("Нет данных о кандидатах.")
        return
    with open('candidates.json', 'r', encoding='utf-8') as f:
        candidates = json.load(f)
    kb = InlineKeyboardBuilder()
    for candidate in candidates:
        kb.button(text=f"{candidate['name']} ({candidate['status']})", callback_data=f"candidate_{candidate['id']}")
    await message.answer("Список кандидатов:", reply_markup=kb.as_markup())

# HR: Select candidate
@router.callback_query(lambda c: c.data.startswith("candidate_"))
async def process_candidate_selection(callback: types.CallbackQuery):
    if callback.from_user.id not in HR_IDS:
        await callback.answer("Доступно только HR.")
        return
    candidate_id = int(callback.data.split("_")[1])
    kb = InlineKeyboardBuilder()
    statuses = ["Недоступен", "Телефонное интервью", "Подумать после интервью", "Интервью HR", "Отказ"]
    for status in statuses:
        kb.row(types.InlineKeyboardButton(text=status, callback_data=f"status_{candidate_id}_{status}"))
    await callback.message.reply("Выберите статус:", reply_markup=kb.as_markup())
    await callback.answer()

# HR: Set status
@router.callback_query(lambda c: c.data.startswith("status_"))
async def process_status_selection(callback: types.CallbackQuery):
    if callback.from_user.id not in HR_IDS:
        await callback.answer("Доступно только HR.")
        return
    parts = callback.data.split("_")
    candidate_id, status = int(parts[1]), "_".join(parts[2:])
    with open('candidates.json', 'r', encoding='utf-8') as f:
        candidates = json.load(f)
    for candidate in candidates:
        if candidate['id'] == candidate_id:
            candidate['status'] = status
            if status == "Отказ":
                kb = InlineKeyboardBuilder()
                reasons = ["Не соответствует требованиям", "Не прошел собеседование", "Не устраивает зарплата"]
                for reason in reasons:
                    kb.button(text=reason, callback_data=f"reason_{candidate_id}_{reason}")
                await callback.message.answer("Укажите причину отказа:", reply_markup=kb.as_markup())
            break
    with open('candidates.json', 'w', encoding='utf-8') as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)
    await callback.message.answer(f"Статус обновлен: {status}")
    await callback.answer()

# HR: Set refusal reason
@router.callback_query(lambda c: c.data.startswith("reason_"))
async def process_reason_selection(callback: types.CallbackQuery):
    if callback.from_user.id not in HR_IDS:
        await callback.answer("Доступно только HR.")
        return
    parts = callback.data.split("_")
    candidate_id, reason = int(parts[1]), "_".join(parts[2:])
    with open('candidates.json', 'r', encoding='utf-8') as f:
        candidates = json.load(f)
    for candidate in candidates:
        if candidate['id'] == candidate_id:
            candidate['reason'] = reason
            break
    with open('candidates.json', 'w', encoding='utf-8') as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)
    await callback.message.answer(f"Причина отказа обновлена: {reason}")
    await callback.answer()
