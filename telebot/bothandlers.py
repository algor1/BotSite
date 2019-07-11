from telegrambot.bot_views.decorators import login_required
from telegrambot.handlers import command,unknown_command,message

from telebot.views import StartView,BotThemeListView,UnknownView,UnknownMessage,message_recieved

urlpatterns = [command('start', StartView.as_command_view()),
               command('bot_theme', BotThemeListView.as_command_view()),
#               command('author_query', login_required(AuthorCommandQueryView.as_command_view())),
               unknown_command(UnknownView.as_command_view()),
               message(message_recieved()),
               ]
