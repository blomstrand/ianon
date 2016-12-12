import codecs
from ianer.POStagger import POSPerceptronTagger
from ianer.NERtagger import NERPerceptronTagger
import xml.etree.ElementTree as ET

def tagText(text):
	post = POSPerceptronTagger(True)
	nert = NERPerceptronTagger(True)

	#root = ET.Element("text")
	
	sentences = []
	for sentence in tokenizeFromFile(text):
		words = []
		p_sent = post.tagSentence(sentence)
		ne_sent = nert.tagSentence(p_sent)
		#xml_sent = ET.SubElement(self.xml_text.root, "sentence")
		for trio in ne_sent:
			words.append((trio[0], trio[2]))
			#xml_word = ET.SubElement(xml_sent, 'w')
			#xml_word.text = trio[0]
			#xml_word.set("pos", trio[1])
			#xml_word.set("ne", trio[2])
		sentences.append(words)
	return sentences
	
def tokenizeFromFile(text):
	"""tokenizes text 'text' and yields a tokenized sentence. """
	
	import re

	sentence = re.compile(r"[^.!?\s][^.!?]*(?:[.!?](?![\'\"]?\s|$)[^.!?]*)*[.!?]?[\'\"]?(?=\s|$)")
	token = re.compile(r"(\b(\w+[\-\']*[\w]*)\b)|([,\.\?:!-])")
	sentences = sentence.findall(text)
	
	for sentence in sentences:
		sent = ''.join(sentence)
		tokens = token.finditer(sent)
		tok_sent = [t.group(0) for t in tokens]
		yield tok_sent

def handleFile(filename):
	with open("temp.txt", 'wb+') as f:
		for chunk in filename.chunks():
			f.write(chunk)
	
	with codecs.open("temp.txt", mode = 'r', encoding = 'utf-8') as r:
		content = r.read()
		return content
