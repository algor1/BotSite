from telegrambot.models import Update,Message
from telebot.models import History
import json

def save_history(update_id,message):
    update=Update.objects.get(pk=update_id)
    history=History(update=update,message=message)
    history.save()

def get_last_command(update_id):
    last_command={}
    update=Update.objects.get(pk=update_id)
    chat1=update.message.chat
    for m in Message.objects.filter(chat=chat1).order_by('-message_id'):
        if m.text[0]=='/':
            last_command['command']=m.text[1:]
            last_command['num']=0
            for i in History.objects.filter(update__message__chat=chat1).order_by('update__update_id'):
                last_command=json.loads(i.message)
            break


    #lcommand['command']+"_"+last_command['num']
    return last_command

def end_command(update,command):
    return None

def answer(update):
    return None

def last_answer(update):
    history=History.object.get(update=update)
    return history.message

