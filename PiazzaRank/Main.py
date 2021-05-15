from PiazzaBot import PiazzaBot
from Instructor import Instructor
from Algorithms import Algorithms

print('\n----------------Welcome to InstructorRank!----------------\n')

piazza = PiazzaBot()
courses = piazza.getClasses()

cont = True

while cont:
    print('Course List:')

    for i in range(0, len(courses)):
        print('(' + str(i + 1) + ') ' + courses[i]['name'])

    course = None
    while course is None:
        print('\nWhich course would you like to analyze? Enter the number next to the course from above:')
        courseIndex = int(input())
        try:
            course = courses[courseIndex - 1]
        except IndexError:
            print('Invalid Course!')

    print('\nWould you like to limit the number of posts to analyze? This is recommended for courses with thousands of posts. (Y/N)')
    shoudLimit = input()
    limit = None

    if shoudLimit.upper() == 'Y':
        print('How many posts would you like to be analyzed? Enter a number.')
        limit = int(input())

    print('\nGetting posts for ' + str(course['name']) + '...\n')

    if limit is None:
        piazza.getData(course['nid'])
    else:
        piazza.getData(course['nid'], limit=limit)

    print('\nAnalyze another course? (Y/N)')
    resp = input()

    if resp.upper() == 'N':
        print('\nThanks for using InstructorRank!')
        cont = False
    else:
        print('\n')