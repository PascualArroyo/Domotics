class Utils:

	def convert(self, pipe):
		vector = []
		vector.append(int("0x"+pipe[0:2], 16))
		vector.append(int("0x"+pipe[2:4], 16))
		vector.append(int("0x"+pipe[4:6], 16))
		vector.append(int("0x"+pipe[6:8], 16))
		vector.append(int("0x"+pipe[8:10], 16))

		return vector
        