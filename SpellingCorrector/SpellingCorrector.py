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
		happy = ":-) :) :o) :] :3 :c) :> :&gt; =] 8) =) =)) =))) :} :^) :-D :D 8-D 8D x-D xD X-D xD =-D =D =-3 =3 b^d :-)) :'-) :') ;-) ;) *-) *) ;-] ;] ;d ;^) :-, }:-) }:) 3:-) 3:) o:-) 0:-3 0:3 0:-) 0:) 0;^) |;-) |-O <3 &lt;3 &lt;33 &lt;333 (-: (: (o: [: <: &lt;: [= (8 (= (-= {: {-: {-= (^: (^= ((: (((: ((((: (((((: ((((((: :)) :))) :)))) :))))) :)))))) ((-: (((-: ((((-: (((((-: ((((((-: :-)) :-))) :-)))) :-))))) :-)))))) :DD 8DD XDD X-DD =&gt; :p (; c: ^_^ ^.^ ;)) ;))) ;))))"
		sad = ">:[ &lt;:[ :-( :(  :-c :c :-< :'d :< :-[ ]-: :[ ]: :{ ;( :-|| :@ >:( :| :-| :-/ :-\ :/ :\ /: /-: /= /-= :'-( :'( </3 &lt;/3 &lt;/33 &lt;/333 -.- -_- -__- -___- ._. ): :(( :((( :(((( )): ))): )))):"

		for x in happy.split(' '):
			self.Emojis.update({x.lower():'happy'})
		for x in sad.split(' '):
			self.Emojis.update({x.lower():'sad'})
        
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
		#return set(deletes + transposes + replaces + inserts)
		return set([x for x in deletes + transposes + replaces + inserts if (x in self.validWords)])

	def _known_edits2(self, word):
		return set(e2 for e1 in self._edits1(word) for e2 in self._edits1(e1) if e2 in self.NWORDS)

	def _known(self, words):
		return set(w for w in words if w in self.NWORDS)

	def _correct(self, word):
		candidates = self._known(self._edits1(word)) or self._known_edits2(word) or [word]
		#print candidates
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
		word = word.lower()
	
		if word in self.Emojis:
			yield self.Emojis[word]
		
		elif len(word) < 3:
			yield None
			
		elif word in self.validWords:
			#print 'in valid words'
			yield word
		
			
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
	
	
	# Hashtag splitter
	# TODO: 5 and 6 words runtogether
	#		apply this to the runtogethers above?
	def HashTagSplit(self, hashtag):
		hashtag = hashtag.replace('#', '').lower()
		
		# two words ran together
		s = [(hashtag[:i], hashtag[i:]) for i in range(len(hashtag) + 1)]
		runtogethers = [a + ' ' + b for a,b in s]
		
		runtogethers = set(runtogethers)

		words = zip([x.split(' ')[0] for x in runtogethers], [x.split(' ')[1] for x in runtogethers])
		
		DONE = False
		
		for wordPair in words:
			if wordPair[0] in self.validWords and wordPair[1] in self.validWords:
				yield wordPair[0]
				yield wordPair[1]
				DONE = True
				break
		
		if not DONE:
			# Three words ran together
			s = []
			for i in range(1, len(hashtag)):
				for j in range(1, len(hashtag)):
					if j > i:
						s.append((hashtag[:i], hashtag[i:j], hashtag[j:]))
					
			for wordTup in s:
				if wordTup[0] in self.validWords and wordTup[1] in self.validWords and wordTup[2] in self.validWords:
					yield wordTup[0]
					yield wordTup[1]
					yield wordTup[2]
					DONE = True
					break
					
			if not DONE:
				# 4 words ran together
				s = []
				for i in range(1, len(hashtag)):
					for j in range(2, len(hashtag)):
						for k in range(3, len(hashtag)):
							if j>i and k>j:
								s.append((hashtag[:i], hashtag[i:j], hashtag[j:k], hashtag[k:]))
				
				for wordTup in s:
					if wordTup[0] in self.validWords and wordTup[1] in self.validWords and wordTup[2] in self.validWords and wordTup[3] in self.validWords:
						yield wordTup[0]
						yield wordTup[1]
						yield wordTup[2]
						yield wordTup[3]
						DONE = True
						break
				
	
	# Quick and dirty spam detector.
	def IsSpam(self, tweet):
		tweet=tweet.lower()
		
		# RTs can't be spam (in this model)
		if tweet.startswith('rt '):
			return False
			
		isSpam = False
		
		## Working
		if 'stats:' in tweet or 'automatically checked' in tweet:
			return True
			
		## Working
		if 'harvested' in tweet:
			return True
		
		## Working
		if 'unfollow' in tweet and 'via' in tweet:
			return True
		
		## Meh, working about 90%, not picking up many Tweets
		if 'i just posted' in tweet and 'http' in tweet:
			return True
		
		## Quite a few false-positives
		words = tweet.strip().split(' ')
		if tweet.startswith('@') and words[len(words)-1].startswith('http') and (' u ' in tweet or 'you' in tweet) and ('crazy' in tweet or 'nuts' in tweet):
			return True
		
			
		return isSpam
	
	#TODO
	# See about the corrector not correcting for added punctuation (anyone,/anyone. != anyone   ATM)
	# See about dictionary inclusions
	# Possessives? (tomorrow's)
	# Lemmatization - when to do it most effectively
	# Make all above fixes; reprocces reviews; retrain
	def PossibleInclusions():
		pass
		'''
		&gt;&gt;&gt;&gt;		>>>>		meaning: better than/the best			ex: my mom >>>>			my mom is the best
		&lt;&lt;&lt;&lt;		<<<<		meaning: worse than/the worst			ex: my brother <<<		my brother is the worst
		smh									meaning: shake my head/disappointed
		stfu
		lmao
		lmfao
		haha
		hahaha
		shit
		fuck
		fucking
		fucken
		w/o									without
		omg
		alotta
		hmmmm
		lol
		hmmm
		im
		gotta
		ok 			----> okay
		tryna		----> trying
		em			----> them
		bc			----> because
		af			----> as fuck --> really
		xx, xxxx	----> hug/love
		idgaf
		
		
		
		
		
		Words to be added to dictionary:
		
		stressful
		happiness
		genuinely
		anyone( punctuation not picked up? ,.)
		updates
		introducing
		exams
		siblings
		families
		releasing
		edited
		responsibilities
		featuring
		creepiest
		negativity
		ignoring
		realizing
		promoting
		businesses
		definitely
		happened
		congrats
		enjoyed
		should've
		companies
		laughed
		
		
		
		'''
