![header image](https://raw.githubusercontent.com/raunaqsingh2020/PiazzaRank/master/banner.png)

# PiazzaRank

> With great power, comes great responsibility - Voltaire

Grading TAs/Instructors based off of their activity on Piazza!

The program gets the posts for a specific course (which the user provides) and then records the following statistics for each TA- number of responses, the actual contents of the responses, the total and average response times, the total and average response lengths (characters), and lastly, the total and average number of 'Thanks!' they received on Piazza. I then calculated cosine similarities of responses for each TA and conducted a modified PageRank algorithm on the TAs. Finally, I constructed a simple formula which used all of these metrics in order to give the TAs scores for their Piazza performance.
