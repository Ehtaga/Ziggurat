#!/usr/bin/python
# -*-coding:utf-8-*

import re
import os, codecs
from xml.dom.minidom import parse

# Parameters
#################################################

DICTIONARY = "./dico/elra_utf8.final"

SOURCE = "./data/corpus_breast_cancer/tmp_sc_fr/shortcorpus.lem.utf8.tmp"
TARGET = "./data/corpus_breast_cancer/tmp_sc_en/corpus.lem.utf8.tmp"

GOLD = "./data/corpus_breast_cancer/ts.xml"

SOURCESTOPWORDS = "./stopwords_fr.txt"
TARGETSTOPWORDS = "./stopwords_en.txt"

WINDOWSIZE = 3

#def function getContextVector(token):



# Functions
#################################################

# Récupération du dictionnaire
def loadDict(filename):
	dic = {}
	with codecs.open(filename, "r", "utf-8") as dictfile:
		for line in dictfile:
			matchObj = re.match( r'(.*)::(.*)::', line, re.M|re.I)
			dic[matchObj.group(1)]=matchObj.group(2)
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
		if word not in stopwords and lemma not in stopwords and lemma not in [',', '.', "'", ';', ':', '_', '?', '!'] and not lemma.isdigit() and not token.isspace() and len(token.split('/')) > 2:
			pos = getPOS(token)
			if pos not in ['CAR', 'UNITE', 'SYM']:
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
		#print i, word
		if lemma not in cvlist:
			cvlist[lemma] = {}
		for k in range(0,min(i,WINDOWSIZE)):
			contextWord = tokens[i-k-1]
			contextLemma = getLemma(contextWord)
			if contextLemma not in cvlist[lemma]:
				cvlist[lemma][contextLemma] = 1
			else:
				cvlist[lemma][contextLemma] += 1
		for k in range(0,min(len(tokens)-i-1,WINDOWSIZE)):
			contextWord = tokens[i+k+1]
			contextLemma = getLemma(contextWord)
			if contextLemma not in cvlist[lemma]:
				cvlist[lemma][contextLemma] = 1
			else:
				cvlist[lemma][contextLemma] += 1
		i += 1
	return cvlist

# Récupération du gold
def loadGold(filename):
	dom = parse(filename)
	gold = {}
	source = ""
	targets = []
	for element in dom.getElementsByTagName('TRAD'):
		if element.attributes['valid'].value == 'yes':
			for lang in element.getElementsByTagName('LANG'):
				if lang.getAttribute('type') == 'source':
					source = lang.getElementsByTagName('LEM')[0].firstChild.wholeText
				else:
					targets.append(lang.getElementsByTagName('LEM')[0].firstChild.wholeText)
			gold[source] = targets
	return gold

# Main
#################################################

dic = loadDict(DICTIONARY)
source = loadSource(SOURCE)
clean_source = filterStopWords(source,SOURCESTOPWORDS)
cvlist = contextVectors(clean_source)
for cv in cvlist:
	print cv
	for term in cvlist[cv]:
		print "==>", term, cvlist[cv][term]

#etc/sudoers entre env_reset et badpass
#source ~/.bashrc

# top10 et top2O


# tester si aa_bbb => remplacer par aa bbb pour chercher dans le dico