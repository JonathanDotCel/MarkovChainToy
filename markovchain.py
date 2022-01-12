#py 3
# run me

import os

import sourcetext_frost
import sourcetext_poe
import sourcetext_test
import ParseClass

#
# Snippets of code to play with
#

# The 2nd most popular word should be about 1/2 as
# common as the first, etc given enough text
def Test_ZipfLaw():
    
    print( stats.InitialWordProbability("the") )
    
    print( stats.InitialWordProbability("of") )
    
    print( stats.InitialWordProbability("and") )
    
    print( stats.InitialWordProbability("to") )

    print( stats.InitialWordProbability("a") )

    print( stats.InitialWordProbability("cat") )
    
#
# Do the thing
#
stats: ParseClass.WordStats = ParseClass.Parser.PrepareText(sourcetext_poe.lines)

# Dump a quick word count to screen
stats.PrintStats()

#
# assert that it's a proper stochastic matrix
#

# Sum of first cols
firstCol = [thing[0] for thing in stats.matrix]
firstColSum = sum( firstCol )

firstRow = stats.matrix[0]
firstRowSum = sum(firstRow)

#assert firstColSum == 1
#assert firstRowSum == 1

# Example: probability of a transition between two given words
#prob = stats.GetProb( stats.IndexOfWord("the"), stats.IndexOfWord("one") )
#print( "prob {}".format( prob ) )

# Example: get the most probable next word for any given word
#          see implementation for weight details
#nextMostLikely = stats.GetMostLikelyNextWord(stats.IndexOfWord( "so" ) )
#print( "next most likely = {}".format( nextMostLikely ) )

# Pick a start word and let's go
count = 205
nextWord = "one"
print( nextWord )
for thing in range( count ):
    nextMostLikely = stats.GetMostLikelyNextWord(stats.IndexOfWord( nextWord ) )
    print( "next most likely = {}".format( nextMostLikely ) )
    nextWord = nextMostLikely



