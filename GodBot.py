from discord.ext import commands
import shlex
import re

"""
!when [author, message] [equal, match, startswith, endswith]
		"filter_parameter" [send, delete, react] "action_parameter"
"""

class HandleMessage(commands.Cog):
	"""
	This class is used by GodBot() to handle messages and commands from users

	"""
	compare_funcs = {
		'equal': str.__eq__,
		'match': str.__contains__,
		'startswith': str.startswith,
		'endswith': str.endswith
	}

	authorized_words = {
		1: ['author', 'message'],
		2: ['equal', 'match', 'startswith', 'endswith'],
		4: ['send', 'delete', 'react']
	}

	def __init__(self, bot):
		self.bot = bot
		self.conditions = []
		self.actions = []

	@staticmethod
	def is_condition_true(condition, message):
		for subject in condition[0]:
			msg_content = message.author if subject == 'author' else message.content
			for cmp_f in condition[1]:
				cmp_func = HandleMessage.compare_funcs[cmp_f]
				if cmp_func(str(msg_content), str(condition[2])) == False:
					return False
		return True

	@staticmethod
	async def execute_action(actionList, message):
		deleted = False
		for action in actionList[0]:
			if action == 'send':
				await message.channel.send(actionList[1])
			elif action == 'delete' and deleted == False:
				deleted = True
				await message.delete()
			elif action == 'react' and deleted == False:
				await message.add_reaction(actionList[1])

	@staticmethod
	def check_and_between_words(words, authorized_list):
		for word, i in zip(words, range(len(words))):
			if word in authorized_list and i % 2 == 0:
				pass
			elif word == '&' and i % 2 == 1 and i < len(words)-1:
				pass
			else:
				return []
		return list(filter(lambda a: a != '&', words))

	@staticmethod
	def split_instructions(instructions):
		for i in [1, 2, 4]:
			if instructions[i].startswith('('):
				instructions[i] = instructions[i][1:-1]
			instructions[i] = shlex.split(instructions[i])
			instructions[i] = HandleMessage.check_and_between_words(instructions[i], HandleMessage.authorized_words[i])
		for i in [3, 5]:
			if len(instructions) > i and instructions[i].startswith('"'):
				instructions[i] = instructions[i][1:-1]
		return instructions

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author == self.bot.user:
			return
		for condition, action in zip(self.conditions, self.actions):
			if (HandleMessage.is_condition_true(condition, message)):
				await HandleMessage.execute_action(action, message)

	@commands.command("when")
	async def when(self, ctx):
		instruction_list = re.findall('\[[^\]]*\]|\([^\)]*\)|\"[^\"]*\"|\S+', ctx.message.content)
		if len(instruction_list) < 5:
			return
		instruction_list = HandleMessage.split_instructions(instruction_list)
		if len(instruction_list[1]) >= 1:
			condition = [instruction_list[1]]
			if len(instruction_list[2]) >= 1:
				condition.extend([instruction_list[2], instruction_list[3]])
				if len(instruction_list[4]) >= 1:
					self.conditions.append(condition)
					self.actions.append([instruction_list[4], instruction_list[5]])
					print(self.conditions)
					print(self.actions)

class GodBot(commands.Bot):
	"""
	This class contain everything related to the bot initialisation
	Just create an instance of this class and call start_bot() to start the bot.
	"""
	def __init__(self):
		super().__init__(command_prefix="!")
		self.bot_token = "NzQ1NjA4OTExNDkwMzgzOTQz.Xz0QaQ.uTKHwBlmaLy32fcDQItfRARCK9E"
		self.add_cog(HandleMessage(self))

	def start_bot(self):
		self.run(self.bot_token)

x = GodBot()
x.start_bot()