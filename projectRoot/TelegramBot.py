import logging
import os
import ChatbotController as cc
import Constants as con
import dto.User as user
import service.domain.UserDataService as us
from telegram.constants import ChatAction
from telegram import *
from telegram.ext import *
from dotenv import load_dotenv, find_dotenv
from functools import wraps
import service.domain.FoodHistoryService as foodHistory
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import service.asyncr.ComputeMonthlyUserTasteService as cmu
import asyncio

load_dotenv(find_dotenv())
token = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

userData = ''
userMessage = ''
MULTIPLE_MESSAGES = True

#chatbot states
INTERACTION = range(1)

def update_context(context: ContextTypes.DEFAULT_TYPE, response):
        context.user_data['action'] = response.action
        context.user_data['memory'] = response.memory
        context.user_data['info'] = response.info
        context.user_data['callbackMessage'] = response.modifiedPrompt
        return context

def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        async def command_func(update, context, *args, **kwargs):
            await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return await func(update, context,  *args, **kwargs)
        return command_func
    
    return decorator

@send_action(ChatAction.TYPING)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation."""
    telegramUser = update.message.from_user
    context.user_data['info'] = ''
    context.user_data['userData'] =  us.getUserData(telegramUser['id'])

    #if the user data is empty the start a "get data", conversation
    if(context.user_data['userData'] == None):
        context.user_data['userData'] = user.User(telegramUser['username'],telegramUser['id'],None,None,None,None,None,None,None,None,None)
        response = cc.answer_question(context.user_data['userData'],con.USER_FIRST_MEETING_PHRASE,con.TASK_0_HOOK,None,"")
        await context.bot.sendMessage(chat_id=update.message.chat_id, text=response.answer)
        context = update_context(context,response)
    else:
        response = cc.answer_router(context.user_data['userData'],con.USER_GREETINGS_PHRASE,con.TASK_1_HOOK,"",None)
        foodHistory.clean_temporary_declined_suggestions(context.user_data['userData'].id)
        await context.bot.sendMessage(chat_id=update.message.chat_id, text=response.answer)
        context = update_context(context,response)
    return INTERACTION

@send_action(ChatAction.TYPING)
async def interaction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Manage the conversation loop between the user and the chatbot."""
    userMessage = context.user_data['callbackMessage'] if len(context.user_data['callbackMessage'])>0 else update.message.text
    response = cc.answer_router(context.user_data['userData'],userMessage,context.user_data['action'],context.user_data['memory'],context.user_data['info'])
    await context.bot.sendMessage(chat_id=update.message.chat_id, text=response.answer)
    context = update_context(context,response)

    #this means that the bot has to ask the user something else
    if len(context.user_data['callbackMessage'])>0 and MULTIPLE_MESSAGES:
        #await asyncio.sleep(2)
        return await interaction(update, context)
    
    #this means that the bot is in the memory reset state, so we can send a new message
    if context.user_data['action'] == "TASK -1" and MULTIPLE_MESSAGES:
        context.user_data['callbackMessage'] = con.USER_GREETINGS_PHRASE
        #await asyncio.sleep(2)
        return await interaction(update, context)
    
    return None

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text('Bye! Hope to talk to you again soon.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def send_reminder(context: CallbackContext):
    """Send a reminder to users who have reminders enabled and haven't interacted recently."""
    users = us.get_all_users_with_reminder()
    for user in users:
        last_interaction = datetime.strptime(user['lastInteraction'], '%Y-%m-%d %H:%M:%S').date()
        if datetime.now().date() - last_interaction >= timedelta(days=2):
            await context.bot.send_message(chat_id=user['id'], text="Hey! It's been a while since we last talked. How about a chat to keep up with your sustainable habits and discover new recipe? Just write me something and I'll be here for you!")

async def compute_monthly_user_taste():
    """Compute the user's taste for each meal type at the end of the month."""
    cmu.compute_monthly_user_taste()

def main() -> None:
    """Run the bot."""
    application = Application.builder().token(token).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            INTERACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, interaction)]},
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    # Handle the case when a user sends /start but they're not in a conversation
    application.add_handler(CommandHandler('start', start))

    # Set up the scheduler
    scheduler = BackgroundScheduler()

    #reminder scheduled to be sent every day at 12:00 if the user hasn't interacted in the last 2 days
    scheduler.add_job(lambda: asyncio.run(send_reminder(application)), 'cron', hour=12, minute=00)
    #compute the user's taste at the start of the month based on the previous month's data
    scheduler.add_job(lambda: asyncio.run(compute_monthly_user_taste()), 'cron', day=1, hour=0, minute=0)
    scheduler.start()

    application.run_polling()

if __name__ == '__main__':
    main()