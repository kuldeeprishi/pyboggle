import random
from urllib.request import urlopen
import copy
import datetime

from exceptions import BoggleException

LETTERS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'qu', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']


MIN_BOARD_SIZE = 4
MAX_BOARD_SIZE = 16

DICTIONARY_ENDPOINT = "http://dml.cs.byu.edu/~sburton/cs235/projects/boggle/dictionary.txt"

class Boggle:
    def __init__(self, size=4, letters=LETTERS):
        """
        Initialize a boggle board with given size and a custom points table if
        provided
        """
        self.board = []
        assert MIN_BOARD_SIZE <= size <= MAX_BOARD_SIZE, "Invalid Board Size"
        self.size = size
        self.letters = letters

        self.words, self.prefixes = self.load_dictionary()
        self.adjacency = self.build_adjacency()
        self.initialize_board()
        while not self.find_all_words():
            self.initialize_board()


    def __repr__(self):
        """
        Prints the Boggle board

        :return: A string representation of the board
        """
        return '\n'.join([' '.join(row) for row in self.board])

    def build_adjacency(self):
        """
        Builds the adjacency lookup for each position on the board

        :return: A dictionary of adjacent positions for each position on the board
        """
        adjacency = dict()
        for row in range(0, self.size):
            for col in range(0, self.size):
                adjacency[(row, col)] = self.adjacent((row, col))
        return adjacency

    def adjacent(self, pos):
        """
        Finds all adjacent positions for a given position on the board

        :param pos: A 2-tuple giving row and column of a position
        :return: A list of positions adjacent to the given position
        """
        row, col = pos
        adj = []
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                new_row = row + i
                new_col = col + j
                if 0 <= new_row < self.size and 0 <= new_col < self.size and not (i == j == 0):
                    adj.append((new_row, new_col))
        return adj


    def load_dictionary(self):
        """
        Loads a dictionary file into Boggle object's word list

        :param name: Path to the dictionary file
        :return: None
        """
        words = set()
        prefixes = set()
        response = urlopen(DICTIONARY_ENDPOINT)

        if response.status != 200:
            raise BoggleException('Failed to load dictionary.')

        dictionary_words = response.read().decode().split('\n')

        for entry in dictionary_words:
            word = entry.strip()
            if len(word) >= self.size:
                words.add(word)
                for i in range(len(word)):
                    prefixes.add(word[:i])

        return words, prefixes


    def initialize_board(self):
        """
        Initialize a board with random letters

        :return: None
        """
        self.board = []
        for row in range(0, self.size):
            self.board.append([])
            for col in range(0, self.size):
                self.board[row].append(random.choice(LETTERS))

    def get_letter(self, pos):
        """
        Gets the letter at a given position

        :param pos: A 2-tuple giving row and column location of a position
        :return: A letter at the given position
        """
        return self.board[pos[0]][pos[1]]

    def find_all_words(self):
        """
        Finds all words on the board

        :return: A set of words found on the board
        """
        words = set()
        for row in range(self.size):
            for col in range(self.size):
                words |= self.find_words_pos((row, col))
        return words

    def find_words_pos(self, pos):
        """
        Finds words starting at a given position on the board

        :param pos: A 2-tuple giving row and column on the board
        :return: A set of words starting at the given position
        """
        stack = [(n, [pos], self.get_letter(pos)) for n in self.adjacency[pos]]
        words = set()
        while stack:
            curr, path, chars = stack.pop()
            curr_char = self.get_letter(curr)
            curr_chars = chars + curr_char

            # Check if path forms a word
            if curr_chars in self.words:
                words.add(curr_chars)

            # Check if path forms the prefix of a word
            if curr_chars in self.prefixes:
                # Get adjacent positions
                curr_adj = self.adjacency[curr]

                # Check if adjacent positions have already been visited
                stack.extend([(n, path + [curr], curr_chars) for n in curr_adj if n not in path])
        return words

    def get_word_point(self, word):
        word_len  = len(word)
        if word_len >= 8:
            return 11
        elif word_len >= 7:
            return 5
        elif word_len >= 6:
            return 3
        elif word_len >= 5:
            return 2
        elif word_len >= 3:
            return 1
        return 0

    def get_score(self, words):
        all_possible_words = self.find_all_words()
        correct_answers = all_possible_words.intersection(words)

        score = sum([self.get_word_point(word) for word in correct_answers])
        return score




if __name__ == "__main__":
    try:
        print("""
        Welcome to the Boggle Game!!!
        More Info about the game is available at: https://en.wikipedia.org/wiki/Boggle

        Use Ctrl-C to exit at any time during the game
        """)
        size = None
        while not size:
            try:
                print(f"Please select a board size between {MIN_BOARD_SIZE} and {MAX_BOARD_SIZE} !!!")
                size = int(input())

                print("Please wait while the board is Initializing...")
                board = Boggle(size)

                print('Your board is ready!')
                print('Try to find all words in following board.')
                print('Enter multiple words seperated by comma')
                possible_words = len(board.find_all_words())
                print(f'HINT: There is/are {possible_words} hidden word(s) in this board.')
                print(board)
                start_time = datetime.datetime.now()
                print()
                words = set(input().split(', '))
                end_time = datetime.datetime.now()
                print(f"Your submission: {words}")

                score = board.get_score(words)
                print(f"YOU SCORED: {score}")

                words_in_board = board.find_all_words()
                print(f"You missed these: {words_in_board}")
                time_taken = (end_time - start_time).seconds
                print(f"You took {time_taken} sec to solve")
                print("Let's do better this time..")

            except (ValueError, AssertionError):
                print("That's not an expected value. Please try again!")
            size = None

    except KeyboardInterrupt:
        print("Thanks for playing today! Have a great day")

