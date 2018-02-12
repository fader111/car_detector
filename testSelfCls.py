# -*- coding: utf-8 -*-

''' цель теста - понять как взаимодействуют переменные в методе класса и методе экземпляра '''

import os

class Test(object):
	frame = 23 
	objCounter = 0
	
	#@classmethod
	#def __init__(self): # и не важно что стоит self в качестве аргумента, если это это классметод, 
	#					# см на декоратор, то это полюбому будет класс - тот что  обычно cls
	#	self.objCounter+=1
	#	#self.objCounter+=1
	#	print ('objCounter = ',self.objCounter)
	def __init__(self): # это второй вариант. закоменченый выше тоже работает
		Test.objCounter+=1
		print 'init!!!'
		
	def initi(cls):
		print('cls.frame=',cls.frame)
		
	def metod(self,cls):
		self.objCounter = 0
		print('From method: self.objCounter = ',self.objCounter)
		print('From method: cls.objCounter = ',cls.objCounter)

print (Test.frame, Test.objCounter)
a= Test()		
a.initi()
a.metod(Test)

b = Test()
c=Test()
d=Test()
d.metod(Test)

print u'Создано экземпляров класса=',Test.objCounter

''' Итог - взаимодействуют они красиво '''


