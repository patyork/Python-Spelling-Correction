# Spelling correction
import re, collections
import string
import os.path

class SpellingCorrector:
	
	validWords = {}
	NWORDS = None
	alphabet = 'abcdefghijklmnopqrstuvwxyz'
	
	Emojis = {}     # This is by no means a complete list
	
	# Initialize a SpellingCorrector with Valid Words and a Trained Spelling Corrector
	def __init__(self):
		# Define the Valid Words
		with open(os.path.join(os.path.dirname(__file__), 'ValidWords.txt'), 'r') as f:
			for line in f:
				self.validWords.update({line.strip().lower():1})
        
        # Define a Bayesian Spelling Corrector
		self.NWORDS = self._train(self._words(file(os.path.join(os.path.dirname(__file__), 'NewSpellCheckCorpus.txt')).read()))
		
		# Define the Emojis
		happy = ":-) :) :o) :] :3 :c) :> =] 8) =) :} :^) :-D :D 8-D 8D x-D xD X-D XD =-D =D =-3 =3 B^D :-)) :'-) :') ;-) ;) *-) *) ;-] ;] ;D ;^) :-, }:-) }:) 3:-) 3:) O:-) 0:-3 0:3 0:-) 0:) 0;^) |;-) |-O <3 (-: (: (o: [: <: [= (8 (= (-= {: {-: {-= (^: (^= ((: (((: ((((: (((((: ((((((: :)) :))) :)))) :))))) :)))))) ((-: (((-: ((((-: (((((-: ((((((-: :-)) :-))) :-)))) :-))))) :-)))))) :DD 8DD XDD X-DD"
		sad = ">:[ :-( :(  :-c :c :-< :< :-[ :[ :{ ;( :-|| :@ >:( :| :-| :-/ :-\ :/ :\ :'-( :'( </3"

		for x in happy.split(' '):
			self.Emojis.update({x:'happy'})
		for x in sad.split(' '):
			self.Emojis.update({x:'sad'})
        
 	#TODO
 	# Add Update function to update the valid words list, and the spelling corrector corpus
 	# Then, reinitiate the SpellingCorrector
        		
    
    # From Paul Norvig's Spelling Corrector
	def _words(self, text):
		return re.findall('[a-z]+', text.lower())

	def _train(self, features):
		model = collections.defaultdict(lambda: 1)
		for f in features:
			model[f] += 1
		return model

	def _edits1(self, word):
		s = [(word[:i], word[i:]) for i in range(len(word) + 1)]
		deletes    = [a + b[1:] for a, b in s if b]
		transposes = [a + b[1] + b[0] + b[2:] for a, b in s if len(b)>1]
		replaces   = [a + c + b[1:] for a, b in s for c in self.alphabet if b]
		inserts    = [a + c + b     for a, b in s for c in self.alphabet]
		return set(deletes + transposes + replaces + inserts)

	def _known_edits2(self, word):
		return set(e2 for e1 in self._edits1(word) for e2 in self._edits1(e1) if e2 in self.NWORDS)

	def _known(self, words):
		return set(w for w in words if w in self.NWORDS)

	def _correct(self, word):
		candidates = self._known([word]) or self._known(self._edits1(word)) or self._known_edits2(word) or [word]
		return max(candidates, key=self.NWORDS.get)
		
	
	
	## Low level spelling correction functions
	
	# aall ---> all
	def _FixCharacterRepetitions(self, word):
		return re.sub('([ahijkquvwxy])\\1+', '\\1', word)

	# welll ---> well
	def _FixCharacterRepetitions2(self, word):
		return re.sub('([abcdefghijklmnopqrstuvwxyz])\\1+', '\\1\\1', word)

	# hellloo --> helo (hopefully correct will pick this up)
	def _FixCharacterRepetitions3(self, word):
		return re.sub('([abcdefghijklmnopqrstuvwxyz])\\1+', '\\1', word)

	# EX: all.it --> all it
	def _FixLostSpaces(self, word):
		return re.sub('([a-z])[,.;/\\\]([a-z])', '\\1 \\2', word)

	# EX: thatis --> that is
	def _FixRuntogethers(self, word):
		s = [(word[:i], word[i:]) for i in range(len(word) + 1)]
		runtogethers = [a + ' ' + b for a,b in s]

		runtogethers = set(runtogethers)

		words = zip([x.split(' ')[0] for x in runtogethers], [x.split(' ')[1] for x in runtogethers])

		for wordPair in words:
			if wordPair[0] in self.validWords and wordPair[1] in self.validWords:
				return wordPair[0] + ' ' + wordPair[1]
		    
		return word
	
	
	
	# Intermediate spelling correction function
	def _FullCorrect(self, word):
		word = word.lower()
	
		# First, check if in the valid word list, return quickly is it is
		if word in self.validWords:
			return word
	
		# Check emojis/emoticons
		if word in self.Emojis:
			return self.Emojis[word]
	
		#Check hyphenation here
	
	
	
	
		#Remove puncuation
		nowCorrect = word.translate(None, string.punctuation)
		if nowCorrect in self.validWords:
			return nowCorrect
	
		# Try to fix double character repetitions
		nowCorrect = self._FixCharacterRepetitions(word)
		if nowCorrect in self.validWords:
			return nowCorrect
	
		# Try to fix triple character repetitions
		nowCorrect = self._FixCharacterRepetitions2( nowCorrect )
		if nowCorrect in self.validWords:
			return nowCorrect
	
		# Try to fix all character repetitions and hope correct picks it up
		nowCorrect = self._FixCharacterRepetitions3( nowCorrect )
		if nowCorrect in self.validWords:
			return nowCorrect
	
		if nowCorrect not in self.validWords:
			nowCorrect = self._correct(word)
	
		if nowCorrect not in self.validWords:
			return None
		return nowCorrect
		
	
	
	# High-level single-word Spelling Corrector
	def SpellingCorrect(self, word):
	
		if word in self.validWords:
			#print 'in valid words'
			yield word
	
		elif word in self.Emojis:
			yield self.Emojis[word]
		
		elif len(word) < 3:
			yield None
	
		else:
	
			words = []
			# Try to fix dropped spaces and run togethers
			x = self._FixLostSpaces(word).split(' ')
		
			if len(x) > 1:
				# dealing with more than one word
				words = x
			else:
				y = self._FixRuntogethers(word).split(' ')
				if len(y) > 1:
					# dealing with more than one word
					words = y
				
				else: #must be dealing with one word
					words.append(word)
				
			for w in words:
				yield self._FullCorrect(w)
	
	
	# High-level multi-word Spelling Corrector (generator)
	def CorrectSpelling(self, chunk):
		words = chunk.strip().split(' ')
	
		for word in words:
			for correct in self.SpellingCorrect(word):
				if correct is not None: yield correct
	
	
	
	
