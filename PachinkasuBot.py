import discord, csv, datetime, math, conf, PachinkasuBotPrivateCmd
from discord.ext import commands

channelId = int(conf.CHANNEL_ID)
prefix = "!"
version = "2.0.8"

def convertRemainTime(time: int) -> str:
	if time >= (60 * 60 * 24):
		day = math.floor(time / (60 * 60 * 24))
		rem = time % (60 * 60 * 24)
		
		hour = math.floor(rem / (60 * 60))
		rem = rem % (60 * 60)

		minute = math.floor(rem / 60)
		rem = rem % 60

		return str(day) + " 日 " + str(hour) + " 時間 " + str(minute) + " 分 " + str(rem) + " 秒"
	elif time >= (60 * 60):
		hour = math.floor(time / (60 * 60))
		rem = rem % (60 * 60)

		minute = math.floor(rem / 60)
		rem = rem % 60

		return str(hour) + " 時間 " + str(minute) + " 分 " + str(rem) + " 秒"
	elif time >= 60:
		minute = math.floor(time / 60)
		rem = rem % 60

		return str(minute) + " 分 " + str(rem) + " 秒"
	else:
		return str(time) + " 秒"

class PachinkasuBot(commands.Cog):
	def __init__(self, bot: commands.Bot):
		super().__init__()
		self.bot = bot

		self.bot.add_cog(PachinkasuBotMainApp(self.bot))
		self.bot.add_cog(PachinkasuBotPrivateCmd.PachinkasuBotPrivateCmd(self.bot))

class PachinkasuBotHelp(commands.DefaultHelpCommand):
	def __init__(self):
		super().__init__()
		self.commands_heading = "こまんど: "
		self.no_category = "そのほか"
		self.command_attrs["help"] = "すべてのこまんどをひょーじする！"

	def get_ending_note(self):
		return (
			f"それぞれのこまんどのせつめい: {prefix}help <こまんどめい>\n"
			f"それぞれのかてごりのせつめい: {prefix}help <かてごりめい>\n"
		)

class PachinkasuBotMainApp(commands.Cog):
	def __init__(self, bot: commands.Bot):
		super().__init__()
		self.bot = bot
	
	@commands.Cog.listener()
	async def on_ready(self):
		print(bot.user.display_name+": Bot is ready!")
		ch: discord.TextChannel = bot.get_channel(channelId)
		# await ch.send(f"{bot.user.mention}: Bot is ready!")
	
	@commands.command()
	async def version(self, ctx: discord.Message):
		await ctx.reply("PachinkasuBot version "+version)
	
	@commands.command()
	async def keiba(self, ctx: discord.Message, mode: str = None, *args: str):
		""" 重賞レースの詳細を表示するだけ """
		try:
			cmd = mode

			if cmd is None:
				cmd = "next"
			
			with open("./keiba_schedules.csv", "r") as fp:
				
				keibaSchedules = csv.reader(fp, delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
				header = next(keibaSchedules)

				if cmd == "next":
					if None is None: # Shinjiro Koizumi
						pass # やろうとした事を忘れて残ったデッドスペース的な何か
					
					raceFilter = {
						"grade": None,
						"location": None,
						"courseType": None
					}
					sep = False
					output = ""
					nextRace = None
					for arg in args:
						if arg.lower().startswith("grade:"):
							filter = arg.replace("grade:", "").lower()

							if filter == "g1":
								raceFilter["grade"] = "G1"
							elif filter == "g2":
								raceFilter["grade"] = "G2"
							elif filter == "g3":
								raceFilter["grade"] = "G3"
							elif filter == "j-g1":
								raceFilter["grade"] = "J-G1"
							elif filter == "j-g2":
								raceFilter["grade"] = "J-G2"
							elif filter == "j-g3":
								raceFilter["grade"] = "J-G3"
							else:
								output += "Warning: クラスフィルタが正しい値ではありません(gradeフィルタは無効化されています)!\n"
								sep = True
						
						if arg.lower().startswith("location:"):
							filter = arg.replace("location:", "").lower()

							if filter == "sapporo":
								raceFilter["location"] = "札幌"
							elif filter == "hakodate":
								raceFilter["location"] = "函館"
							elif filter == "fukushima":
								raceFilter["location"] = "福島"
							elif filter == "nakayama":
								raceFilter["location"] = "中山"
							elif filter == "tokyo":
								raceFilter["location"] = "東京"
							elif filter == "niigata":
								raceFilter["location"] = "新潟"
							elif filter == "chukyo":
								raceFilter["location"] = "中京"
							elif filter == "kyoto":
								raceFilter["location"] = "京都"
							elif filter == "hanshin":
								raceFilter["location"] = "阪神"
							elif filter == "kokura":
								raceFilter["location"] = "小倉"
							else:
								output += "Warning: 競馬場フィルタが正しい値ではありません(locationフィルタは無効化されています)!\n"
								sep = True
						
						if arg.lower().startswith("type:"):
							filter = arg.replace("type:", "").lower()

							if filter == "turf":
								raceFilter["courseType"] = "芝"
							elif filter == "dirt":
								raceFilter["courseType"] = "ダート"
							elif filter == "obstacle":
								raceFilter["courseType"] = "障害"
							else:
								output += "Warning: 馬場特性フィルタが正しい値ではありません(typeフィルタは無効化されています)!\n"
								sep = True
					nowTimestamp = int(datetime.datetime.now().timestamp())

					if raceFilter["grade"] is not None:
						newRow = []
						for row in keibaSchedules:
							if row[8] == raceFilter["grade"]:
								newRow.append(row)
							elif raceFilter["courseType"] == "障害" and raceFilter["grade"] in row[8]:
								newRow.append(row)
						keibaSchedules = newRow
						output += "クラスフィルタ: " + raceFilter["grade"] + "\n"
						sep = True

					if raceFilter["location"] is not None:
						newRow = []
						for row in keibaSchedules:
							if row[3] == raceFilter["location"]:
								newRow.append(row)
						keibaSchedules = newRow
						output += "競馬場フィルタ: " + raceFilter["location"] + "\n"
						sep = True
					
					if raceFilter["courseType"] is not None:
						newRow = []
						for row in keibaSchedules:
							if row[4] == raceFilter["courseType"]:
								newRow.append(row)
						keibaSchedules = newRow
						output += "馬場特性フィルタ: " + raceFilter["courseType"] + "\n"
						sep = True

					for row in keibaSchedules:
						raceTimestamp = int(datetime.datetime.strptime(row[0], "%Y/%m/%d %H:%M").timestamp())
						if nowTimestamp < raceTimestamp:
							nextRace = row
							break
						
					if nextRace is not None:
						try:
							date, count, title, location, courseType, distanceCategory, distance, raceNumber, grade = nextRace
						except IndexError:
							pass
						
						if sep:
							output += "----------\n"
						output += "次のレース:\n"
						if count != "":
							output += "第" + str(count) + "回 "
						output += title + " (" + grade.replace("1", "Ⅰ").replace("2", "Ⅱ").replace("3", "Ⅲ") + ") " + location + " "
						if raceNumber != "":
							output += "第" + str(raceNumber) + "R"
						output += " " + courseType + " " + distance + "m"
						if distanceCategory != "- - -":
							output += " (" + distanceCategory + ")\n"
						else:
							output += "\n"
						output += "出走まで あと " + convertRemainTime(raceTimestamp - nowTimestamp) + " (" + date + ")"

						await ctx.reply(output)
					else:
						await ctx.reply("次のレースはありません。")
		except IndexError:
			pass

	@commands.command()
	async def sayHello(self, ctx: discord.Message, target: discord.Member):
		""" メンションで挨拶するだけ """
		await ctx.reply(f"Hello, {target.mention}!")
		return

	@commands.command()
	async def sayGoodbye(self, ctx: discord.Message, target: discord.Member):
		""" メンションで挨拶するだけ """
		await ctx.reply(f"Goodbye, {target.mention}!")
		return

	@commands.command()
	async def fucks(self, ctx: discord.Message):
		""" Everybody, say \"FAX\"!!! """
		await ctx.reply("FAX")
		return

	@commands.command()
	async def carnival(self, ctx: discord.Message):
		""" おちんぽびんびんカーニバル """
		await ctx.reply(file=discord.File("./images/a2834bef3d470f02.jpg"))
		return

	@commands.command()
	async def chinchinland(self, ctx: discord.Message, param):
		""" ちんちんランドコントローラー """
		try:
			opt = param
		except NameError:
			opt = "open"
		
		if opt == "open":
			await ctx.reply(file=discord.File("./images/kogusoku-2018-04-01_03-22-17_914645.jpg"))
		elif opt == "close":
			await ctx.reply(file=discord.File("./images/ER2TZnhU4AAdVnW.jpg"))
		elif opt == "toggle":
			await ctx.reply(file=discord.File("./images/kogusoku_15153333.jpg"))
		else:
			await ctx.reply("第1引数は `open`, `close`, `toggle` のいずれかで指定してください！")
		return

	@commands.command()
	async def paradise(self, ctx: discord.Message, param):
		""" いわゆる \"失楽園\" """
		try:
			opt = param
		except IndexError:
			opt = "mechashiko"
		
		if opt == "mechashiko":
			await ctx.reply(file=discord.File("./images/20170803152915.jpg"))
		elif opt == "chunithm":
			await ctx.reply(file=discord.File("./images/chunithm-paradise_02.jpg"))
		elif opt == "lost":
			await ctx.reply(file=discord.File("./images/paradiseLost.jpg"))
		else:
			await ctx.reply("第1引数は `mechashiko`, `chunithm`, `lost` のいずれかで指定してください！")
		return

	@commands.command(name="3150")
	async def com_3150(self, ctx: discord.Message):
		""" 気分がいい時に使いましょう """
		await ctx.reply(file=discord.File("./images/shirou-t-4.jpg"))
		return

	@commands.command(name="810")
	async def com_3150(self, ctx: discord.Message):
		""" インタビュアー「じゃあ、オナニーとか、っていうのは?」？？？:「やりますねぇ！」 """
		await ctx.reply(file=discord.File("./images/810.jpg"))
		return

	@commands.command()
	async def pachinko(self, ctx: discord.Message):
		""" みんな大好きシンホギア """
		await ctx.reply(file=discord.File("./images/D_YqTm2UcAAcCDf.jpg"))
		return

	@commands.command()
	async def chinko(self, ctx: discord.Message):
		""" キモすぎ海綿体 """
		await ctx.reply(file=discord.File("./images/IMG_20200212_193304.png"))
		return

	@commands.command()
	async def doshitan(self, ctx: discord.Message):
		""" 困ったとき、悩みがあるとき、いつでも呼び出してください。 """
		await ctx.reply(file=discord.File("./images/E_oFbZsUUAY3YE5.jpg"))
		await ctx.reply(
			"あなたの一言で、救える命がある。\n"
			"\n"
			"子供のSOS相談窓口 (文部科学省):\n"
			"電話: 0120-0-78310\n"
			"ホームページ: https://www.mext.go.jp/a_menu/shotou/seitoshidou/06112210.htm\n"
			"\n"
			"児童相談所虐待対応ダイヤル (厚生労働省):\n"
			"電話(局番なし): 189\n"
			"ホームページ: https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kodomo/kodomo_kosodate/dial_189.html\n"
			"\n"
			"子どもの人権110番 (法務省):\n"
			"電話: 0120-007-110\n"
			"ホームページ: https://www.moj.go.jp/JINKEN/jinken112.html\n"
		)
		return

	@commands.command()
	async def saimu(self, ctx: discord.Message):
		""" 救いの手 """
		await ctx.reply("法律事務所 ホームワン: https://www.saimu110.info/")
		return

	@commands.command()
	async def atom(self, ctx: discord.Message):
		""" \ｱﾄﾑﾎｳﾘﾂｼﾞﾑｼｮ/ """
		await ctx.reply("アトム法律事務所弁護士法人グループ: https://www.atomfirm.com/")
		return
	
	@commands.command()
	async def shots(self, ctx: discord.Message):
		""" パリピになれるよ """
		await ctx.reply(
			"Shots shots shots shots shots\n"
			"Shots shots shots shots shots\n"
			"Shots shots shots shots shots\n"
			"Shots, everybody\n"
			"Shots shots shots shots shots\n"
			"Shots shots shots shots shots\n"
			"Shots shots shots shots shots\n"
			"Shots, everybody\n"
			"\n"
			"https://www.youtube.com/watch?v=XNtTEibFvlQ"
		)
	
	@commands.command()
	@commands.is_owner()
	async def logout(self, ctx: discord.Message):
		""" ログアウトと再起動 """
		await ctx.reply("\N{WAVING HAND SIGN}")
		await bot.close()

bot = commands.Bot(command_prefix=prefix, help_command=PachinkasuBotHelp())
bot.add_cog(PachinkasuBot(bot=bot))

bot.run(conf.TOKEN)
