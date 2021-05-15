class Instructor:
	def __init__(self, uid, course):
		self.uid = uid
		self.profile = course.get_users([uid])
		self.name = self.profile[0]['name']
		self.imgUrl = self.profile[0]['photo_url']
		self.responseCount = 0
		self.responses = []
		self.totalResponseTime = 0
		self.avgResponseTime = 0
		self.totalResponseLength = 0
		self.avgResponseLength = 0
		self.totalThanksTags = 0
		self.avgThanksTags = 0
		
	#log new response for instructor
	def addResponse(self, content, thanks):
		self.responses.append(content)
		self.responseCount += 1
		self.totalThanksTags += thanks
		self.totalResponseLength += len(content)
		self.avgThanksTags = self.totalThanksTags / self.responseCount
		self.avgResponseLength = self.totalResponseLength / self.responseCount
		self.avgResponseTime = self.totalResponseTime / self.responseCount

	def logResponseTime(self, time):
		self.totalResponseTime += time

	def getName(self):
		return self.name

	def getPosts(self):
		return self.responses

	def __str__(self):
		return str(self.name) + " (" + str(self.responseCount) + ") - " + "(" + str(self.totalThanksTags) + ")" + " avg. time - " + str(self.avgResponseTime)