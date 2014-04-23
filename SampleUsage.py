from SpellingCorrector import SpellingCorrector as SC

corrector = SC.SpellingCorrector()

#print corrector._correct('probbly')

sentence = 'This. is a saample reviiew/sntence thatshould show alll of the abbilities of.this systenn :)'

for x in corrector.CorrectSpelling(sentence):
	print x,
print ''
