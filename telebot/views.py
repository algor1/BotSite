# Create your views here.
from telegrambot.bot_views.generic import TemplateCommandView
from telegrambot.bot_views.generic.list import ListCommandView
from telegrambot.bot_views.generic.responses import TextResponse, KeyboardResponse
from telegram import ParseMode
from accounts.models import BotTheme
from telebot.models import History
from telebot.utils import save_history, get_last_command
import logging
import sys
import traceback
import json

logger = logging.getLogger(__name__)
PY3 = sys.version_info > (3,)


class StartView(TemplateCommandView):
    template_text = "telebot/messages/command_start_text.txt"

class BotThemeListView(ListCommandView):
    template_text = "telebot/messages/command_bot_themes_list_text.txt"
#    template_keyboard = "telebot/messages/command_bot_theme_list_keyboard.txt"
    model = BotTheme
    context_object_name = "BotTheme"

class UnknownView(TemplateCommandView):
    template_text = "telebot/messages/command_start_text.txt"

class UnknownMessage(TemplateCommandView):
    template_text = "telebot/messages/message_unknown_text.txt"
    context={}
    tmp_text=''
    def get_context(self, bot, update, **kwargs):
        self.context['update']= update
        return self.context
    def get_template_text(self, bot, update, **kwargs):
        last_command=get_last_command(update_id=int(update.update_id))
        if last_command:

            self.template_text="telebot/messages/command_"+last_command['command']+"_"+str(last_command['num']+1)+"_text.txt"
            self.tmp_text=last_command
        return self.tmp_text
    def handle(self, bot, update, **kwargs):
        try:
            last_com=self.get_template_text(bot, update, **kwargs)
            last_com['num']+=1
            ctx = self.get_context(bot, update, **kwargs)
            text = TextResponse(self.template_text, ctx).render()
            keyboard = KeyboardResponse(self.template_keyboard, ctx).render()
#             logger.debug("Text:" + str(text.encode('utf-8')))
#             logger.debug("Keyboard:" + str(keyboard))
            if text:
                if not PY3:
                    text = text.encode('utf-8')
                bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
                save_history(update_id=int(update.update_id),message= json.dumps(last_com))

            else:
                logger.info("No text response for update %s" % str(update))
        except:
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
            raise


def message_recieved(**kwargs):
    mess=UnknownMessage()
    message_view=mess.as_command_view(**kwargs)
    mess.context['next_question']='wats up!'
#    message_update=mess.context['update']


#    logger.info(str(message_update.message.text))
    return message_view