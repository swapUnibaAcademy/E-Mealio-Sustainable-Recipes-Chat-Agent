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
import service.bot.LangChainService as lcs

#---------------------------------------------------------
## PER SALVARE L'OUTPUT SUL FILE TXT

import sys

log_file = open("output.txt", "w", encoding="utf-8")
sys.stdout = log_file
sys.stderr = log_file

#---------------------------------------------------------

load_dotenv(find_dotenv())

token = os.getenv("TELEGRAM_BOT_TOKEN")
"""Token del bot telegram."""


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
"""Logger per tenere traccia delle attività del bot."""


userData = ''

"""
L'oggetto user_data  definito all'interno del contesto del bot telegram (context: ContextTypes.DEFAULT_TYPE),  viene usato
per monitorare il flusso conversazionale e i dati utente, e contiene le seguenti informazioni:

    - userData: contiene i dati utente come definiti nella classe DTO. L'oggetto viene recuperato dal database all'inizio di una conversazione
                oppure viene creato durante la prima interazione e quindi archiviato. Questi dati vengono passati avanti e indietro al controller e utilizzati da quest'ultimo quando necessario.

    - action: contiene il token successivo che rappresenta l'azione che deve essere invocata. Questo valore viene restituito dal controller dell'agente.

    - memory: per alcune funzionalità, è abilitata la possibilità di tenere traccia di una parte della conversazione.

    - info: simile alla memoria, questo campo archivia le informazioni utilizzate dal controller per fornire al livello LLM i dettagli estratti.

    - callbackMessage: se popolato dall'agente controller, questo campo contiene un messaggio utente fittizio che viene immediatamente ritrasmesso al controller. Ciò consente di 
                       generare due risposte in determinati casi, ad esempio quando un'interazione si sta chiudendo e l'hub deve essere nuovamente presentato.
"""

userMessage = ''
MULTIPLE_MESSAGES = True

#chatbot states
INTERACTION = range(1)
"""Stato responsabile della gestione della conversazione continua tra l'utente e l'agente."""

MENU_LABELS = {
    "it": {
        "recipe_recommendation": "Suggerimento Ricetta",
        "recipe_improvement": "Miglioramento Ricetta",
        "food_expert": "Esperto Alimentare",
        "profile": "Profilo Utente",
        "diary": "Diario Alimentare",
        "diary_recap": "Riepilogo Diario"
    },
    "en": {
        "recipe_recommendation": "Recipe Recommendation",
        "recipe_improvement": "Recipe Improvement",
        "food_expert": "Food Expert",
        "profile": "User Profile Recap and Update",
        "diary": "Food Diary",
        "diary_recap": "Food Diary Recap"
    }
}

def build_menu_buttons(language: str = "en"):
    labels = MENU_LABELS.get(language, MENU_LABELS["en"])  # recupera in inglese se la lingua non è ancora supportata

    return [
        [InlineKeyboardButton("🍽️ " + labels["recipe_recommendation"], callback_data="Recipe Recommendation")],
        [InlineKeyboardButton("🛠️ " + labels["recipe_improvement"], callback_data="Recipe Improvement")],
        [InlineKeyboardButton("🌱 " + labels["food_expert"], callback_data="Food Expert")],
        [InlineKeyboardButton("👤 " + labels["profile"], callback_data="User Profile Recap and Update")],
        [InlineKeyboardButton("🥘 " + labels["diary"], callback_data="Food Diary")],
        [InlineKeyboardButton("📊 " + labels["diary_recap"], callback_data="Food Diary Recap")],
        
    ]

def update_context(context: ContextTypes.DEFAULT_TYPE, response):
    """
    Aggiorna lo stato interno dell'utente in base alla risposta ricevuta dal modello.

    Args : 
    - context (ContextTypes.DEFAULT_TYPE) : il contesto corrente di Telegram, che contiene i dati utente
    - response : oggetto istanza della classe Response che contiene la risposta ricevuta dal prompt inviato al modello.
    
    Returns : 
    - ContextTypes.DEFAULT_TYPE: The updated context with modified user_data.
    """
    context.user_data['action'] = response.action
    context.user_data['memory'] = response.memory
    context.user_data['info'] = response.info
    context.user_data['callbackMessage'] = response.modifiedPrompt
    return context

def send_action(action):
    """
    Decoratore personalizzato per far si che il bot mostri un'azione in corso prima di eseguire una funzione asincrona
    Args : 
    - action (telegram.constants.ChatAction) : azione da mostrare (ad esempio ChatAction.TYPING mostra "sta scrivendo...")

    Returns :
    - Callable : decoratore che wrappa la funzione di gestione asincrona per inviare l'azione di chat specificata prima della sua esecuzione.
    """
    def decorator(func):
        """
        Decoratore effettivo che wrappa la funzione specificata.
        
        Args : 
        - func : funzione da wrappare.
        
        Returns : 
        - Callable : la funzione asincrona wrappata."""

        @wraps(func)
        async def command_func(update, context, *args, **kwargs):
            """
            Invia l'azione che il bot sta compiendo alla chat dell'utente prima di eseguire la funzione wrappata.

            Args : 
            - update (telegram.Update) : aggiornamento telegram ricevuto
            - context (telegram.ext.ContextTypes.DEFAULT_TYPE) : contesto di callback

            Returns : 
            - restituisce l'output effettivo della funzione wrappata.
            """
            # solo per i messaggi di testo
            #await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            #return await func(update, context,  *args, **kwargs)

            # per gestire anche i callback
            if update.message:
                chat_id = update.message.chat_id
            elif update.callback_query:
                chat_id = update.callback_query.message.chat_id
            else:
                chat_id = update.effective_user.id  # fallback

            await context.bot.send_chat_action(chat_id=chat_id, action=action)
            return await func(update, context,  *args, **kwargs)
        return command_func
    
    return decorator

@send_action(ChatAction.TYPING)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Inizia la conversazione (l'utente ha inviato il comando /start).
    """

    # estraimo l'utente che ha inviato il comando interagendo con il bot
    telegramUser = update.message.from_user

    user_language = telegramUser.language_code

    # e salviamo le informazioni nel contesto corrente
    context.user_data['info'] = ''
    context.user_data['userData'] =  us.getUserData(telegramUser['id']) # recupera dal db l'utente con dato id

    # se l'utente non è presente nel db, iniziamo una conversazione "get data" per ricavare le sue informazioni
    if(context.user_data['userData'] == None):

        # creiamo un nuovo utente
        context.user_data['userData'] = user.User(telegramUser['username'],telegramUser['id'],None,None,None,None,user_language,None,None,None,None,None,None,None,None,None)
        
        # l'utente ha inviato il comando /start ed è prima volta che interagisce con il chatbot,
        # per questo come messaggio da inviare al chatbot usiamo USER_FIRST_MEETING_PHRASE = "Hi! It's the first time we met."
        # con TASK_0_HOOK che indica di chiedere all'utente i dati personali.
        response = cc.answer_question(context.user_data['userData'], con.USER_FIRST_MEETING_PHRASE,con.TASK_0_0_HOOK,None,"")
        
        print("\n++++++++++++++++++++++++++++++++++++++++++++++++++")
        print("Invio messaggio all'utente : \n",response.answer)
        print("+++++++++++++++++++++++++++++++++++++++++++++++\n")

        await context.bot.sendMessage(chat_id=update.message.chat_id, text=response.answer)
        
        # aggiorniamo il contesto corrente
        context = update_context(context,response)
    else:

        # l'utente ha inviato il comando /start ma ha già interagito precedentemente con il chatbot, 
        # per questo come messaggio da inviare al chatbot usiamo USER_GREETINGS_PHRASE = "Hi!"
        # con TASK_1_HOOK che indica il messaggio di benvenuto.
        response = cc.answer_router(context.user_data['userData'],con.USER_GREETINGS_PHRASE,con.TASK_1_HOOK,"",None)
        foodHistory.clean_temporary_declined_suggestions(context.user_data['userData'].id)

        print("\n++++++++++++++++++++++++++++++++++++++++++++++++++")
        print("Invio messaggio all'utente : \n",response.answer)
        print("+++++++++++++++++++++++++++++++++++++++++++++++\n")

        tastiera_markup = InlineKeyboardMarkup(build_menu_buttons(context.user_data['userData'].language))

        #await context.bot.sendMessage(chat_id=update.message.chat_id, text=response.answer)
        await update.message.reply_text(response.answer, reply_markup=tastiera_markup)
        
        context = update_context(context,response)
        ####################

    return INTERACTION

@send_action(ChatAction.TYPING)
async def interaction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("\n\n===================================================================================")
    print("context.user_data['callbackMessage'] : ", context.user_data['callbackMessage'])
    print("update.message.text : ", update.message.text)


    userMessage = context.user_data['callbackMessage'] if len(context.user_data['callbackMessage']) > 0 else update.message.text
    context.user_data['callbackMessage'] = ""  

    response = cc.answer_router(
        context.user_data['userData'],
        userMessage,
        context.user_data['action'],
        context.user_data['memory'],
        context.user_data['info']
    )

    print("\n++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("Invio messaggio all'utente : \n", response.answer)
    print("+++++++++++++++++++++++++++++++++++++++++++++++\n")

    # LOGICA PER MENU AL SECONDO MESSAGGIO TASK_1_HOOK O TASK_MINUS_1_HOOK
    if response.action == con.TASK_1_HOOK or response.action == con.TASK_MINUS_1_HOOK:
        if context.user_data.get('menu_ready', False):
            # secondo messaggio: mostra il menu
            
            tastiera_markup = InlineKeyboardMarkup(build_menu_buttons(context.user_data['userData'].language))
            await update.message.reply_text(response.answer, reply_markup=tastiera_markup)
            context.user_data['menu_ready'] = False  
        else:
            # primo messaggio TASK_1_HOOK: non mostrare menu, ma imposta flag
            await context.bot.sendMessage(chat_id=update.message.chat_id, text=response.answer)
            context.user_data['menu_ready'] = True
    else:
        await context.bot.sendMessage(chat_id=update.message.chat_id, text=response.answer)
        # reset se cambia token
        context.user_data['menu_ready'] = False  

    context = update_context(context, response)
    
    # gestione ricorsiva
    if len(context.user_data['callbackMessage']) > 0 and MULTIPLE_MESSAGES:
        return await interaction(update, context)
    if context.user_data['action'] == "TOKEN -1" and MULTIPLE_MESSAGES:
        context.user_data['callbackMessage'] = con.USER_GREETINGS_PHRASE
        return await interaction(update, context)

    return None

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancella e termina la conversazione."""
    await update.message.reply_text('Bye! Hope to talk to you again soon.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def schedule_user_reminder(scheduler, bot, user):
    
    async def personalized_reminder():
        last_interaction = datetime.strptime(user['lastInteraction'], '%Y-%m-%d %H:%M:%S').date()
        if datetime.now().date() - last_interaction >= timedelta(days=us.get_num_days_reminder(user['id'])):
            # traduciamo il messaggio da inviare in base alla lingua dell'utente
            await bot.send_message(chat_id=user['id'], text=lcs.translate_text(con.REMINDER,user['language']))

    # Rimuove job esistenti con lo stesso ID (per evitare duplicati)
    job_id = f"user_reminder_{user['id']}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)

    # Programma il job personalizzato
    scheduler.add_job(
        lambda: asyncio.run(personalized_reminder()),
        trigger='cron',
        hour=us.get_hour_reminder(user['id']),
        minute=0,
        id=job_id,
        replace_existing=True
    )

async def compute_monthly_user_taste():
    """Calcola il profilo di gusto degli utenti per ogni tipologia di pasto alla fine del mese."""
    cmu.compute_monthly_user_taste()

@send_action(ChatAction.TYPING)
async def callback(update: Update, context: CallbackContext) -> None:
    
    opzione = update.callback_query.data
    response = cc.answer_router(context.user_data['userData'],con.USER_BUTTON_CLICK.format(functionality=opzione),context.user_data['action'],context.user_data['memory'],context.user_data['info'])
    
    print("\n++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("Invio messaggio all'utente : \n",response.answer)
    print("+++++++++++++++++++++++++++++++++++++++++++++++\n")
    
    await update.effective_user.send_message(response.answer)
    
    context = update_context(context,response)

    # ELIMINA IL MESSAGGIO CON I BOTTONI
    #await update.callback_query.message.delete()

    # ELIMINA SOLO I BOTTONI E LASCIA IL MESSAGGIO DEL MENU
    await update.callback_query.message.edit_reply_markup(reply_markup=None)


def main() -> None:
    """Avvia il bot telegram."""

    application = Application.builder().token(token).build()
    
    # definiamo il gestore delle conversazioni ConversationHandler(entry_points, states, fallbacks) :
    # - entry_points rappresenta il punto di inizio della conversazione
    # - states è il dizionario degli stati della conversazione
    # - fallbacks sono i comandi che interrompono la conversazione.

    # il gestore dei comandi CommandHandler("comando", callbackfunction) gestisce l'arrivo di un comando da parte dell'utente : 
    # quando il bot riceve dall'utente il comando \comando esegue la funzione callbackfunction.

    # il gestore dei messaggi MessageHandler(filters, callbackfunction) gestisce l'arrivo di messaggi di testo da parte dell'utente :
    # quando il bot riceve un messaggio di testo (filters.TEXT) e non di comando (~filters.COMMAND) eseguie la funzione callbackfunction.

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],  
        states={
            INTERACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, interaction)]},
        fallbacks=[CommandHandler('cancel', cancel)],  
    )

    # aggiunge il ConversationHandler all'applicazione, così che il bot sappia gestire la conversazione
    application.add_handler(conv_handler)

    # Handle the case when a user sends /start but they're not in a conversation
    application.add_handler(CommandHandler('start', start))

    # Handle callback of the menu buttons
    application.add_handler(CallbackQueryHandler(callback))

    # configuriamo lo scheduler (che verrà eseguito in background su un thread separato)
    scheduler = BackgroundScheduler()

    #reminder scheduled to be sent every day at 12:00 if the user hasn't interacted in the last 2 days
    # VERSIONE NUOVA : PERSONALIZZATO IN BASE ALL'UTENTE
    users = us.get_all_users_with_reminder()
    for user in users:
        schedule_user_reminder(scheduler, application.bot, user)

    #compute the user's taste at the start of the month based on the previous month's data
    scheduler.add_job(lambda: asyncio.run(compute_monthly_user_taste()), 'cron', day=1, hour=0, minute=0)

    scheduler.start()

    application.run_polling()

    
if __name__ == '__main__':
    main()

