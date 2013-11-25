#!/usr/bin/python
# -*-coding:utf-8-*

import re
import os, codecs
from xml.dom.minidom import parse
from math import sqrt
from math import log1p
from math import log


# Usage
#################################################
# python script.py



# Parameters
#################################################

DICTIONARY = "./dico/elra_utf8.final"

SOURCE = "./data/corpus_breast_cancer/tmp_sc_fr/corpus.lem.utf8.tmp"
TARGET = "./data/corpus_breast_cancer/tmp_sc_en/corpus.lem.utf8.tmp"

GOLD = "./data/corpus_breast_cancer/ts.xml"

SOURCESTOPWORDS = "./stopwords_fr.txt"
TARGETSTOPWORDS = "./stopwords_en.txt"

WINDOWSIZE = 3




# Functions
#################################################

# Récupération du dictionnaire
def loadDict(filename):
	dic = {}
	with codecs.open(filename, "r", "utf-8") as dictfile:
		for line in dictfile:
			matchObj = re.match( r'(.*)::(.*)::', line, re.M|re.I)
			term = matchObj.group(1)
			translation = matchObj.group(2)
			if term not in dic:
				dic[term] = []
			dic[term].append(translation)
	return dic


# Récupération du mot, de son POStag et de son lemme
def getWord(token):
	return token.split('/')[0]

def getPOS(token):
	return token.split('/')[1].split(':')[0]

def getLemma(token):
	if token.isspace() or len(token.split('/')) == 1 :
		return token
	if len(token.split('/')) == 2:
		return token.split('/')[1]
	else:
		return token.split('/')[2].split(':')[0]

# Récupération du corpus fr
def loadSource(filename):
	fr = ""
	with codecs.open(filename, "r", "utf-8") as srcfile:
		for line in srcfile:
			matchFILE = re.match( r'^__FILE', line, re.M|re.I)
			matchENDFILE = re.match( r'^__ENDFILE', line, re.M|re.I)
			if not matchFILE and not matchENDFILE:
				fr += line
	return fr.split(" ")

# Filtrage des stopwords
def filterStopWords(tokens, stopwordsfile):
	stopwords = []
	filteredTokens = []
	with codecs.open(stopwordsfile, "r", "utf-8") as swfile:
		for line in swfile.readlines():
			stopwords.append(line[0:-1])
	for token in tokens:
		lemma = getLemma(token)
		word = getWord(token).lower()
		if word not in stopwords and lemma not in stopwords and lemma not in [',', '.', "'", ';', ':', '_', '?', '!', '(', ')', '[', ']', '"'] and not lemma.isdigit() and not token.isspace() and len(token.split('/')) > 2:
			pos = getPOS(token)
			if pos not in ['CAR', 'UNITE', 'SYM', 'CD']:
				filteredTokens.append(token)
	return filteredTokens


# Donne le nb d'occurences de chaque mot
def getNbOcc(tokens):
	occ = {}
	for token in tokens:
		lemma = getLemma(token)
		if lemma not in occ:
			occ[lemma] = 1
		else:
			occ[lemma] += 1
	return occ

# Filtrage des hapax
def filterHapax(tokens,occ):
	filteredTokens = []
	for token in tokens:
		lemma = getLemma(token)
		if occ[lemma] > 1:
			filteredTokens.append(token)
	return filteredTokens

# Récupération des termes source non traduits
# def filterAlreadyTranslated(tokens, dict):
# 	filteredTokens = []
# 	for token in tokens:
# 		lemma = getLemma(token)
# 		word = getWord(token).lower()
# 		if word not in dict and lemma not in dict and word not in filteredTokens:
# 			filteredTokens.append(token)
# 	return filteredTokens

# Création des vecteurs de contexte
def contextVectors(tokens):
	cvlist = {}
	i = 0
	for token in tokens:
		word = getWord(token).lower()
		lemma = getLemma(token)
		pos = getPOS(token)
		# print i, word, pos
		#if pos in ['NN', 'NNS', 'NNP', 'NNPS', 'SBC', 'SBP', 'ADJ', 'ADV', 'VCJ', 'VNCFF', 'VNCNT', 'VPAR', 'ADJ1PAR', 'ADJ2PAR']:
		if pos not in ['CC','CD','DT','EX','FW','IN','JJR','JJS','LS','MD','POS','PRP','PRP$','RB','RBR','RBS','RP','SYM','TO','UH','VB','VBD','VBG','VBN','VBP','VBZ','WDT','WP','WP$','WRB']:
			if lemma not in cvlist:
				cvlist[lemma] = {}
			for k in range(0,min(i,WINDOWSIZE)):
				contextWord = tokens[i-k-1]
				contextLemma = getLemma(contextWord)
				if len(contextLemma) > 0:
					if contextLemma not in cvlist[lemma]:
						cvlist[lemma][contextLemma] = 1.0
					else:
						cvlist[lemma][contextLemma] += 1.0
			for k in range(0,min(len(tokens)-i-1,WINDOWSIZE)):
				contextWord = tokens[i+k+1]
				contextLemma = getLemma(contextWord)
				if len(contextLemma) > 0:
					if contextLemma not in cvlist[lemma]:
						cvlist[lemma][contextLemma] = 1.0
					else:
						cvlist[lemma][contextLemma] += 1.0
		i += 1

	# On ne garde pas les mots aparraissant une seule fois
	# short_cvlist = {}
	# for token in cvlist:
	# 	short_cvlist[token] = {}
	# 	for neighbour in cvlist[token]:
	# 		if cvlist[token][neighbour] > 1:
	# 			short_cvlist[token][neighbour] = cvlist[token][neighbour]

	# cvlist = {k: v for k, v in cvlist.items() if v > 1}

	return cvlist

# Information mutuelle
def normalizeIM(vector,occ):
	norm_cvlist = {}
	total_nb_cooc = 0.0
	for term in vector:
		total_nb_cooc += float(sum(vector[term].values()))
	total_nb_cooc /= 2.0
	total_nb_occ = float(sum(occ.values()))
	for term in vector:
		norm_cvlist[term] = {}
		for coocc in vector[term]:
			a = vector[term][coocc] / total_nb_cooc
			b = occ[coocc] / total_nb_occ
			c = occ[term] / total_nb_occ
			norm_cvlist[term][coocc] = log(a/(b*c))
	return norm_cvlist

# Dice
def normalizeDice(vector,occ):
	norm_cvlist = {}
	for term in vector:
		norm_cvlist[term] = {}
		for coocc in vector[term]:
			a = vector[term][coocc]
			b = occ[coocc]
			c = occ[term]
			norm_cvlist[term][coocc] = 2*a/(b+c)
	return norm_cvlist

# Récupération du gold
def loadGold(filename):
	dom = parse(filename)
	gold = {}
	for element in dom.getElementsByTagName('TRAD'):
		source = ""
		targets = []
		if element.attributes['valid'].value == 'yes':
			for lang in element.getElementsByTagName('LANG'):
				if lang.getAttribute('type') == 'source':
					source = lang.getElementsByTagName('LEM')[0].firstChild.wholeText
				else:
					targets.append(lang.getElementsByTagName('LEM')[0].firstChild.wholeText)
			gold[source] = targets
	return gold

# Liste des mots à traduire
def getSourceTerms(source_vectors, target_vectors,gold):
	terms_to_translate = {}
	for term in gold:
		if term in source_vectors:
			for translation in gold[term]:
				if translation in target_vectors:
					terms_to_translate[term] = source_vectors[term]
	return terms_to_translate

# Traduction des vecteurs de contexte
def translateVectors(vectors,dictionary):
	translated_vectors = {}
	for term in vectors:
		translated_vectors[term] = {}
		for word in vectors[term]:
			if re.sub('_',' ',word) in dictionary:
				for translation in dictionary[re.sub('_',' ',word)]:
					if translation not in translated_vectors[term]:
						translated_vectors[term][translation] = vectors[term][word]
					else:
						if vectors[term][word] > translated_vectors[term][translation]:
							translated_vectors[term][translation] = vectors[term][word]

			# else:
			# 	translated_vectors[term][word] = ["???"]
	return translated_vectors

# Calcul de similarité entre 2 vecteurs
def getRootedSquareSums(vectors):
	sums = {}
	for term in vectors:
		sums[term] = 0
		for word in vectors[term]:
			sums[term] += vectors[term][word]**2
		sums[term] = sqrt(sums[term])
	return sums

def getSimilarity(vector1, vector2, translated_square_sums, target_square_sums):
	# print 'Similarity'
	w1, v1 = vector1
	w2, v2 = vector2
	# print len(v1), len(v2)
	intersection = set(v1.keys()) & set(v2.keys())
	numerator = sum([v1[x] * v2[x] for x in intersection])
	denominator = translated_square_sums[w1] * target_square_sums[w2]
	if denominator:
		return w2, float(numerator) / denominator
	else:
		return 0

# Calcul de similarité avec tous les vecteurs cible
def getSimilarities(vector1, target_vectors, translated_square_sums, target_square_sums):
	similarities = {}
	# print 'Entrée getSimilarities'
	for term in target_vectors:
		# print 'Term :', term
		w, s = getSimilarity(vector1, [term, target_vectors[term]], translated_square_sums, target_square_sums)
		similarities[term] = s
	return similarities

# Calcul du Top des résultats
def getTop(n, similarities):
	return sorted(similarities, key=similarities.get, reverse=True)[:n]




# Main
#################################################

print 'Loading dictionary...'
dic = loadDict(DICTIONARY)

print 'Loading source...'
source = loadSource(SOURCE)

print 'Cleaning source...'
clean_source = filterStopWords(source,SOURCESTOPWORDS)
source_occ = getNbOcc(clean_source)
clean_source = filterHapax(clean_source,source_occ)

print 'Loading target...'
target = loadSource(TARGET)

print 'Cleaning target...'
clean_target = filterStopWords(target,TARGETSTOPWORDS)
target_occ = getNbOcc(clean_target)
clean_target = filterHapax(clean_target,target_occ)

print 'Loading gold...'
gold = loadGold(GOLD)

print 'Creating source context vectors...'
source_cvlist = contextVectors(clean_source)
#source_cvlist = normalizeDice(source_cvlist,source_occ)

print 'Creating target context vectors...'
target_cvlist = contextVectors(clean_target)
#target_cvlist = normalizeDice(target_cvlist,target_occ)

print 'Getting missing translations...'
source_terms = getSourceTerms(source_cvlist,target_cvlist,gold)

print 'Translating source vectors...'
translated_source_terms = translateVectors(source_terms,dic)

print 'Pre-computing rooted square sums...'
translated_square_sums = getRootedSquareSums(translated_source_terms)
target_square_sums = getRootedSquareSums(target_cvlist)

print 'Computing cosine similarities vector...'
top1 = 0.0
top5 = 0.0
top10 = 0.0
top20 = 0.0
top50 = 0.0
top100 = 0.0
for term in source_terms:
	print 'Computing similarities vector for term',term
	similarities = getSimilarities([term,translated_source_terms[term]],target_cvlist,translated_square_sums,target_square_sums)
	for correctTranslation in gold[term]:
		#print correctTranslation
		if correctTranslation in getTop(1,similarities):
			print 'Top1'
			top1 += 1.0
		else:
			if correctTranslation in getTop(5,similarities):
				print 'Top5'
				top5 += 1.0
			else:
				if correctTranslation in getTop(10,similarities):
					print 'Top10'
					top10 += 1.0
				else:
					if correctTranslation in getTop(20,similarities):
						print 'Top20'
						top20 += 1.0
					else:
						if correctTranslation in getTop(50,similarities):
							print 'Top50'
							top50 += 1.0
						else:
							if correctTranslation in getTop(100,similarities):
								print 'Top100'
								top100 += 1.0
print 'Top 1 :', top1/len(source_terms)
print 'Top 5 :', (top1+top5)/len(source_terms)
print 'Top 10 :', (top1+top5+top10)/len(source_terms)
print 'Top 20 :', (top1+top5+top10+top20)/len(source_terms)
print 'Top 50 :', (top1+top5+top10+top20+top50)/len(source_terms)
print 'Top 100 :', (top1+top5+top10+top20+top50+top100)/len(source_terms)