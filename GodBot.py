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

	def __init__(self, bot):
		self.bot = bot
		self.conditions = []
		self.actions = []

	@staticmethod
	def is_condition_true(condition, message):
		msg_content = message.author if condition[0] == 'author' else message.content
		cmp_func = HandleMessage.compare_funcs[condition[1]]
		return cmp_func(str(msg_content), str(condition[2]))

	@staticmethod
	async def execute_action(bot, action, message):
		if action[0] == 'send':
			await message.channel.send(action[1])
		elif action[0] == 'delete':
			await message.delete()
		elif action[0] == 'react':
			await message.add_reaction(action[1])

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author == self.bot.user:
			return
		for condition, action in zip(self.conditions, self.actions):
			if (HandleMessage.is_condition_true(condition, message)):
				await HandleMessage.execute_action(self.bot, action, message)

	@commands.command("when")
	async def when(self, ctx):
		instruction_list = shlex.split(ctx.message.content)
		if len(instruction_list) < 5:
			return
		if instruction_list[1] in ['author', 'message']:
			condition = [instruction_list[1]]
			if instruction_list[2] in ['equal', 'match', 'startswith', 'endswith']:
				condition.extend([instruction_list[2], instruction_list[3]])
				if instruction_list[4] in ['send', 'delete', 'react']:
					if instruction_list[4] != 'delete' and len(instruction_list) >= 6:
						self.conditions.append(condition)
						self.actions.append([instruction_list[4], instruction_list[5]])
					elif instruction_list[4] == 'delete':
						self.conditions.append(condition)
						self.actions.append([instruction_list[4]])

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