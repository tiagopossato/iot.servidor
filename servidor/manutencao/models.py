from django.db import models

class Log(models.Model):
    tipo = models.CharField(max_length=6)
    mensagem = models.CharField(max_length=255)
    sync = models.BooleanField(default=False)
    tempo = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.mensagem

    class Meta:
        verbose_name = 'Log'
        verbose_name_plural = 'Logs'