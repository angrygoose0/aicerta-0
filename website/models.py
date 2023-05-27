from django.db import models

# Create your models here.
class Emails(models.Model):
    from_email = models.TextField()
    subject = models.TextField()
    message = models.TextField()

    def __str__(self):
        return "%s, %s, %s" % (self.from_email, self.subject, self.message)