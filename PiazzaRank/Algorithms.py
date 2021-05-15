from collections import defaultdict
import re
import math

class Algorithms():
    #conduct PageRank on given graph (adjacency matrix), returns PageRank values 
    def pageRank(self, endorsementGraph):

        epsilon = 0.2
        numInstructors = len(endorsementGraph.keys())

        transitionMatrix = defaultdict(dict)
        for instructorRow in endorsementGraph.keys():
            endorsementGraph[instructorRow][instructorRow] = 1
            for instructorCol in endorsementGraph.keys():
                transitionMatrix[instructorRow][instructorCol] = epsilon / numInstructors
                if (instructorCol in endorsementGraph[instructorRow] and endorsementGraph[instructorRow][instructorCol] != 0):
                    outdegree = 0
                    for value in (endorsementGraph[instructorRow]).values():
                        outdegree += value
                    transitionMatrix[instructorRow][instructorCol] = (1 - epsilon) * (endorsementGraph[instructorRow][instructorCol] / outdegree) + epsilon / numInstructors

        x = {}
        for instructor in endorsementGraph.keys():
            x[instructor] = 0
        x[list(endorsementGraph.keys())[0]] = 1

        while (x != self.matrixMultiply(x, transitionMatrix)):
            x = self.matrixMultiply(x, transitionMatrix)

        return x


    def matrixMultiply(self, x, transition):
        product = {}
        for i in x.keys():
            temp = 0
            for j in x.keys():
                temp += x[j] * transition[j][i]
            product[i] = temp
        return product
		
	#finds average cosine similarity of list of responses
    def cosineSimilarityPosts(self, posts):
        documentFrequency = {}
        termFrequencies = {}

        for post in posts:
            termFrequency = {}
            words = post.split()
            for word in words:
                filteredWord = re.sub('[^A-Za-z0-9]+', '', word).lower()

                if filteredWord in termFrequency:
                    termFrequency[filteredWord] = termFrequency[filteredWord] + 1
                else:
                    termFrequency[filteredWord] = 1

            termFrequencies[post] = termFrequency

            for word in termFrequency.keys():
                if word in documentFrequency:
                    documentFrequency[word] = documentFrequency[word] + 1
                else:
                    documentFrequency[word] = 1

        weightVectors = {}

        for post in posts:
            weightVector = {}
            for word in documentFrequency:
                weight = 0
                if word in termFrequencies[post]:
                    weight = termFrequencies[post][word] * math.log((len(posts) / documentFrequency[word]), 10)
                weightVector[word] = weight
            weightVectors[post] = weightVector

        totalCosineSimilarity = 0
        numCosineSimilarities = 0

        for i in range(len(posts)):
            for j in range(i + 1, len(posts)):
                dotProduct = 0
                iMagnitude = 0
                jMagnitude = 0
                for key in weightVectors[posts[i]]:
                    dotProduct += weightVectors[posts[i]][key] * weightVectors[posts[j]][key]
                    iMagnitude += weightVectors[posts[i]][key] ** 2
                    jMagnitude += weightVectors[posts[j]][key] ** 2
                
                iMagnitude = math.sqrt(iMagnitude)
                jMagnitude = math.sqrt(jMagnitude)

                cosineSimilarity = 0

                if (iMagnitude * jMagnitude != 0):
                    cosineSimilarity = dotProduct / (iMagnitude * jMagnitude)

                totalCosineSimilarity += cosineSimilarity
                numCosineSimilarities += 1

        avgCosineSimilarity = 0
        if (numCosineSimilarities != 0):
            avgCosineSimilarity = totalCosineSimilarity / numCosineSimilarities
        
        return avgCosineSimilarity