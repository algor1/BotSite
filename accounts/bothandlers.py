urlpatterns = [command('start', StartView.as_command_view()),
           command('author', AuthorCommandView.as_command_view()),
           command('author_inverse', AuthorInverseListView.as_command_view()),
           command('author_query', login_required(AuthorCommandQueryView.as_command_view())),
           unknown_command(UnknownView.as_command_view()),
           regex(r'author_(?P<name>\w+)', AuthorName.as_command_view()),
          ]