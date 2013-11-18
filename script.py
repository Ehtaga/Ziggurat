#!/usr/bin/python
# -*-coding:utf-8-*

import re
import os, codecs

# Parameters
#################################################

DICTIONARY = "./dico/elra_utf8.final"

SOURCE = "./data/corpus_breast_cancer/tmp_sc_fr/corpus.lem.utf8.tmp"
TARGET = "./data/corpus_breast_cancer/tmp_sc_en/corpus.lem.utf8.tmp"

GOLD = "./data/corpus_breast_cancer/ts.xml"

SOURCESTOPWORDS = "./stopwords_fr.txt"
TARGETSTOPWORDS = "./stopwords_en.txt"

WINDOWSIZE = 3

#def function getContextVector(token):



# Functions
#################################################

# Récupération du dictionnaire
def importDict(filename):
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
def importSource(filename):
	fr = ""
	with codecs.open(filename, "r", "utf-8") as srcfile:
		for line in srcfile:
			fr += line
	return fr.split(" ")

# Filtrage des stopwords
def filterStopWords(words, stopwordsfile):
	stopwords = []
	filteredWords = []
	with codecs.open(stopwordsfile, "r", "utf-8") as swfile:
		for line in swfile.readlines():
			stopwords.append(line[0:-1])
	for word in words:
		lemma = getLemma(word)
		if getWord(word) not in stopwords and lemma not in stopwords and lemma not in [',', "'", ';', ':', '_'] and not lemma.isdigit(): #R
			filteredWords.append(word)
	return filteredWords


# Main
#################################################

#dic = importDict(DICTIONARY)
source = importSource(SOURCE)
clean_source = filterStopWords(source,SOURCESTOPWORDS)
print clean_source

#etc/sudoers entre env_reset et badpass
#source ~/.bashrc

# top10 et top2O


# print line
# 		matchObj = re.search( r'.*/.*/(.*) ', line, re.M|re.I)
# 		if matchObj:
# 			print matchObj.group(1)
# 		else:
# 			print "No match!!"