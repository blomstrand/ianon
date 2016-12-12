from django.db import models

# Create your models here.
class Document(models.Model):
	def __str__(self):
		return self.filename
	filename = models.CharField(max_length=150)
	last_modified = models.DateTimeField(auto_now=True)
	uploaded = models.DateTimeField(auto_now_add=True)

class Word(models.Model):
	def __str__(self):
		return self.word_text
	word_text = models.CharField(max_length=100)
	named_entity = models.CharField(max_length=20)
	s_id = models.IntegerField()
	document = models.ForeignKey(Document, on_delete=models.CASCADE)