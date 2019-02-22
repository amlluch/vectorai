from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

# Create your models here.


class Country(models.Model):

    name = models.CharField(_("Name"), db_column='name', max_length = 150, null=True, blank=True)
    code2 = models.CharField(_("Code2"), db_column='code2', max_length = 2, unique = True)
    code3 = models.CharField(_("Code3"), db_column='code3', max_length = 3, unique = True)
    number = models.CharField(_("Number"), db_column='number', max_length = 3, unique = True)
       

class Document(models.Model):

    image = models.ImageField(_("Document image"), upload_to=settings.UPLOAD_TO, null=True, blank=True)
