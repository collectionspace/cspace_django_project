from django.db import models
from positions.fields import PositionField

class AdditionalInfo(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    order = PositionField()
    contentType = models.CharField(max_length=4, choices=(('HTML', 'HTML'), ('TEXT', 'Plain Text')), default='HTML')
    live = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['order']
    
    def __unicode__(self):
        return self.name