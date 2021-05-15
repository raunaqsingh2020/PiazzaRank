from piazza_api import Piazza
from piazza_api.exceptions import AuthenticationError
from time import sleep
from io import StringIO
from html.parser import HTMLParser
from datetime import datetime, timedelta
from collections import defaultdict
import math

from Instructor import Instructor
from Algorithms import Algorithms

class PiazzaBot():
	def __init__(self):
		self.p = Piazza()
		self.login()
		self.instructors = {}
		#adjacency matrix for TA endorsements
		self.endorsementGraph = defaultdict(dict)

	def login(self):
		print('Enter your Piazza account email address:')
		username = input()
		print('Enter your Piazza account password:')
		password = input()
		print('\n...\n')
		try:
			self.p.user_login(username, password)
			self.classes = self.p.get_user_classes()
		except AuthenticationError:
			print('Invalid Email/Password!\n')
			self.login()

	def getClasses(self):
		return self.classes

	def getData(self, courseId, **kwargs):

		self.instructors = {}
		self.endorsementGraph = defaultdict(dict)

		course = self.p.network(courseId)
		posts = course.iter_all_posts()
		if kwargs.get('limit', None) is not None:
			#limit number of posts to analyze
			posts = course.iter_all_posts(limit=kwargs.get('limit', None))

		animation = "|/-\\"
		idx = 0

		for post in posts:
			print(animation[idx % len(animation)], end="\r")
			idx += 1
			if post['type'] == 'question':
				#find response times
				changeLog = post['change_log']
				recentStudentPost = None
				for change in changeLog:
					if ((change['type'] == 'i_answer' and 'uid' in change) and (course.get_users([change['uid']])[0]['role'] == 'professor' or course.get_users([change['uid']])[0]['role'] == 'ta')):
						if recentStudentPost:
							timeOfQuestion = datetime.strptime(recentStudentPost, '%Y-%m-%dT%H:%M:%SZ')
							timeOfAnswer = datetime.strptime(str(change['when']), '%Y-%m-%dT%H:%M:%SZ')
							responseTime = (timeOfAnswer - timeOfQuestion).total_seconds()
							if change['uid'] not in self.instructors:
								self.instructors[change['uid']] = Instructor(change['uid'], course)
							self.instructors[change['uid']].logResponseTime(responseTime)
					elif (change['type'] == 'create' or change['type'] == 'followup' or change['type'] == 'feedback') and ('uid' not in change or course.get_users([change['uid']])[0]['role'] == 'student'):
						recentStudentPost = change['when']
				#get response content and TA endorsements
				responses = post['children']
				while (len(responses) != 0):
					for response in responses:
						if (response['type'] == 'i_answer'):
							if response['history'][0]['uid'] not in self.instructors:
								self.instructors[response['history'][0]['uid']] = Instructor(response['history'][0]['uid'], course)
							studentEndorsers = 0
							for endorser in response['tag_endorse']:
								if endorser['role'] == 'student':
									studentEndorsers += 1
								else:
									#update adjacency matrix for TA endorsements
									if response['history'][0]['uid'] not in self.endorsementGraph[endorser['id']]:
										self.endorsementGraph[endorser['id']][response['history'][0]['uid']] = 0
									if endorser['id'] not in self.endorsementGraph[response['history'][0]['uid']]:
										self.endorsementGraph[response['history'][0]['uid']][endorser['id']] = 0
									self.endorsementGraph[endorser['id']][response['history'][0]['uid']] += 1
							self.instructors[response['history'][0]['uid']].addResponse(strip_tags(response['history'][0]['content']), studentEndorsers)
						if (response['type'] == 'feedback'):
							if ('uid' in response and (course.get_users([response['uid']])[0]['role'] == 'professor' or course.get_users([response['uid']])[0]['role'] == 'ta')):
								if response['uid'] not in self.instructors:
									self.instructors[response['uid']] = Instructor(response['uid'], course)
								studentEndorsers = 0
								for endorser in response['tag_good']:
									if endorser['role'] == 'student':
										studentEndorsers += 1
									else:
										#update adjacency matrix for TA endorsements
										if response['uid'] not in self.endorsementGraph[endorser['id']]:
											self.endorsementGraph[endorser['id']][response['uid']] = 0
										if endorser['id'] not in self.endorsementGraph[response['uid']]:
											self.endorsementGraph[response['uid']][endorser['id']] = 0
										self.endorsementGraph[endorser['id']][response['uid']] += 1
								self.instructors[response['uid']].addResponse(strip_tags(response['subject']), studentEndorsers)
						responses.remove(response)
						#go through followup discussions as well
						for child in response['children']:
							responses.append(child)
			sleep(1)

		self.printResults(course)

	#print major statistics and final TA ranking
	def printResults(self, course):
		print('Statistics:\n')
		print('Total Number of Responses:')
		numResponseList = sorted(self.instructors.values(), key=lambda x: x.responseCount, reverse=True)
		for value in numResponseList:
			if value.responseCount != 0:
				print(str(value.name) + ' (' + str(value.responseCount) + ')')
		
		print('\nAverage Response Time:')
		avgTimeList = sorted(self.instructors.values(), key=lambda x: x.avgResponseTime, reverse=False)
		for value in avgTimeList:
			if value.avgResponseTime != 0:
				print(str(value.name) + ' (' + str((timedelta(seconds=int(value.avgResponseTime)))) + ')')

		print('\nAverage Response Length (Characters):')
		avgLengthList = sorted(self.instructors.values(), key=lambda x: x.avgResponseLength, reverse=True)
		for value in avgLengthList:
			if value.avgResponseLength != 0:
				print(str(value.name) + ' (' + '%.2f' % value.avgResponseLength + ')')

		print('\nAverage Thanks Tags Received:')
		avgThanksList = sorted(self.instructors.values(), key=lambda x: x.avgThanksTags, reverse=True)
		for value in avgThanksList:
			print(str(value.name) + ' (' + '%.2f' % value.avgThanksTags + ')')

		print('\nCalculating Average Response Similarity...')

		postSimilarities = {}
		algos = Algorithms()
		for instructor in self.instructors.values():
			postSimilarities[instructor.name] = algos.cosineSimilarityPosts(instructor.responses)
		print('\nAverage Response Similarity (from 0 to 1, 1 being identical):')
		postSimilarities = sorted(postSimilarities.items(), key=lambda item: item[1])
		for name, value in postSimilarities:
			if value != 0:
				print(str(name) + ' (' + '%.3f' % value + ')')

		print('\nEndorsement Value (PageRank Value, from 0 to 1):')
		endorsementValues = sorted(algos.pageRank(self.endorsementGraph).items(), key=lambda item: item[1], reverse=True)
		for uid, val in endorsementValues:
			print(str(course.get_users([uid])[0]['name']) + ' (' + '%.2f' % val + ')')


		print('\n----------------OVERALL INSTRUCTOR RANKINGS----------------')
		scores = {}
		for instructor in self.instructors.values():
			score = instructor.responseCount * 1.2 * math.log(instructor.avgResponseLength, 2) * math.exp(instructor.avgThanksTags / 2)
			if (instructor.avgResponseTime != 0):
				score = score / math.log(instructor.avgResponseTime)
			if (instructor.name in postSimilarities):
				score = score * (1 - postSimilarities[instructor.name])
			if (instructor.name in endorsementValues):
				score = score * (1 + endorsementValues[instructor.name])
			scores[instructor.name] = score
		scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
		for name, value in scores:
			print(str(name) + ' (' + '%.2f' % value + ')')

#Following code snippet from https://stackoverflow.com/questions/753052/strip-html-from-strings-in-python:

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()