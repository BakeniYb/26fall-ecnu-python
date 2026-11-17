from time import sleep
from termcolor import colored
import random
from simpleeval import simple_eval, InvalidExpression, NameNotDefined, FunctionNotDefined
from snownlp import SnowNLP
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


'''
<Bakeni聊天系统>

包含7个Bot:
1-3 课上已实现的HelloBot、GreetingBot、FavoriteColorBot;
4 可无限循环的CalcBot;
5 可根据语句判断情感分数、并根据情绪推荐两首歌的EmotionBot;
6 《请查收你的明日订单》多结局悬疑微科幻文字冒险游戏StoryAdventureBot;
7 答案之书AnswerBookBot

改进点:
菜单式入口，可选择中文/英文两种bot提问语言（Bot6/7暂无），bot也会根据用户输入的是中文还是英文来用同样的语言回答;
CalcBot增加了反复执行功能，用户可以一直输入算术表达式求值，直到输入x/q/quit/exit为止;
同时整理了各种用户可能输入的符号的不同形式，每一种符号都转换成同一个形式表示，还增加了容错，提前拦截除以0等不合法计算形式，防止终端报错。
（整理各种字符不同形式时借助了ai）

EmotionBot介绍:
用snownlp库和自己补充的情绪关键词测试中文语句的情感分数，用vaderSentiment库测试英文语句的情感分数，范围从-1(negative)到1(positive)，
并根据情感分数推荐适合该情绪的两首歌曲。

StoryAdventureBot介绍:
设计了一个简单悬疑微科幻剧情《请查收你的明日订单》，玩家需要在每个场景种做出选择，不同的选择组合会导致剧情走向不同，
一共有5各结局，可多次探索，解锁全部结局。
(代码编写时参考了https://blog.csdn.net/weixin_29263201/article/details/158083935)

AnswerBookBot介绍:
一些理性分析无法回答、无法解释的问题，就交给随机和命运吧。输入答案之书的页码/想问的问题，从答案之书给与的回答中也许能得到一些慰藉。

'''
class Bot: # Bot父类

    wait = 1
    language = 'English'

    def __init__(self):
        self.q = ''
        self.a = ''

    def _think(self, s): 
        return s
    
    def _format(self, s):
        return colored(s, 'green')

    def _text(self, zh, en):
        if Bot.language == 'Chinese':
            return zh
        return en

    def _language(self, s): 
        # 判断输入语句的语言
        chinese = 0
        english = 0
        for c in s:
            if '\u4e00' <= c <= '\u9fff':
                chinese+=1
            elif c.isalpha():
                english+=1
        if chinese >= english and chinese > 0:
            return 'Chinese'
        return 'English'

    def _question(self):
        return self.q
    def run(self): 
        sleep(Bot.wait) 
        print(self._format(self._question())) 
        self.a = input() 
        if self.a.strip().lower() in ['q','quit','exit']:
            # 退出键
            return
        sleep(Bot.wait)
        print(self._format(self._think(self.a))) 


# 1.HelloBot
class HelloBot(Bot): 
    def __init__(self):
        self.name = 'HelloBot'
        self.q = "Hi, what is your name?"

    def _question(self):
        return self._text("你好，你叫什么名字？", self.q)
    
    def _think(self, s):
        if self._language(s) == 'Chinese':
            return f"你好，{s}"
        return f"Hello {s}"

# 2.GreetingBot
class GreetingBot(Bot): 
    def __init__(self):
        self.name = 'GreetingBot'
        self.q = "How are you today?"

    def _question(self):
            return self._text("你今天过得怎么样？", self.q)

    def _think(self, s): 
        if self._language(s) == 'Chinese':
            if '不好' in s or '不开心' in s or '不高兴' in s or '难过' in s or '累' in s or '烦' in s:
                return "听到这个我有点难过，希望你接下来会好起来。"
            if '好' in s or '不错' in s or '开心' in s or '还行' in s:
                return "我也很好！"
            return "谢谢你和我说这些。"
        if 'not' in s.lower() or 'bad' in s.lower() or 'sad' in s.lower():
            return "Sorry to hear that"
        if 'good' in s.lower() or 'fine' in s.lower():
            return "I'm feeling good too"
        return "Sorry to hear that"
        
# 3.FavoriteColorBot
class FavoriteColorBot(Bot):
    def __init__(self):
        self.name = 'FavoriteColorBot'
        self.q = "What's your favorite color?"

    def _question(self):
            return self._text("你最喜欢什么颜色？", self.q)

    def _think(self, s):
        if self._language(s) == 'Chinese':
            colors = ['红色', '橙色', '黄色', '绿色', '蓝色', '靛蓝', '紫色']
            return f"你喜欢{s}呀。我最喜欢的颜色是{random.choice(colors)}"
        colors = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'purple']
        return f"You like {s.lower()}? My favorite color is {random.choice(colors)}"

# 4.CalcBot
class CalcBot(Bot):
    def __init__(self):
        self.name = 'CalcBot'
        self.q = ("Input some arithmetic expression to try (x / q / exit / quit to return to menu):")

    def _question(self):
        return self._text("输入一个算术表达式试试（x / q / exit / quit 返回菜单）：",self.q)
    
    def _clean(self, s): 
        # 把各种括号、全角符号和数学符号统一成能识别的半角符号
        s = ' '.join(s.split()) 
        for z in ['\u200b', '\u200c', '\u200d', '\ufeff']:
            s = s.replace(z, '')
        for b in '([{（［｛【〔〖〘〚｟❨❪❬❮❰❲❴':
            s = s.replace(b, '(')
        for b in ')]}）］｝】〕〗〙〛｠❩❫❭❯❱❳❵':
            s = s.replace(b, ')')
        for m in '*×✖✕✗✘❌⨯⨉╳ⅹxXｘＸ∗﹡✱＊⋅·∙•・':
            s = s.replace(m, '*')
        for d in '/÷∕⁄／⫽⟋':
            s = s.replace(d, '/')
        for p in '+＋﹢➕':
            s = s.replace(p, '+')
        for m in '-−–—―‐‑‒﹣﹘－':
            s = s.replace(m, '-')
        for p in '%％﹪':
            s = s.replace(p, '%')
        for d in '.．':
            s = s.replace(d, '.')
        for e in '=＝':
            s = s.replace(e, '=')
        for p in '^＾':
            s = s.replace(p, '**')
        for e in 'ｅＥ':
            s = s.replace(e, 'e')
        digits = '０１２３４５６７８９'
        for i in range(10):
            s = s.replace(digits[i], str(i))
        fixed = ''
        i = 0
        while i < len(s):
            if (s[i] == ',' or s[i] == '，') and i > 0 and s[i - 1].isdigit():
                if i + 3 < len(s) and s[i + 1:i + 4].isdigit() and (i + 4 == len(s) or not s[i + 4].isdigit()):
                    i += 1
                    continue
            fixed += s[i]
            i += 1
        s = fixed
        s = s.rstrip('。；;？?,，')
        if s.endswith('='):
            s = s[:-1].strip()
        fixed = ''
        last = ''
        for c in s:
            if (c == '(' and (last.isdigit() or last == ')')) or (c.isdigit() and last == ')'):
                fixed += '*'
            fixed += c
            if c != ' ':
                last = c
        return fixed

    def _think(self, s): 
        s = self._clean(s)
        if s == '':
            return self._text("抱歉，表达式是空的。请输入类似 1+2 的式子。","Sorry, the expression is empty. Please input something like 1+2.")
        allowed = '0123456789.+-*/%() eE'
        for c in s:
            if c not in allowed:
                if c in ',，':
                    return self._text("抱歉，不支持逗号。请去掉千分位逗号或用小数点。","Sorry, commas are not supported.Please remove thousands separators or use a decimal point.")
                return self._text(
                    f"抱歉，算术表达式里不能出现 '{c}'。请使用数字、括号和 + - * / % **。",
                    f"Sorry, '{c}' is not allowed in an arithmetic expression. Please use numbers, brackets and the operators + - * / % **.")
        depth = 0
        for c in s:
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
            if depth < 0:
                return self._text("抱歉，括号没有配对，请检查表达式。","Sorry, the brackets are not matched. Please check the expression.")
        if depth != 0:
            return self._text("抱歉，括号没有配对，请检查表达式。","Sorry, the brackets are not matched. Please check the expression.")
        try:
            result = simple_eval(s)
            return self._text(f"完成，结果 = {result}", f"Done. Result = {result}")
        except ZeroDivisionError:
            return self._text("抱歉，不能除以 0，请换一个表达式。","Sorry, I cannot divide by zero. Please try another expression.")
        except (SyntaxError, InvalidExpression):
            return self._text("抱歉，这不是一个合法的算术表达式，请重试。","Sorry, that is not a valid arithmetic expression. Please try again.")
        except (NameNotDefined, FunctionNotDefined):
            return self._text("抱歉，我只支持数字、括号和 + - * / % **。","Sorry, I only support numbers, brackets and the operators + - * / % **.")
        except (ValueError, OverflowError):
            return self._text("抱歉，结果太大，我算不了。","Sorry, the result is too large for me to calculate.")
        except Exception: 
            return self._text("抱歉，这个表达式出了点问题，请重试。","Sorry, something went wrong with this expression. Please try again.")

    def run(self):
        quit_words = ['x', 'q', 'exit', 'quit']
        sleep(Bot.wait)
        print(self._format(self._question()))
        while True:
            self.a = input()
            if self.a.strip().lower() in quit_words:
                break
            sleep(Bot.wait)
            print(self._format(self._think(self.a)))
            print(self._format(self._text("再输入一个表达式（x / q / exit / quit 返回菜单）：","Input another expression (x / q / exit / quit to return to menu):")))

# 5.EmotionBot
class EmotionBot(Bot):
    _SONGS_ZH = [
        (-0.40, ["朴树《平凡之路》", "牛奶咖啡《明天，你好》", "华晨宇《好想爱这个世界啊》", "隔壁老樊《我曾》"]),
        (-0.15, ["周杰伦《晴天》", "买辣椒也用券《起风了》", "毛不易《像我这样的人》", "陈奕迅《好久不见》"]),
        ( 0.15, ["毛不易《平凡的一天》", "金玟岐《岁月神偷》", "陈粒《奇妙能力歌》", "房东的猫《云烟成雨》"]),
        ( 0.40, ["周杰伦《七里香》", "田馥甄《小幸运》", "朴树《New Boy》", "S.H.E《紫藤花》"]),
        ( 9.00, ["大张伟《倍儿爽》", "五月天《恋爱ing》", "周杰伦《牛仔很忙》", "S.H.E《中国话》"]),
    ]

    _SONGS_EN = [
        (-0.40, ["Coldplay《Fix You》", "The Beatles《Let It Be》", "Bill Withers《Lean on Me》", "Simon & Garfunkel《Bridge over Troubled Water》"]),
        (-0.15, ["Coldplay《Yellow》", "Adele《Someone Like You》", "The Cranberries《Dreams》", "Radiohead《Creep》"]),
        ( 0.15, ["Jason Mraz《I'm Yours》", "Norah Jones《Don't Know Why》", "The Beatles《Here Comes the Sun》", "Jack Johnson《Banana Pancakes》"]),
        ( 0.40, ["Owl City《Good Time》", "Pharrell Williams《Happy》", "Queen《Don't Stop Me Now》", "Mark Ronson《Uptown Funk》"]),
        ( 9.00, ["Earth, Wind & Fire《September》", "ABBA《Dancing Queen》", "Katrina & The Waves《Walking on Sunshine》", "Taylor Swift《Shake It Off》"]),
    ]

    def __init__(self):
        self.name = 'EmotionBot'
        self.q = ("I can read the emotion behind your words. Tell me something in Chinese or English (x / q / exit / quit to return to menu):")
        self.analyzer = SentimentIntensityAnalyzer()

    def _question(self):
        return self._text("我可以通过文字感受你的情绪。用中文或英文告诉我一句话（x / q / exit / quit 返回菜单）：", self.q)

    def _rule_score(self, s):
        rules = [
            ('没有不开心', 1), ('没有不高兴', 1), ('不是很好', -1), ('不太好', -1),
            ('不太开心', -1), ('不太高兴', -1), ('不太快乐', -1), ('不太喜欢', -1),
            ('不开心', -1), ('不高兴', -1), ('不快乐', -1), ('不幸福', -1),
            ('不喜欢', -1), ('不满意', -1), ('不舒服', -1), ('不期待', -1),
            ('不兴奋', -1), ('不好', -1), ('不棒', -1), ('不差', 1),
            ('不难过', 1), ('不伤心', 1), ('不痛苦', 1), ('不失望', 1),
            ('不生气', 1), ('不焦虑', 1), ('不害怕', 1), ('不讨厌', 1),
            ('不孤独', 1), ('不崩溃', 1), ('不累', 1), ('不烦', 1),
            ('不坏', 1), ('不错', 1),
            ('很开心', 1), ('很高兴', 1), ('很快乐', 1), ('很幸福', 1),
            ('很喜欢', 1), ('很满意', 1), ('很舒服', 1), ('很期待', 1),
            ('很兴奋', 1), ('很棒', 1), ('很好', 1), ('真好', 1),
            ('好开心', 1), ('好高兴', 1), ('好棒', 1), ('好喜欢', 1),
            ('还好', 1), ('还行', 1), ('开心', 1), ('高兴', 1), 
            ('快乐', 1), ('幸福', 1), ('喜欢', 1), ('满意', 1), 
            ('舒服', 1), ('期待', 1), ('兴奋', 1),
            ('很难过', -1), ('很伤心', -1), ('很痛苦', -1), ('很失望', -1),
            ('很生气', -1), ('很焦虑', -1), ('很害怕', -1), ('很讨厌', -1),
            ('很糟糕', -1), ('很孤独', -1), ('很崩溃', -1), ('很累', -1),
            ('好累', -1), ('太累', -1), ('累了', -1), ('累死', -1),
            ('很烦', -1), ('好烦', -1), ('太烦', -1), ('烦躁', -1),
            ('心烦', -1), ('烦死', -1), ('很差', -1), ('太差', -1), 
            ('差劲', -1), ('很坏', -1), ('太坏', -1), ('坏透', -1),
            ('难过', -1), ('伤心', -1), ('痛苦', -1), ('失望', -1),
            ('生气', -1), ('焦虑', -1), ('害怕', -1), ('讨厌', -1),
            ('糟糕', -1), ('孤独', -1), ('崩溃', -1), ('担心', -1),
            ('委屈', -1), ('后悔', -1), ('无聊', -1), ('郁闷', -1),
            ('绝望', -1), ('愤怒', -1), ('紧张', -1),
        ]
        score = 0
        i = 0
        while i < len(s):
            matched = False
            for word, value in rules:
                if s.startswith(word, i):
                    score += value
                    i += len(word)
                    matched = True
                    break
            if not matched:
                i += 1
        return score

    def _score(self, s):
        # 分数范围统一到-1~1
        language = self._language(s)
        if language == 'Chinese':
            score = SnowNLP(s).sentiments*2 - 1
            rule_score = self._rule_score(s)
            if rule_score > 0:
                score = max(score, 0.5)
            elif rule_score < 0:
                score = min(score, -0.5)
        else:
            score = self.analyzer.polarity_scores(s)['compound']
        return language, score

    def _songs(self, score, language):
        table = self._SONGS_ZH if language == 'Chinese' else self._SONGS_EN
        for limit, songs in table:
            if score <= limit:
                return random.sample(songs, 2)
        return random.sample(table[-1][1], 2)

    def _think(self, s):
        s = s.strip()
        if s == '':
            return self._text("请先告诉我一句话，我才能读情绪。","Please tell me a sentence so I can read its emotion.")
        has_word = False
        for c in s:
            if c.isalpha():
                has_word = True
                break
        if not has_word:
            return self._text("请用文字表达，不要只输入数字或符号。","Please use some words, not only numbers or symbols.")
        try:
            language, score = self._score(s)
        except Exception: 
            return self._text("抱歉，我读不懂这句话的情绪，请换一句试试。","Sorry, I could not read the emotion in that sentence. Please try another one.")
        
        songs = self._songs(score, language)

        if language == 'Chinese':
            if score > 0.05:
                mood = '积极'
                reply = "我能感受到你的正能量，继续保持！"
            elif score < -0.05:
                mood = '消极'
                reply = "听到这个我有点难过，祝福你！"
            else:
                mood = '中性'
                reply = "听起来比较平静，愿意的话可以再和我说说。"
            song_text = "、".join(songs)
            return f"情绪：{mood}（分数 = {score:.2f}）。{reply}\n向你推荐两首歌叭：{song_text}"
        if score > 0.05:
            mood = 'positive'
            reply = "I can feel the positive energy. Keep it up!"
        elif score < -0.05:
            mood = 'negative'
            reply = "I'm sorry to hear that. Take care of yourself."
        else:
            mood = 'neutral'
            reply = "It sounds fairly neutral. Tell me more if you like."
        song_text = " / ".join(songs)
        return f"Emotion: {mood} (score = {score:.2f}). {reply}\nSongs for you: {song_text}"

    def run(self):
        quit_words = ['x', 'q', 'exit', 'quit']
        sleep(Bot.wait)
        print(self._format(self._question()))
        while True:
            self.a = input()
            if self.a.strip().lower() in quit_words:
                break
            sleep(Bot.wait)
            print(self._format(self._think(self.a)))
            print(self._format(self._text( "再告诉我一句话（x / q / exit / quit 返回菜单）：","Tell me another sentence (x / q / exit / quit to return to menu):")))

# 6.StoryAdventureBot
class StoryAdventureBot(Bot):

    wait = 1.12
    def __init__(self):
        self.name = 'StoryAdventureBot'
        self.q = "欢迎来到《请查收你的明日订单》！"

    def _question(self):
        return "欢迎来到《请查收你的明日订单》！\n输入选项编号继续游戏，输入 q 返回主菜单。"

    def _format(self, s, color='green'):
        return colored(s, color)

    def _say(self, s, color='green'):
        print(self._format(s, color))
        sleep(StoryAdventureBot.wait)

    def _choose(self, prompt, options):
        while True:
            self._say(prompt, None)
            for key, value in options.items():
                print(self._format(f"{key}. {value}"))
            choice = input(colored("请输入选项：", 'blue')).strip().lower()
            if choice in ['q', 'quit', 'exit']:
                return None
            if choice in options:
                return choice
            self._say("输入无效，请输入对应的选项编号，或输入 q 返回主菜单。", 'blue')
            print('\n')

    def _ending(self, ending_name, ending_text):
        self._say("\n" + "==================" + " " + ending_name + " " + "==================")
        self._say(ending_text)
        self._say("本次剧情结束，感谢游玩~再次探索可解锁更多结局哦！")

    def run(self):
        while True:# 一些结局参数的初始化
            has_receipt = False
            trust_linxia = False
            has_server_clue = False
            know_secret = False
            final_choice = ""

            self._say("\n" + "====================================================")
            self._say("《请查收你的明日订单》")
            self._say("一款悬疑微科幻文字冒险游戏")
            self._say("====================================================" + "\n")
            self._say(
                "晚上 23:10，你走进一家 24 小时便利店，准备买一瓶可乐。\n"
                "就在店员准备扫码时，收银机突然吐出一张小票。\n"
            )
            self._say(
                "【未来订单】\n"
                "订单编号：OR-2317\n"
                "订单时间：23:17\n"
                "商品：可乐 1、三明治 1、创可贴 1\n"
                "备注：请不要让店员打开后门。\n",
                'yellow'
            )

            # 场景一：一张奇怪的小票
            choice = self._choose(
                "场景一：一张奇怪的小票\n"
                "店员林夏皱起眉头：奇怪，我还没结账呢。\n",
                {
                    '1': "把小票交给林夏",
                    '2': "悄悄把小票收起来",
                    '3': "询问旁边的机器人小橘"
                }
            )
            if choice is None:
                return
            if choice == '1':
                trust_linxia = True
                self._say("你把小票递给林夏。她看了半天，神情变得谨慎，但似乎愿意相信你。\n")
            elif choice == '2':
                has_receipt = True
                self._say("你把小票折好放进口袋。也许之后能派上用场。\n")
            else:
                self._say(
                    "你问小橘是怎么回事。小橘回答：根据数据库，您将在七分钟后购买一份三明治。\n"
                    "你：那我七分钟后会不会变成亿万富翁？\n"
                    "小橘：抱歉，该功能尚未开放。\n"
                )

            # 场景二：机器人知道得太多了
            choice = self._choose(
                "场景二：机器人知道得太多了\n"
                "你觉得这家店不太对劲，决定进一步调查。\n",
                {
                    '1': "询问小橘：你怎么知道未来订单？",
                    '2': "询问林夏：这台机器以前也这样吗？",
                    '3': "检查收银机后台"
                }
            )
            if choice is None:
                return
            if choice == '1':
                self._say(
                    "小橘：本店部署了 ORANGE-FUTURE 服务，可以预测未来七分钟内的顾客行为。\n"
                    "你：所以你能预知未来？\n"
                    "小橘：不完全准确，预测准确率为 87.6%。剩下的 12.4% 由顾客自由发挥。\n"
                )
            elif choice == '2':
                if trust_linxia:
                    self._say(
                        "林夏压低声音：最近几天已经发生过几次类似的事。每次系统出错，"
                        "后门附近就会出现奇怪的订单。\n"
                    )
                    has_server_clue = True
                else:
                    self._say("林夏：只是机器故障吧，你不用太在意。她似乎不想多说。\n")
            else:
                self._say(
                    "收银机后台显示：\n"
                    "ORANGE-FUTURE\n"
                    "Prediction Mode: ACTIVE\n"
                    "Feedback Mode: ACTIVE\n"
                    "Next Update: 23:17\n",
                    'yellow'
                )
                has_server_clue = True

            # 场景三：23:17 停电
            choice = self._choose(
                "场景三：23:17 停电\n"
                "突然，便利店停电了。应急灯亮起，小橘发出警告：请不要让林夏打开后门！\n"
                "与此同时，后门传来三声敲门声。\n",
                {
                    '1': "阻止林夏开门",
                    '2': "跟着林夏去后门",
                    '3': "留在柜台检查小橘"
                }
            )
            if choice is None:
                return
            if choice == '1':
                self._say("你提醒林夏小票上的备注。她惊讶地看着你，决定暂时听你的。\n")
                trust_linxia = True
            elif choice == '2':
                self._say(
                    "你跟林夏来到后门。门外没有人，只有一个快递柜。\n"
                    "柜门上贴着纸条：致 ORANGE-FUTURE 项目组，请于 23:24 前取回测试设备。\n"
                )
                has_server_clue = True
            else:
                self._say(
                    "你打开小橘的维护面板，屏幕显示：\n"
                    "Feedback Mode: ACTIVE\n"
                    "External Data Transfer: ON\n"
                    "Server Temperature: 82°C\n",
                    'yellow'
                )
                has_server_clue = True

            # 场景四：后门的秘密
            self._say(
                "场景四：后门的秘密\n"
                "你发现便利店后面藏着一个小型服务器机房。服务器旁有一张工作证：\n"
                "姓名：陈默\n"
                "部门：智能零售系统研发部\n"
                "项目：ORANGE-FUTURE\n"
                "这时，你的手机收到两条短信：不要相信小橘。也不要相信林夏。\n",
                None
            )
            choice = self._choose(
                "你决定怎么做？",
                {
                    '1': "联系工作证上的陈默",
                    '2': "询问林夏",
                    '3': "检查服务器"
                }
            )
            if choice is None:
                return
            if choice == '1':
                self._say(
                    "陈默接起电话：你怎么会在服务器旁边？\n"
                    "你：我也想知道，为什么你们把未来订单印在收银机上？\n"
                    "陈默：23:24 前，千万不要让系统进入自我优化模式。\n"
                )
                has_server_clue = True
            elif choice == '2':
                if trust_linxia:
                    self._say(
                        "林夏终于告诉你：这家店是测试门店。系统不仅预测顾客行为，"
                        "还会根据预测结果调整商品陈列、灯光和机器人的行动。\n"
                    )
                    know_secret = True
                else:
                    self._say("林夏：我只是普通店员，你问我这些干什么？她没有继续解释。\n")
            else:
                self._say(
                    "服务器上运行着一个循环程序：\n"
                    "预测顾客行为 → 生成行动 → 改变店内环境 → 收集顾客数据 → 更新预测。\n"
                    "你终于明白：它不仅预测行为，还会主动改变环境。\n"
                )
                know_secret = True
                has_server_clue = True

            # 场景五：所谓的未来
            self._say(
                "场景五：所谓的未来\n"
                "陈默赶到便利店。他解释说，系统并不能真正预测未来，"
                "只是根据过去的数据计算未来七分钟内顾客最可能做什么。\n"
                "更严重的是，系统会根据预测结果主动改变便利店环境，"
                "再把改变后的结果当成新的数据，不断强化自己的预测。\n",
                None
            )
            choice = self._choose(
                "你还想问陈默什么？",
                {
                    '1': "询问如何关闭系统",
                    '2': "询问故障原因",
                    '3': "质问他为什么不停止测试"
                }
            )
            if choice is None:
                return
            if choice == '1':
                self._say("陈默：服务器后台有紧急关闭入口，但需要管理员权限。\n")
            elif choice == '2':
                self._say(
                    "陈默：系统的自我优化程序出现问题，预测和执行任务不断增加，"
                    "服务器温度已经超过安全范围。\n"
                )
                has_server_clue = True
            else:
                self._say(
                    "陈默：直接断电可能导致数据损坏，所以我赶来处理。\n"
                    "你：所以你们就让它继续运行？\n"
                    "陈默没有回答。\n"
                )
                know_secret = True

            # 场景六：最后七分钟
            self._say(
                "场景六：最后七分钟\n"
                "时间来到 23:23。服务器温度不断升高，小橘的声音断断续续：\n"
                "系统即将进入自我优化模式。预计完成时间：23:24。\n",
                None
            )
            choice = self._choose(
                "陈默：必须马上做出决定！",
                {
                    '1': "关闭系统",
                    '2': "相信小橘，让系统继续运行",
                    '3': "修改系统预测结果"
                }
            )
            if choice is None:
                return
            if choice == '1':
                final_choice = "shutdown"
                self._say("你按下紧急关闭按钮。服务器发出一声长鸣，屏幕逐渐暗了下去。\n")
            elif choice == '2':
                final_choice = "trust_ai"
                self._say("你决定相信小橘。它回答：感谢您的信任，系统将继续运行。\n")
            else:
                final_choice = "modify"
                if has_server_clue and know_secret:
                    self._say(
                        "你根据找到的线索修改反馈机制，让系统不再主动干预顾客选择。\n"
                        "屏幕显示：修改成功。"
                    )
                else:
                    self._say(
                        "你尝试修改系统，但缺少关键线索，无法确认应该修改哪一部分。\n"
                        "屏幕显示：修改失败。"
                    )
                    final_choice = "modify_failed"

            # 场景七：结局判定。隐藏结局必须放在普通成功结局之前。
            self._say("场景七：23:24 订单完成", None)

            if (final_choice == "modify"
                    and has_receipt
                    and has_server_clue
                    and know_secret):
                self._ending(
                    "隐藏结局 END04：第八分钟",
                    "系统似乎被修复了。就在你准备离开时，打印机突然再次启动。\n"
                    "订单时间：23:31\n"
                    "商品：可乐 1\n"
                    "备注：欢迎回来。\n"
                    "你：不是说修好了吗？\n"
                    "小橘：根据预测，您还会回来。\n"
                )
            elif (final_choice == "modify"
                    and has_server_clue
                    and know_secret):
                self._ending(
                    "好结局 END02：未来便利店",
                    "你成功修改了系统，让它学会等待顾客自主选择，而不是主动干预。\n"
                    "小橘：已更新行为准则：顾客没有下单前，不得擅自预测其购买行为。\n"
                    "林夏：这下终于像个正常机器人了。\n"
                )
            elif final_choice == "shutdown":
                self._ending(
                    "好结局 END01：正常营业",
                    "你成功关闭系统，阻止了事故。林夏终于可以安心下班，陈默开始收拾服务器。\n"
                    "你拿起可乐准备离开。\n"
                    "林夏：先生，你的可乐还没付款。\n"
                    "你：忙了半天，差点忘了。\n"
                )
            elif final_choice == "trust_ai":
                self._ending(
                    "搞笑结局 END03：最佳员工",
                    "系统继续运行，并将你识别为最适合管理便利店的人类。\n"
                    "收银机打印出一份合同：恭喜您成为本店首席运营顾问。工作时间：24 小时。\n"
                    "你：我只是来买瓶可乐的啊！\n"
                )
            else:
                self._ending(
                    "失败结局 END05：系统维护中",
                    "服务器过热，系统自动断开。\n"
                    "林夏：好了，现在只能手动盘点了。\n"
                    "陈默：看来今晚又得加班。\n"
                    "你：所以……我的三明治呢？\n"
                    "林夏：卖完了。\n"
                )

            # 再来一次
            choice = self._choose(
                "再玩一次么？",
                {'1': "重新开始", '2': "返回主菜单"}
            )
            if choice != '1':
                return



# 7. AnswerBookBot
SOFT = [
    "是的。",
    "毫无疑问。",
    "去做吧，不用问。",
    "这一次，会好起来。",
    "顺其自然。",
    "保持耐心，它在路上。",
    "相信你的直觉。",
    "会有人帮你。",
    "你比你以为的更有准备。",
    "现在就是最好的时机。",
    "你不需要谁的许可。",
    "会有人理解你的。",
]

MID = [
    "也许。",
    "是的——但有个条件。",
    "时机未到。",
    "取决于你愿不愿意先开口。",
    "你现在问，还太早。",
    "答案不在书里，在你手上。",
    "换一个方向看看。",
    "会有代价。",
    "一半一半。",
    "你已经有答案了，你只是在找一个同意的人。",
    "先做最小的那一步。",
    "时间会替你回答。",
]

HARD = [
    "不。",
    "不会。",
    "别想了。",
    "你已经问过很多遍了。",
    "你在骗自己。",
    "你自己清楚，只是不敢承认。",
    "晚了。",
    "你问错了对象。",
    "你期待的答案不在这里。",
    "你只是不甘心。",
    "这不是命运，是你的选择。",
    "你不想要答案，你想要安慰。",
]

SPECIAL = {
    1: "是的。而且比你担心的要好得多。",
    50: "你已经知道答案了。你只是想听别人把它说出口。",
    100: "这是最后一页。答案从来不在书里。",
}

class AnswerBookBot(Bot):
    def __init__(self):
        super().__init__()
        self.name = 'AnswerBookBot'
        self.q = ("把问题说出口，或随便报一个 1-100 的页码\n"
                  "或写如下格式：22 这一次会赢吗\n"
                  "[ 输入 q 合上书 ]\n"
                  ">")
        self.count = 0
        self.last = None

    def _format(self, s):
        return s

    def _think(self, s):
        s = s.strip()

        if not s:
            return "你还没问哦"

        if s == self.last:
            return ("\n[ 书页自己合上了一半 ]\n\n"
                    "你刚才问过了哦。\n"
                    "答案不会因为你多问一次就改变。\n")

        self.last = s
        self.count += 1

        text = s
        if text.startswith('第'):
            text = text[1:].strip()

        number = ''
        for c in text:
            if c.isdigit():
                number += c
            else:
                break

        if number != '':
            page = int(number)
            if not 1 <= page <= 100:
                return "\n这本书只有 100 页哦\n"
            asked = f"[ 你翻到了第 {page} 页 ]"
        else:
            page = random.randint(1, 100)
            asked = f"[ 书自己翻到了第 {page} 页 ]"

        if page in SPECIAL:
            answer = SPECIAL[page]
        elif page <= 33:
            answer = random.choice(SOFT)
        elif page <= 66:
            answer = random.choice(MID)
        else:
            answer = random.choice(HARD)

        return (f"\n{asked}\n"
                "───────────────────────────\n"
                "\n"
                f"{answer}\n"
                "\n"
                "───────────────────────────\n")

    def run(self):
        print("\n" + "═"*38)
        print("答 案 之 书")
        print("═" * 38)
        print("心里想着你的问题。")
        print("然后随便报一个数字，或者直接问。")
        print("═"*38)

        while True:
            print(self._format(self.q))
            a = input("  ").strip()

            if a.lower() in ("q", "quit", "exit", "退出"):
                print("\n书合上了。")
                if self.count >= 3:
                    print(f"你已经问了 {self.count} 次。")
                    print("这本身就是答案。\n")
                break

            sleep(0.5)
            print(self._format(self._think(a)))


# Bakeni 聊天系统
class Bakeni: 

    def __init__(self, wait=1):
        Bot.wait = wait
        self.bots = []

    def add(self, bot):
        self.bots.append(bot) 

    def _prompt(self, s):
        print(s)
        print()

    def _text(self, zh, en):
        if Bot.language == 'Chinese':
            return zh
        return en

    def _ask_language(self):
        self._prompt("请选择bot使用的语言 / Choose the bot language: 1. 中文, 2. English")
        while True:
            choice = input().strip().lower()
            if choice in ['1', '中文', 'chinese', 'zh']:
                Bot.language = 'Chinese'
                break
            if choice in ['2', 'english', 'en']:
                Bot.language = 'English'
                break
            print("请输入 1 或 2 / Please enter 1 or 2.")

    def _show_menu(self):
        self._prompt(self._text("请选择一个bot：", "Choose a bot:"))
        for i, bot in enumerate(self.bots, 1):
            print(f"{i}. {bot.name}")
        print(self._text("q. 退出", "q. Quit"))
        print()

    def run(self):
        self._prompt("Bakeni dialog system / Bakeni 对话系统")
        self._ask_language()
        self._prompt(self._text("欢迎使用 Bakeni 对话系统。", "Welcome to the Bakeni dialog system."))
        while True:
            self._show_menu()
            choice = input().strip().lower()
            if choice in ['q', 'quit', 'exit']:
                break
            if choice.isdigit():
                index = int(choice)
                if 1 <= index <= len(self.bots):
                    self.bots[index - 1].run()
                    continue
            print(self._text("请输入菜单编号，或 q 退出。", "Please enter a menu number, or q to quit."))


bakeni = Bakeni(1)

bakeni.add(HelloBot())
bakeni.add(GreetingBot())
bakeni.add(FavoriteColorBot())
bakeni.add(CalcBot())
bakeni.add(EmotionBot())
bakeni.add(StoryAdventureBot())
bakeni.add(AnswerBookBot())
# 运行之
bakeni.run()
