from __future__ import print_function

import random
import copy
import Image


class Board:
	def __init__(self, size, mask):

		self.size = size

		self.words = []

		self.cells = [['.' for _ in range(size[0])] for _ in range(size[1])]

		self.mask = mask

	def placeWord(self, word, start, direction):

		start_x, start_y = start

		# check if all the positions are either free or compatible
		changes = []
		for i_ch, ch in enumerate(word):
			x, y = 0, 0

			if direction == "down":
				x = start_x
				y = start_y + i_ch
			elif direction == "up":
				x = start_x
				y = start_y - i_ch
			elif direction == "right":
				x = start_x + i_ch
				y = start_y
			elif direction == "left":
				x = start_x - i_ch
				y = start_y
			elif direction == "down-right":
				x = start_x + i_ch
				y = start_y + i_ch
			elif direction == "down-left":
				x = start_x - i_ch
				y = start_y + i_ch
			elif direction == "up-right":
				x = start_x + i_ch
				y = start_y - i_ch
			elif direction == "up-left":
				x = start_x - i_ch
				y = start_y - i_ch

			changes.append((x, y, ch))

			cur_char = self.cells[y][x]



			# catch invalid position
			if not self.mask[(x, y)]:
				return False

			if cur_char != '.' and cur_char != ch:
				return False

		# if we get to this point, the word is good to be placed
		#    and we can apply the changes
		for (x, y, ch) in changes:
			self.cells[y][x] = ch

		self.words.append(word)

		return True

	def replaceEmptyCells(self):
		for i_y in range(self.size[1]):
			for i_x in range(self.size[0]):
				ch = self.cells[i_y][i_x]

				if ch == '.':
					self.cells[i_y][i_x] = random.choice('abcdefghijklmnopqrstuvwxyz ')
			


	def __str__(self):
		string = ""

		cleaned_cells = []

		for i_y in range(self.size[1]):
			new_row = []
			for i_x in range(self.size[0]):

				if not self.mask[(i_x, i_y)]:
					new_row.append(' ')
				else:
					new_row.append(self.cells[i_y][i_x])
			cleaned_cells.append(new_row)

		for row in cleaned_cells:

			string += "\t".join(row) + '\n'

		# add word list
		max_word_len = max([len(w) for w in self.words])

		for i_w, word in enumerate(sorted(self.words)):
			if i_w % 4 == 0:
				string += '\n'

			string += word+'\t\t\t\t\t'

		string = string.upper()


		return string


def generateBoard(size, vocab, mask):

	max_restart = 150

	need_to_restart = True

	trial_num = 0
	while need_to_restart and trial_num < max_restart:
		print("Trial:", trial_num)
		trial_num += 1
		board = Board(size, mask)

		# iterate through the words to try fit them all in

		worked = False

		for word in vocab:
			# need to reset worked to False
			worked = False

			attempts = 0

			while not worked and attempts < 10000:
				attempts += 1

				# pick random location to place it
				direction = random.choice(['up', 'down', 'left', 'right', 
											'up-left', 'up-right', 'down-left', 'down-right'])

				word_len = len(word)

				start_x, start_y = 0, 0

				if direction == 'down':
					# nb: randint range is inclusive, so need to subtract one when converting to list index
					start_x = random.randint(0, size[0]-1)
					start_y = random.randint(0, size[1]-word_len)
				elif direction == 'up':
					start_x = random.randint(0, size[0]-1)
					start_y = random.randint(word_len-1, size[1]-1)
				elif direction == 'right':
					start_x = random.randint(0, size[0]-word_len)
					start_y = random.randint(0, size[1]-1)
				elif direction == 'left':
					start_x = random.randint(word_len-1, size[0]-1)
					start_y = random.randint(0, size[1]-1)
				elif direction == 'down-right':
					start_x = random.randint(0, size[0]-word_len)
					start_y = random.randint(0, size[1]-word_len)
				elif direction == 'down-left':
					start_x = random.randint(word_len-1, size[0]-1)
					start_y = random.randint(0, size[1]-word_len)
				elif direction == 'up-right':
					start_x = random.randint(0, size[0]-word_len)
					start_y = random.randint(word_len-1, size[1]-1)
				elif direction == 'up-left':
					start_x = random.randint(word_len-1, size[0]-1)
					start_y = random.randint(word_len-1, size[1]-1)


				worked = board.placeWord(word, (start_x, start_y), direction)

			# if we absolutely couldn't fit the word, start over
			if not worked:
				break

		if worked:
			need_to_restart = False

	if need_to_restart:
		print("Could not fit all words onto board...")
		print("Try decreasing number of words, changing mask, or increasing board size.")
		return None
	else:
		print("Done!")
		board.replaceEmptyCells()
		return board


def extractMask(mask_filename, grid_size):
	mask = dict() # map from position to boolean (usable or not)
	mask_img = Image.open(mask_filename).convert('RGB').resize(grid_size)
	pix = mask_img.load()
	for x in range(mask_img.size[0]):
		for y in range(mask_img.size[1]):
			c = pix[x,y]
			if sum(c[:3]) <= 200*3:
				mask[(x, y)] = True
			else:
				mask[(x, y)] = False

	return mask

def getVocab(vocab_filename, vocab_size):

	with open(vocab_filename, 'r') as f:
		vocab = f.read().lower().split('\n')

	vocab = vocab[:vocab_size]

	return vocab



print("meow")

modes = dict()

modes['normal'] = {
	"vocab_filename": 'vocabs/large_vocab.txt',
	"mask_filename": "masks/normal.png",
	"vocab_size": 50,
	"grid_size": (25, 25)
}

modes['round'] = {
	"vocab_filename": 'vocabs/round_vocab.txt',
	"mask_filename": "masks/round.png",
	"vocab_size": 30,
	"grid_size": (21, 21)
}

modes['farming'] = {
	"vocab_filename": 'vocabs/farm_vocab.txt',
	"mask_filename": "masks/corn.png",
	"vocab_size": 23,
	"grid_size": (28, 28)
}

modes['fishing'] = {
	"vocab_filename": 'vocabs/fishing_vocab.txt',
	"mask_filename": "masks/fish.png",
	"vocab_size": 26,
	"grid_size": (18,18)
}

modes['cooking'] = {
	"vocab_filename": 'vocabs/cooking_vocab.txt',
	"mask_filename": "masks/bread.png",
	"vocab_size": 40,
	"grid_size": (28,28)
}

mode = modes['fishing']

mask = extractMask(mode['mask_filename'], mode['grid_size'])
vocab = getVocab(mode['vocab_filename'], mode['vocab_size'])


board = generateBoard(mode['grid_size'], vocab, mask)

print(board)
