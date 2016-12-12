from django.shortcuts import render, get_object_or_404

from django.template import RequestContext
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.files.base import ContentFile
from ianer.models import Document, Word
from ianer.forms import DocumentForm
from ianer.processer import tagText, handleFile
# Create your views here.

def texts(request):
	"""POST handels delete or export, GET presents available texts"""
	if request.method == 'POST':
		if 'export' in request.POST:
			selected_texts = request.POST.getlist('check[]')
			if len(selected_texts) < 2:
			
				doc_id = selected_texts[0]
				document = get_object_or_404(Document, pk=doc_id)
				words = document.word_set.all()
				s_count = 0
				content = ""
				for word in words:
					if s_count < word.s_id:
						content += "\n"
						s_count = word.s_id
					content += word.word_text + " "
				
				filename = document.filename
				response = HttpResponse(content, content_type="text/plain")
				response['Content-Disposition'] = 'attachment; filename=%s' % filename
				
				return response
			
			else:
				return HttpResponseRedirect(reverse('texts'))
				
		elif 'delete' in request.POST:
			selected_texts = request.POST.getlist('check[]')
			for text_id in selected_texts:
				text = get_object_or_404(Document, pk=text_id)
				text.delete()
			return HttpResponseRedirect(reverse('texts'))
	else:
		documents = Document.objects.all()
		return render(request,
				'ianer/texts.html',
				{'documents': documents}
		)

def upload(request):
	"""POST handles file upload, GET presents empty form"""
	if request.method == 'POST':
		if 'upload_b' in request.POST:
			new_doc = Document(filename = request.POST['filename'])
			new_doc.save()
			content = handleFile(request.FILES['docfile'])
			sent_list = tagText(content)
			header = new_doc.filename
			s_count = 0
			w_count = 0
			word_list = []
			for sentence in sent_list:
				for word in sentence:
					a = Word(word_text=word[0], 
							named_entity=word[1], 
							s_id=s_count, 
							document=new_doc 
							)
					word_list.append(a)
				s_count += 1
			Word.objects.bulk_create(word_list)
			words = new_doc.word_set.all()
			doc_id = new_doc.id
			return HttpResponseRedirect(reverse('edit', args=(doc_id,)))
	else:
		return render(request,
				'ianer/upload.html', {}
		)
	
def edit(request, doc_id):
	"""POST handles text-edits or export, GET presents words in text"""
	if request.method == 'POST':
		#handle edit form requests
		if 'edit_b' in request.POST:
			word_id = request.POST['id']
			marked_word = get_object_or_404(Word, pk=word_id)
			name_list = ["B-PRS", "I-PRS"]
			loc_list = ["B-LOC", "I-LOC"]
			org_list = ["B-ORG", "I-ORG"]
			other = "O"
			selected_ne = request.POST['NE']
			edit_word = request.POST['ord']
			
			#change the marked words attributes depending on options form. 
			if (marked_word.named_entity not in loc_list) and selected_ne == 'loc':
				marked_word.named_entity = "B-LOC"
				marked_word.save(update_fields=['named_entity'])
			elif (marked_word.named_entity not in name_list) and selected_ne == 'name':
				marked_word.named_entity = "B-PRS"
				marked_word.save(update_fields=['named_entity'])
			elif (marked_word.named_entity not in org_list) and selected_ne == 'org':
				marked_word.named_entity = "B-ORG"
				marked_word.save(update_fields=['named_entity'])
			elif (marked_word.named_entity != other) and selected_ne == 'other':
				marked_word.named_entity = other
				marked_word.save(update_fields=['named_entity'])
			elif marked_word.word_text != edit_word:
				marked_word.word_text = edit_word
				marked_word.save(update_fields=['word_text'])
			
			doc = Document.objects.get(pk=doc_id)
			doc.save()
			return HttpResponseRedirect(reverse('edit', args=(doc_id,)))
		
		if 'export_b' in request.POST:
			doc_id = request.POST['id']
			document = get_object_or_404(Document, pk=doc_id)
			words = document.word_set.all()
			s_count = 0
			content = ""
			for word in words:
				if s_count < word.s_id:
					content += "\n"
					s_count = word.s_id
				content += word.word_text + " "
			
			filename = document.filename
			response = HttpResponse(content, content_type="text/plain")
			response['Content-Disposition'] = 'attachment; filename=%s' % filename
			
			return response
	else:
		doc = get_object_or_404(Document, pk=doc_id)
		words = doc.word_set.all()
		header = doc.filename
		return render(request,
			'ianer/edit.html',
			{'header': header, 'words': words ,'doc_id': doc_id}
		)

def mainPage(request):
	
	return render(request,
		'ianer/main.html')


