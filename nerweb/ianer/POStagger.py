# -*- coding: utf-8 -*-
import os
import random
from collections import defaultdict
import pickle
import codecs
import xml.etree.ElementTree as ET
from ianer.perceptron import AveragedPerceptron

class POSPerceptronTagger(object):

	START = ['-START-', '-START2-']
	END = ['-END-', '-END2-']
	
	def __init__(self, load=False):
		self.model = AveragedPerceptron()
		self.tagdict = {}
		self.classes = set()
		self.t_sentence = []
		if load:
			self.load("ianer/postagger.t")
	
	"""def loadData(self, filename):
		tree = ET.parse(filename)
		root = tree.getroot()
		xml_sentence = root.findall("./sentence")
		for i in xml_sentence:
			sentence = []
			words = i.findall("./w")
			for w in words:
				pos = w.get("pos")
				token = w.text
				sentence.append((token,pos))
			yield sentence"""
			
	def loadData(self, filename):
		sentences = []
		sentence = []
		with codecs.open(filename,mode = 'r', encoding = 'utf-8') as f:
			for line in f:
				if line == '\n':
					sentences.append(sentence)
					sentence = []
					continue
				h = line.strip()
				sentence.append(h)
			
		for sentence in sentences:
			yield sentence
				

	def tagFromFile(self, file_name):
		'''Tags a suc2 xml file and returns a list of word, tag pairs.'''
		prev, prev2 = self.START
		for sentence in self.loadData(file_name):
			tokens = []
			context = self.START + [w for w in sentence] + self.END
			for i, word in enumerate(sentence):
				tag = self.tagdict.get(word)
				if not tag:
					feats = self._get_features(i, word, context, prev, prev2)
					tag = self.model.predict(feats)
				tokens.append((word, tag))
				prev2 = prev
				prev = tag
			self.t_sentence.append(tokens)
	
	def tagSentence(self, sentence):
		"""tags a list of tokens"""
		prev, prev2 = self.START
		context = self.START + [w for w in sentence] + self.END
		tokens = []
		for i, word in enumerate(sentence):
			tag = self.tagdict.get(word)
			if not tag:
				feats = self._get_features(i, word, context, prev, prev2)
				tag = self.model.predict(feats)
			prev2 = prev
			prev = tag
			tokens.append((word, tag))
		return tokens
		
	def train(self, file_name, save_loc=None, nr_iter=1):
		'''Train a model from sentences, and save it at ``save_loc``. ``nr_iter``
		controls the number of Perceptron training iterations.

		:param file_name: A SUC2 xml file with <text><sentence><w> format. 
		:param save_loc: If not ``None``, saves a pickled model in this location.
		:param nr_iter: Number of training iterations.
		'''
		print("training")
		self._make_tagdict(file_name)
		self.model.classes = self.classes
		prev, prev2 = self.START
		for iter in range(nr_iter):
			for sentence in self.loadData(file_name):
				context = self.START + [w for w, t, ne in sentence] + self.END
				for i, pair in enumerate(sentence):
					guess = self.tagdict.get(pair[0])
					if not guess:
						feats = self._get_features(i, pair[0], context, prev, prev2)
						guess = self.model.predict(feats)
						self.model.update(pair[1], guess, feats)
					prev2 = prev
					prev = guess
		self.model.average_weights()
		# Pickle as a binary file
		if save_loc is not None:
			pickle.dump((self.model.weights, self.tagdict, self.classes),
						open(save_loc, 'wb'), -1)
		return None

	def _get_features(self, i, word, context, prev, prev2):
		'''Map tokens into a feature representation, implemented as a
		{hashable: float} dict. If the features change, a new model must be
		trained.
		'''
		def add(name, *args):
			features[' '.join((name,) + tuple(args))] += 1

		i += len(self.START)
		features = defaultdict(int)
		# It's useful to have a constant feature, which acts sort of like a prior
		add('bias')
		add('i suffix', word[-3:])
		add('i pref1', word[0])
		add('i-1 tag', prev)
		add('i-2 tag', prev2)
		add('i tag+i-2 tag', prev, prev2)
		add('i word', context[i])
		add('i-1 tag+i word', prev, context[i])
		add('i-1 word', context[i-1])
		add('i-1 suffix', context[i-1][-3:])
		add('i-2 word', context[i-2])
		add('i+1 word', context[i+1])
		add('i+1 suffix', context[i+1][-3:])
		add('i+2 word', context[i+2])
		return features

	def _make_tagdict(self, file_name):
		print("making tagdict")
		'''Make a tag dictionary for single-tag words.'''
		counts = defaultdict(lambda: defaultdict(int))
		for sentence in self.loadData(file_name):
			for word, tag, ne in sentence:
				counts[word][tag] += 1
				self.classes.add(tag)
		freq_thresh = 20
		ambiguity_thresh = 0.97

		for word, tag_freqs in counts.items():
			tag, mode = max(tag_freqs.items(), key=lambda item: item[1])
			n = sum(tag_freqs.values())
			# Don't add rare words to the tag dictionary
			# Only add quite unambiguous words
			if n >= freq_thresh and (float(mode) / n) >= ambiguity_thresh:
				self.tagdict[word] = tag

	def load(self, loc):
		'''Load a pickled model.'''
		try:
			w_td_c = pickle.load(open(loc, 'rb'))
		except IOError:
			msg = ("Missing trontagger.pickle file.")
			raise FileExistsError(msg)
		self.model.weights, self.tagdict, self.classes = w_td_c
		self.model.classes = self.classes
		return None
	
	def write(self, filename):
		with codecs.open(filename, mode = 'w', encoding = 'utf-8') as _file:
			for sentence in self.t_sentence:
				for pair in sentence:
					_file.write(pair[0] + '\t' + pair[1])
					_file.write('\n')
				_file.write('\n')