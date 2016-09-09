from django.core import validators
from django.db import models


class CollaboratoryContext(models.Model):
    """A generic HBP Software"""
    software_name_validator = validators.RegexValidator(r'^[0-9a-zA-Z_-]*$')

    ctx = models.UUIDField(unique=True)
    access_key = models.CharField(max_length=20, unique=True)
    secret_key = models.CharField(max_length=40, unique=True)
    uuid = models.CharField(max_length=40, unique=True)

    class Meta(object):
        '''meta'''
        ordering = ['ctx']

    # UUIDField is not supported by automatic JSON serializer
    # so we add a method that retrieve a more convenient dict.
    def as_json(self):
        return {
            'access_key': self.access_key,
            'secret_key': self.secret_key,
            'uuid': self.uuid,
            'ctx': str(self.ctx),
        }

    def __unicode__(self):
        return str.format("{0}({1},{2},{3})", self.ctx, + self.access_key, + self.secret_key, + self.uuid)

    @models.permalink
    def get_absolute_url(self):
        return reverse('clbctx_show', args=[str(self.ctx)])
