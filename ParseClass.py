
# Regex for splittin stuff
import re

#
# Keeps a running count of words via AddWord()
# Then generates an "A" Matrix and pi init table
# via BuildAMatrix()
# Then you ask it things.
#
# Crap version of this: https://en.wikipedia.org/wiki/Markov_chain
#
class WordStats(object):

    def __init__(self) -> None:
        
        # Words are indexed in the order they're found
        # The following dicts use this index

        # words in the order we found them
        self._indexFromWord = dict()    # <string, int>
        self._wordFromIndex = dict()    # <int, string>

        # same as _wordCounts, but with indices
        self._indicesCounts = dict()    # <int, int>

        # popularity of a given word at the start
        self._initialStates = dict()    # <int, int>
        self._numWords = 0
        self._numUniqueWords = 0

        # All the text but with the words replaced
        # with their indices.
        # e.g. "the cat and the dog" = 0,1,2,0,3
        self.tokenised = []

        # The A matrix
        self.matrix = []

        self.didBuildMatrix = False

        # little thing to reduce pair repetition
        # e.g. transition (12->14)
        self.usedPairs = {}     #<int, int>

    # Add a word, do the thing
    def AddWord(self, inWord: str) -> None:

        self._numWords += 1

        # Do we have this already?
        # TODO: cache the keys() ref and stop pestering it
        keys = self._indexFromWord.keys()

        if inWord in keys:
            
            # Seen this before; find it & increment
            
            wordIndex = self._indexFromWord[inWord]
            self._indicesCounts[wordIndex] += 1

        else:
            
            # New word, give it an index, and
            # start recording stats
            
            wordIndex = len(self._indexFromWord) - 1

            self._indexFromWord[inWord] = wordIndex
            self._wordFromIndex[wordIndex] = inWord
            self._indicesCounts[wordIndex] = 1
            
            self._initialStates[wordIndex] = 0

            # Don't populate the matrix, but
            self.matrix.append([])

        # assuming the count is at least 1 at this point
        self._initialStates[wordIndex] = float(
            self._indicesCounts[wordIndex]) / float(self._numWords)

        self._numUniqueWords = len(self._indexFromWord)

        self.tokenised.append(wordIndex)

        # Could start building elements of the state transition
        # matrix here, but it's a bit of a faff because we don't
        # have the final array/list length yet, and I'm not that
        # bothered.

    def PrintStats(self) -> None:
        print("Total words: {}\n".format(self._numWords))
        print("Unique words: {}\n".format(self._numUniqueWords))

    # Probability of any given word
    def InitialWordProbability(self, inString: str) -> float:
        
        idx = self.IndexOfWord( inString )

        # TODO: cache that keys ref
        keys = [thing for thing in self._indicesCounts.keys()]

        if idx in keys:
            return self._initialStates[idx]
        else:
            return 0

    # "thing" in int out
    def IndexOfWord(self, inWord: str) -> int:

        keys = [thing for thing in self._indexFromWord.keys()]
        if inWord in keys:
            return self._indexFromWord[inWord]
        return -1

    # Int in, "thing" out
    def WordFromIndex(self, inIndex: int) -> str:

        keys = [thing for thing in self._wordFromIndex.keys()]
        if inIndex in keys:
            return self._wordFromIndex[inIndex]
        return None


    # Builds the "A" matrix from our data
    # Should probs be automatic
    def BuildAMatrix(self) -> None:

        M = self._numUniqueWords

        # Would be nice if I could assign this in a
        # much less fragmented way

        self.matrix = []
        for startWord in range(M):
            self.matrix.append([0] * M)

        # pythonese for an M-length array
        transitionsForWordIndex = [0] * M

        # Just count the ocurrences into the matrix
        # e.g. matrix[firstOne][secondOne]
        for i in range(len(self.tokenised) - 1):
            wordIndex = self.tokenised[i]
            nextWordIndex = self.tokenised[i+1]

            self.matrix[wordIndex][nextWordIndex] += 1

            transitionsForWordIndex[wordIndex] += 1

        # Check for mistakes
        # E.g. if a word didn't transition to anything
        for i in range(len(transitionsForWordIndex)):
            if transitionsForWordIndex[i] == 0:
                if i == len(self._wordFromIndex) - 1:
                    print("last word has no transitions... that's fine")
                else:
                    word = self.WordFromIndex(i)
                    raise Exception("But how?={}".format(word))

        # Then divide by the # of ocurrences for each
        # e.g. num("the cat") vs num("the")
        for i in range(M):

            # get all the transitions for word[i]
            transitions = self.matrix[i]

            for j in range(len(transitions)):
                trans = float(transitionsForWordIndex[i])
                if trans != 0:
                    transitions[j] /= trans
            
        # Done?
        self.didBuildMatrix = True

    # Probability of a word transitioning to another
    def GetProb(self, word1: int, word2: int) -> float:
        return self.matrix[word1][word2]
    
    # Given a word index, which word is most likely next
    # E.g. A(i,j)
    def GetMostLikelyNextWord(self, word1: int) -> str:

        self.usedPairs = self.usedPairs or {}
        
        highestProbIndex = 0
        highestProb = 0.0
        gotHighestProb = False
        
        # Find this word's transitions...
        transitions = self.matrix[word1]

        for i in range(len(transitions)):
            prob = transitions[i]

            # have we used this (i,j) transition before?
            # reduce to 1/2, 1/3, 1/4 etc
            if ( prob > highestProb ):
                key = (word1, i)
                # TODO: cache keys() ref, etc
                if ( key in self.usedPairs.keys() ):
                    prob *= 1 / (self.usedPairs[key] +1)

            # Most likely (or first thing we've found)
            if (prob > highestProb) or (not gotHighestProb):
                gotHighestProb = True
                highestProb = prob
                highestProbIndex = i

        # TODO: concise, descriptive errors
        if not gotHighestProb:
            raise Exception("Boohoo!")

        # Since tuples are hashable :)
        key = (word1,highestProbIndex)
        if ( key in self.usedPairs.keys() ):
            self.usedPairs[ key ] += 1
        else:
            self.usedPairs[ key ] = 1

        return self.WordFromIndex(highestProbIndex)

# Mostly just a static wrapper
class Parser(object):

    def __init__(self) -> None:
        print("Don't instantiate me!")
        pass

    @classmethod
    def ConditionWord(cls, inText: str) -> str:
        # fucking gross, but it mostly works:
        outVal = inText.encode("ASCII", "ignore")
        outVal = str(outVal, "utf-8")
        outVal = outVal.lower()
        return outVal

    @classmethod
    def PrepareText(cls, inText) -> WordStats:

        # Here we will use regex to split a string with five
        # delimiters Including the dot, comma, semicolon,
        # a hyphen, and space followed by any amount of extra whitespace.
        splitVars = re.split(r"[-;,.\s]\s*", inText)

        # Init
        returnStats = WordStats()

        # Add words
        print( "Parsing the text..." );
        for thing in splitVars:
            conditioned = Parser.ConditionWord(thing)
            if conditioned:
                returnStats.AddWord(conditioned)
        
        # Build matrix
        print( "Building the \"A\" matrix..." )
        returnStats.BuildAMatrix()
        
        return returnStats
