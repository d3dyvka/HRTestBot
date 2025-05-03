import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from decouple import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

bot = Bot(token=config('BOT_TOKEN'))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class DialogStates(StatesGroup):
    waiting_for_name = State()
    greeting = State()
    company_presentation = State()
    candidate_questions = State()
    training_question = State()
    interest_check = State()
    interview_invitation = State()
    whatsapp_check = State()