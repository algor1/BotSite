from django.db import models

# Create your models here.

class History(models.Model):
    update = models.ForeignKey('telegrambot.Update', on_delete=models.CASCADE)
    message = models.CharField(max_length=200, blank=True)

#    def __str__(self):
#        return self.update.message.user.first_name + ' / ' + self.update.id

