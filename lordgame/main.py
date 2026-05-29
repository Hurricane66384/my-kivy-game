from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.utils import get_color_from_hex
from kivy.uix.popup import Popup
from kivy.core.text import LabelBase  
import random
import os

# ==================== 0. 全局解决中文乱码 ====================
def get_valid_font():
    possible_names = ["myfont.ttf", "myfont.ttc", "simhei.ttf", "msyh.ttc"]
    for name in possible_names:
        local_font = os.path.join(os.path.dirname(__file__), name)
        if os.path.exists(local_font): return local_font
    win_fonts = ["C:\\Windows\\Fonts\\msyh.ttc", "C:\\Windows\\Fonts\\simsun.ttc", "C:\\Windows\\Fonts\\simhei.ttf"]
    for path in win_fonts:
        if os.path.exists(path): return path
    return None

font_path = get_valid_font()
if font_path:
    LabelBase.register(name="Roboto", fn_regular=font_path)

# ==================== 1. 核心游戏数据与多难度信仰平衡逻辑 ====================
class KingdomCore:
    def __init__(self, last_name, religion_type="未确立", difficulty_level="普通"):
        self.lord_name = last_name if last_name.strip() else "卡佩"
        self.religion = religion_type 
        self.difficulty = difficulty_level # "简单", "普通", "地狱"
        
        self.age = 18
        self.is_married = False
        self.children_count = 0
        self.generation = 1
        self.year = 1
        self.tech_level = 1
        self.plot_assassination_bonus = 0  
        self.is_game_over = False
        
        # 👑 动态难度资源配置矩阵
        if self.difficulty == "简单":
            self.gold = 600
            self.food = 300
            self.land = 8
            self.protection_years = 20 # 20年无蛮族免战保护
            self.disaster_chance = 12  # 极低天灾率
        elif self.difficulty == "地狱":
            self.gold = 250
            self.food = 100
            self.land = 4
            self.protection_years = 5  # 仅5年保护
            self.disaster_chance = 45  # 疯狂爆发天灾
        else: # 普通
            self.gold = 350  
            self.food = 150
            self.land = 5
            self.protection_years = 10
            self.disaster_chance = 25

        # 全局动态长效状态机
        self.active_statuses = []
        
        # 初始军队编制
        self.my_army_units = [
            {"id": 1, "title": "01.征召轻步兵", "type": "步兵", "power": 2} for _ in range(5)
        ]
        
        self.titles = [
            {"name": "【流浪骑士】", "req": 1}, {"name": "【册封男爵】", "req": 10},
            {"name": "【世袭伯爵】", "req": 30}, {"name": "【至高公爵】", "req": 60},
            {"name": "【开国君王】", "req": 100}, {"name": "【日不落神圣皇帝】", "req": 200}
        ]

        self.tech_tree = [f"【Lv.{i} 封建科技演进】" for i in range(1, 21)]
        
        # ⚔️ 完整30大王牌军团
        self.army_shop = [
            {"id": 1, "title": "01.征召轻步兵", "gold": 20, "army": 2, "type": "步兵"},
            {"id": 2, "title": "02.威尔士长弓手", "gold": 35, "army": 4, "type": "弓兵"},
            {"id": 3, "title": "03.条顿持盾重步兵", "gold": 45, "army": 5, "type": "步兵"},
            {"id": 4, "title": "04.圣殿骑士先锋", "gold": 80, "army": 9, "type": "骑兵"},
            {"id": 5, "title": "05.瑞士长枪方阵兵", "gold": 50, "army": 6, "type": "步兵"},
            {"id": 6, "title": "06.热那亚重弩卫队", "gold": 55, "army": 7, "type": "弓兵"},
            {"id": 7, "title": "07.法兰西精锐骠骑", "gold": 90, "army": 10, "type": "骑兵"},
            {"id": 8, "title": "08.拜占庭圣骑兵", "gold": 110, "army": 12, "type": "骑兵"},
            {"id": 9, "title": "09.哥特双手巨剑士", "gold": 65, "army": 8, "type": "步兵"},
            {"id": 10, "title": "10.波兰翼骑兵团", "gold": 120, "army": 14, "type": "骑兵"},
            {"id": 11, "title": "11.奥斯曼新军火枪手", "gold": 90, "army": 11, "type": "弓兵"},
            {"id": 12, "title": "12.纽伦堡轻型青铜炮", "gold": 100, "army": 13, "type": "特殊"},
            {"id": 13, "title": "13.苏格兰高地剑士", "gold": 40, "army": 5, "type": "步兵"},
            {"id": 14, "title": "14.英格兰皇家斥候", "gold": 50, "army": 6, "type": "骑兵"},
            {"id": 15, "title": "15.乌克兰哥萨克骑兵", "gold": 85, "army": 10, "type": "骑兵"},
            {"id": 16, "title": "16.佛兰德斯精锐投石兵", "gold": 30, "army": 3, "type": "弓兵"},
            {"id": 17, "title": "17.德意志双手巨剑兵", "gold": 70, "army": 9, "type": "步兵"},
            {"id": 18, "title": "18.马穆鲁克重骑兵", "gold": 115, "army": 13, "type": "骑兵"},
            {"id": 19, "title": "19.明朝神机营火铳兵", "gold": 95, "army": 12, "type": "弓兵"},
            {"id": 20, "title": "20.红衣大炮轰击阵", "gold": 140, "army": 18, "type": "特殊"},
            {"id": 21, "title": "21.北欧维京狂战士", "gold": 60, "army": 8, "type": "步兵"},
            {"id": 22, "title": "22.大马士革弯刀卫队", "gold": 75, "army": 9, "type": "步兵"},
            {"id": 23, "title": "23.蒙古怯薛近卫骑兵", "gold": 130, "army": 15, "type": "骑兵"},
            {"id": 24, "title": "24.不列颠长弓卫队", "gold": 80, "army": 10, "type": "弓兵"},
            {"id": 25, "title": "25.日本战国赤备骑兵", "gold": 105, "army": 12, "type": "骑兵"},
            {"id": 26, "title": "26.西班牙大方阵长矛手", "gold": 85, "army": 11, "type": "步兵"},
            {"id": 27, "title": "27.诸葛连弩机动营", "gold": 70, "army": 9, "type": "弓兵"},
            {"id": 28, "title": "28.法兰西皇家重装骑士", "gold": 150, "army": 20, "type": "骑兵"},
            {"id": 29, "title": "29.达芬奇重甲机关战车", "gold": 160, "army": 22, "type": "特殊"},
            {"id": 30, "title": "30.拜占庭铁甲具装巨骑", "gold": 180, "army": 25, "type": "骑兵"}
        ]

        # 🔮 完整10大影子密谋
        self.plot_shop = [
            {"id": 1, "title": "01.死士沙场投毒", "desc": "牺牲最后1队军团，下场战力+6", "cost_gold": 0, "need_army": 2},
            {"id": 2, "title": "02.金买敌军先锋", "desc": "消耗50金币，下场战力+5", "cost_gold": 50, "need_army": 0},
            {"id": 3, "title": "03.伪造宣战圣旨", "desc": "消耗30金币，直接抢占1块领地", "cost_gold": 30, "need_army": 0},
            {"id": 4, "title": "04.刺杀敌方统帅", "desc": "牺牲最后1队军团并花30金，下场战力+12", "cost_gold": 30, "need_army": 2},
            {"id": 5, "title": "05.散布粮仓黑死病", "desc": "消耗40金币，使邻国领地绝收并夺其20粮", "cost_gold": 40, "need_army": 0},
            {"id": 6, "title": "06.暗中走私铁矿", "desc": "消耗20粮食，倒卖换取50金币", "cost_gold": -50, "need_army": 0}, 
            {"id": 7, "title": "07.买通宗教审判长", "desc": "花费60金币，封锁任何日常天灾2回合", "cost_gold": 60, "need_army": 0},
            {"id": 8, "title": "08.夜袭敌方马厩", "desc": "牺牲1队兵，下场战役敌方骑兵战力折半", "cost_gold": 0, "need_army": 2},
            {"id": 9, "title": "09.重金招募民间游侠", "desc": "花费70金币，直接随机获赠1队强力骑兵", "cost_gold": 70, "need_army": 0},
            {"id": 10, "title": "10.影子宫廷政变", "desc": "花费100金币，立刻强行诞下一名嫡系储君", "cost_gold": 100, "need_army": 0}
        ]

        # 📜 完整50张内政卡牌池
        self.normal_deck = [
            {"title": "[政务01] 开垦荒地", "desc": "发展农业", "gold": -6, "food": 25, "land": 0},
            {"title": "[政务02] 商队贸易", "desc": "粮换资金", "gold": 30, "food": -10, "land": 0},
            {"title": "[政务03] 兴修水渠", "desc": "引水灌溉", "gold": -10, "food": 30, "land": 0},
            {"title": "[政务04] 邻国联姻", "desc": "联姻(要求:未婚)", "gold": 30, "food": 10, "land": 1, "type": "marry"},
            {"title": "[政务05] 诞下子嗣", "desc": "王室添丁(要求:已婚)", "gold": -5, "food": -5, "land": 0, "type": "child"},
            {"title": "[政务06] 盐铁专卖", "desc": "管控资源", "gold": 35, "food": -4, "land": 0},
            {"title": "[政务07] 颁布法典", "desc": "稳固统治", "gold": -15, "food": 0, "land": 1},
            {"title": "[政务08] 采石筑墙", "desc": "强化城防", "gold": -10, "food": -10, "land": 1},
            {"title": "[政务09] 疏浚河道", "desc": "预防洪涝", "gold": -12, "food": 20, "land": 0},
            {"title": "[政务10] 设立市集", "desc": "促进通商", "gold": 40, "food": -8, "land": 0},
            {"title": "[政务11] 开采金矿", "desc": "补充国库", "gold": 50, "food": -15, "land": 0},
            {"title": "[政务12] 举办竞技", "desc": "提振民心", "gold": -20, "food": 15, "land": 0},
            {"title": "[政务13] 森林伐木", "desc": "获取物料", "gold": 15, "food": -5, "land": 0},
            {"title": "[政务14] 建立磨坊", "desc": "粮食加工", "gold": -8, "food": 22, "land": 0},
            {"title": "[政务15] 没收家产", "desc": "严惩贪腐", "gold": 60, "food": -10, "land": -1},
            {"title": "[政务16] 恩赏骑士", "desc": "巩固军心", "gold": -25, "food": 10, "land": 1},
            {"title": "[政务17] 推广轮作", "desc": "农业飞跃", "gold": -5, "food": 35, "land": 0},
            {"title": "[政务18] 沿海捕捞", "desc": "开拓渔业", "gold": -6, "food": 18, "land": 0},
            {"title": "[政务19] 修缮修院", "desc": "安抚教会", "gold": -18, "food": 0, "land": 1},
            {"title": "[政务20] 雇佣铁匠", "desc": "改良军备", "gold": -15, "food": -5, "land": 1},
            {"title": "[政务21] 扩建港口", "desc": "海外远航", "gold": 45, "food": -12, "land": 0},
            {"title": "[政务22] 圈地畜牧", "desc": "肉类丰收", "gold": -10, "food": 28, "land": 0},
            {"title": "[政务23] 查抄走私", "desc": "充公暗财", "gold": 35, "food": 5, "land": 0},
            {"title": "[政务24] 设立驿站", "desc": "强化集权", "gold": -14, "food": -4, "land": 2},
            {"title": "[政务25] 减免赋税", "desc": "休养生息", "gold": -30, "food": 40, "land": 0},
            {"title": "[政务26] 招募流民", "desc": "填充劳力", "gold": -12, "food": 25, "land": 0},
            {"title": "[政务27] 建立庄园", "desc": "贵族割据", "gold": 20, "food": 15, "land": -1},
            {"title": "[政务28] 开垦山地", "desc": "贫瘠多收", "gold": -8, "food": 16, "land": 0},
            {"title": "[政务29] 统一商税", "desc": "财富重组", "gold": 38, "food": -6, "land": 0},
            {"title": "[政务30] 铸造新币", "desc": "通货操纵", "gold": 55, "food": -18, "land": 0},
            {"title": "[政务31] 选拔侍从", "desc": "提拔近臣", "gold": -10, "food": 8, "land": 1},
            {"title": "[政务32] 净化沼泽", "desc": "化害为利", "gold": -15, "food": 32, "land": 0},
            {"title": "[政务33] 兴建粮仓", "desc": "防范灾荒", "gold": -12, "food": 20, "land": 1},
            {"title": "[政务34] 垄断香料", "desc": "暴利贸易", "gold": 65, "food": -20, "land": 0},
            {"title": "[政务35] 严控盐场", "desc": "官营资产", "gold": 42, "food": -5, "land": 0},
            {"title": "[政务36] 驱逐流寇", "desc": "境内治安", "gold": -8, "food": 12, "land": 1},
            {"title": "[政务37] 修筑御道", "desc": "王权巡视", "gold": -22, "food": -5, "land": 2},
            {"title": "[政务38] 建立医馆", "desc": "防治伤寒", "gold": -16, "food": 10, "land": 0},
            {"title": "[政务39] 清查田亩", "desc": "清算隐产", "gold": 28, "food": 14, "land": 0},
            {"title": "[政务40] 异邦结盟", "desc": "购买属国", "gold": -40, "food": 20, "land": 2},
            {"title": "[政务41] 设立学堂", "desc": "培育文官", "gold": -18, "food": 5, "land": 1},
            {"title": "[政务42] 征收人头税", "desc": "强取豪夺", "gold": 48, "food": -15, "land": 0},
            {"title": "[政务43] 组建猎队", "desc": "皇家狩猎", "gold": -5, "food": 22, "land": 0},
            {"title": "[政务44] 购买粮草", "desc": "以钱易粮", "gold": -35, "food": 45, "land": 0},
            {"title": "[政务45] 出售爵位", "desc": "头衔买卖", "gold": 70, "food": -12, "land": -1},
            {"title": "[政务46] 军屯种地", "desc": "兵士农作", "gold": -5, "food": 30, "land": 0},
            {"title": "[政务47] 扩建王宫", "desc": "彰显国威", "gold": -50, "food": 0, "land": 2},
            {"title": "[政务48] 开拓牧场", "desc": "战马培育", "gold": -15, "food": 25, "land": 1},
            {"title": "[政务49] 严惩盗匪", "desc": "保护商道", "gold": 15, "food": 10, "land": 0},
            {"title": "[政务50] 普天同庆", "desc": "王室大赦", "gold": -25, "food": 35, "land": 1}
        ]

        # 🌪️ 基础天灾模板（由核心根据不同难度动态增幅）
        self.disaster_deck_raw = [
            {"title": "领地蝗虫大旱", "gold": -10, "food": -40, "land": 0, "s_name": "连年大旱", "s_type": "food_modifier", "s_val": -0.30, "s_dur": 5, "s_desc": "全国大旱：农耕基本产量减少30%"},
            {"title": "狂犬瘟疫流行", "gold": -35, "food": -15, "land": 0, "s_name": "疯狗恶疾", "s_type": "gold_modifier", "s_val": -0.15, "s_dur": 3, "s_desc": "瘟疫封城：内政金币流失15%"},
            {"title": "庄园叛军暴动", "gold": -30, "food": -10, "land": -1, "s_name": None},
            {"title": "王室金库失盗", "gold": -65, "food": 0, "land": 0, "s_name": None},
            {"title": "黑死病蔓延", "gold": -20, "food": -30, "land": 0, "s_name": "大鼠疫", "s_type": "combat_modifier", "s_val": -2.0, "s_dur": 4, "s_desc": "黑死病：三军战力强行削减2点"},
            {"title": "特大山洪暴发", "gold": -15, "food": -25, "land": -1, "s_name": None},
            {"title": "异端邪教煽动", "gold": -40, "food": -10, "land": 0, "s_name": "信仰动摇", "s_type": "gold_modifier", "s_val": -0.20, "s_dur": 4, "s_desc": "邪教横行：教民拒绝纳税致收益暴跌20%"},
            {"title": "寒冬暴雪冻害", "gold": 0, "food": -45, "land": 0, "s_name": "凛冬已至", "s_type": "food_modifier", "s_val": -0.25, "s_dur": 3, "s_desc": "极端冰冻：庄稼持续被冻死减产25%"},
            {"title": "码头突发火灾", "gold": -50, "food": 0, "land": 0, "s_name": None},
            {"title": "贵族领主抗税", "gold": -60, "food": 0, "land": 0, "s_name": "诸侯离心", "s_type": "gold_modifier", "s_val": -0.25, "s_dur": 5, "s_desc": "领主抗税：王室中央财政缩水25%"},
            {"title": "麦田根腐病害", "gold": 0, "food": -35, "land": 0, "s_name": "根腐病灾", "s_type": "food_modifier", "s_val": -0.20, "s_dur": 3, "s_desc": "根腐毒菌：本土农业减产20%"},
            {"title": "境内山贼袭掠", "gold": -30, "food": -15, "land": 0, "s_name": None},
            {"title": "强震摧毁村庄", "gold": -25, "food": -25, "land": -1, "s_name": None},
            {"title": "疯王胡乱挥霍", "gold": -80, "food": -10, "land": 0, "s_name": None},
            {"title": "邻国商路断绝", "gold": -45, "food": -10, "land": 0, "s_name": "商贸封锁", "s_type": "gold_modifier", "s_val": -0.30, "s_dur": 4, "s_desc": "边境关停：海外贸易税收锐减30%"},
            {"title": "皇家马瘟爆发", "gold": -15, "food": -30, "land": 0, "s_name": "战马疫症", "s_type": "combat_modifier", "s_val": -3.0, "s_dur": 3, "s_desc": "骑士无马：全军突击力永久折损3点"},
            {"title": "乱党刺杀重臣", "gold": -40, "food": 0, "land": -1, "s_name": None},
            {"title": "盐井透水废弃", "gold": -55, "food": -5, "land": 0, "s_name": None},
            {"title": "庄稼连阴腐烂", "gold": 0, "food": -40, "land": 0, "s_name": "连绵淫雨", "s_type": "food_modifier", "s_val": -0.15, "s_dur": 4, "s_desc": "久雨不晴：收成霉变减产15%"},
            {"title": "宗教异端审判", "gold": -35, "food": -15, "land": -1, "s_name": "狂热内耗", "s_type": "gold_modifier", "s_val": -0.10, "s_dur": 3, "s_desc": "人人自危：审判开销致财政减损10%"}
        ]
        
        self.log_history = [f"[帝国纪元] 【{self.lord_name}】登基。当前难度：【{self.difficulty}】模式！"]
        self.current_options = []
        self.roll_cards()

    def get_army_summary(self):
        total_raw = sum(u.get("power", 0) for u in self.my_army_units)
        counts = {"步兵": 0, "骑兵": 0, "弓兵": 0, "特殊": 0}
        for u in self.my_army_units:
            t = u.get("type", "步兵")
            counts[t] = counts.get(t, 0) + 1
        return total_raw, counts

    def get_tech_name(self):
        return self.tech_tree[self.tech_level - 1]

    def get_active_modifier(self, mod_type):
        val = 0.0 if mod_type != "combat_modifier" else 0
        for s in self.active_statuses:
            if s["type"] == mod_type:
                val += s["value"]
        return val

    def roll_cards(self):
        pool = []
        for c in self.normal_deck:
            if "type" in c and c["type"] == "marry" and self.is_married: continue
            if "type" in c and c["type"] == "child" and not self.is_married: continue
            pool.append(c)
        self.current_options = random.sample(pool, 2)

    # ⚔️ 战术推演沙盘：兵种相克判定
    def calculate_selected_battle(self, enemy_name, enemy_units, selected_my_units):
        self.log_history.append(f"\n[前线战报] ⚔️【我方部队】 VS 【{enemy_name}】")
        
        my_counts = {"步兵": 0, "骑兵": 0, "弓兵": 0, "特殊": 0}
        for u in selected_my_units: my_counts[u["type"]] = my_counts.get(u["type"], 0) + 1
            
        enemy_counts = {"步兵": 0, "骑兵": 0, "弓兵": 0, "特殊": 0}
        enemy_raw_power = 0
        for e in enemy_units:
            enemy_counts[e["type"]] += 1
            enemy_raw_power += e["power"]

        # 1.5倍杀伤相克
        my_bonus = min(my_counts["步兵"], enemy_counts["骑兵"]) * 1.5 + min(my_counts["骑兵"], enemy_counts["弓兵"]) * 1.5 + min(my_counts["弓兵"], enemy_counts["步兵"]) * 1.5
        enemy_bonus = min(enemy_counts["步兵"], my_counts["骑兵"]) * 1.5 + min(enemy_counts["骑兵"], my_counts["弓兵"]) * 1.5 + min(enemy_counts["弓兵"], my_counts["步兵"]) * 1.5

        religion_combat_bonus = len(selected_my_units) if self.religion == "战神铁血宗" else 0
        combat_disaster_debuff = self.get_active_modifier("combat_modifier")

        my_final_power = sum(u["power"] for u in selected_my_units) + my_bonus + self.plot_assassination_bonus + religion_combat_bonus + combat_disaster_debuff
        my_final_power = max(1.0, my_final_power)
        enemy_final_power = enemy_raw_power + enemy_bonus
        
        if religion_combat_bonus > 0:
            self.log_history.append(f" >> [战神铁血] 战吼狂热：全军实战杀伤力永久提升 +{religion_combat_bonus}！")
        if combat_disaster_debuff < 0:
            self.log_history.append(f" >> [国难重挫] 战意低迷，受到持续状态强行扣减 {abs(combat_disaster_debuff)} 点威力！")
            
        self.plot_assassination_bonus = 0 
        self.log_history.append(f" ⚖️ 沙盘对撞：我军实战力 {my_final_power:.1f} VS 敌军守备力 {enemy_final_power:.1f}")

        if my_final_power >= enemy_final_power:
            # 唯金教溃逃惩罚
            loss_rate = 0.40 if self.religion == "隐秘唯金教" else 0.20
            # 难度对战损概率的修正
            if self.difficulty == "简单": loss_rate *= 0.5
            if self.difficulty == "地狱": loss_rate *= 1.5

            loss_num = max(0, int(len(selected_my_units) * loss_rate))
            for _ in range(loss_num):
                if selected_my_units:
                    lost_u = selected_my_units.pop(random.randint(0, len(selected_my_units)-1))
                    if lost_u in self.my_army_units: self.my_army_units.remove(lost_u)
            self.log_history.append(f" 🎉【胜利】 艰难击退异端势力！我方不幸折损 {loss_num} 队编制。")
            return True
        else:
            self.log_history.append(" ❌【大败】 派往沙盘中央的前线主战部队全部战死！")
            for lost_u in selected_my_units:
                if lost_u in self.my_army_units: self.my_army_units.remove(lost_u)
            return False

    def next_turn_phase(self):
        if self.is_game_over: return
        self.year += 1
        if self.year % 3 == 0 and self.tech_level < 20: self.tech_level += 1

        # 更新并剔除过期持续天灾Buff
        remaining_statuses = []
        for s in self.active_statuses:
            s["remains"] -= 1
            if s["remains"] > 0:
                remaining_statuses.append(s)
            else:
                self.log_history.append(f" ✨ [国运回暖] 持续灾厄【{s['name']}】的影响终于消散了。")
        self.active_statuses = remaining_statuses

        # 兵力维护开销（简单模式下维护成本极低）
        army_size = len(self.my_army_units)
        if self.difficulty == "简单":
            food_drain = (army_size // 6)
            gold_drain = (army_size // 8)
        elif self.difficulty == "地狱":
            food_drain = (army_size // 2 + 2)
            gold_drain = (army_size // 3 + 2)
        else: # 普通
            food_drain = (army_size // 3 + 1)
            gold_drain = (army_size // 4 + 1)
        
        self.food -= food_drain
        self.gold -= gold_drain

        if self.gold < 0 or self.food < 0:
            self.is_game_over = True
            self.log_history.append("[覆灭原因] 国库彻底破产，或全军断粮引发军变！游戏结束。")
            return

        self.age += 1
        if self.age >= 60:
            self.trigger_inheritance()
            return
        self.roll_cards()

    def execute_card(self, c):
        g_mod = c["gold"]
        f_mod = c["food"]
        
        if self.religion == "隐秘唯金教" and g_mod > 0: g_mod = int(g_mod * 1.2)
        if self.religion == "圣天主教派" and c.get("type") == "child": f_mod = max(-2, f_mod // 2)

        # 🔮 持续天灾在执行卡牌时的直接系数影响
        if g_mod > 0:
            gold_debuff_rate = self.get_active_modifier("gold_modifier")
            g_mod = int(g_mod * (1.0 + gold_debuff_rate))
        if f_mod > 0:
            food_debuff_rate = self.get_active_modifier("food_modifier")
            f_mod = int(f_mod * (1.0 + food_debuff_rate))

        # 宗教什一税/内政废弛惩罚
        if self.religion == "圣天主教派" and g_mod > 0:
            tax = int(g_mod * 0.25)
            g_mod -= tax
            self.log_history.append(f" ⛪ [什一税] 圣座强征了你 {tax} 金币。")
        if self.religion == "战神铁血宗" and f_mod > 0:
            waste = int(f_mod * 0.35)
            f_mod -= waste
            self.log_history.append(f" 🛡️ [内政废弛] 全民崇武导致粮食减产 -{waste} 粮。")

        if self.gold < abs(g_mod) or self.food < abs(f_mod):
            self.execute_rest()
            return
            
        self.gold += g_mod; self.food += f_mod; self.land += c["land"]
        if c.get("type") == "marry": self.is_married = True
        if c.get("type") == "child": self.children_count += 1
        self.next_turn_phase()

    def execute_rest(self):
        gold_income = self.land * 3
        food_income = self.land * 4
        
        # 简单模式下休养生息获得双倍低保
        if self.difficulty == "简单":
            gold_income *= 2
            food_income *= 2

        gold_debuff_rate = self.get_active_modifier("gold_modifier")
        gold_income = int(gold_income * (1.0 + gold_debuff_rate))
        food_debuff_rate = self.get_active_modifier("food_modifier")
        food_income = int(food_income * (1.0 + food_debuff_rate))

        if self.religion == "隐秘唯金教": gold_income = int(gold_income * 1.2)
        elif self.religion == "圣天主教派":
            tax = int(gold_income * 0.25)
            gold_income -= tax
        if self.religion == "战神铁血宗":
            waste = int(food_income * 0.35)
            food_income -= waste

        self.gold += max(0, gold_income)
        self.food += max(0, food_income)
        self.next_turn_phase()

    def execute_recruit(self, u):
        if any(exist.get("title", "") == u["title"] for exist in self.my_army_units):
            self.log_history.append(f"[军事署] 【{u['title']}】为唯一编制，不可重组！")
            return
        cost = u["gold"]
        if self.difficulty == "简单": cost = int(cost * 0.7) # 简单模式买兵打折
        if self.gold < cost: return
        self.gold -= cost
        self.my_army_units.append({"id": u["id"], "title": u["title"], "type": u["type"], "power": u["army"]})
        self.log_history.append(f"[军备] 扩组【{u['title']}】")

    def execute_plot_item(self, p):
        cost = p["cost_gold"]
        if self.religion == "隐秘唯金教" and cost > 0: cost = int(cost * 0.8)
        if self.gold < cost or len(self.my_army_units) < p["need_army"]: return
        
        self.gold -= cost
        if p["need_army"] > 0: self.my_army_units.pop() 
        
        if p["id"] == 1: self.plot_assassination_bonus += 6
        elif p["id"] == 2: self.plot_assassination_bonus += 5
        elif p["id"] == 3: self.land += 1
        elif p["id"] == 4: self.plot_assassination_bonus += 12
        elif p["id"] == 5: self.food += 20
        elif p["id"] == 6: self.food -= 20; self.gold += 50
        elif p["id"] == 9: self.my_army_units.append({"id": 8, "title": "08.拜占庭圣骑兵", "type": "骑兵", "power": 12})
        elif p["id"] == 10: self.children_count += 1
        
        self.log_history.append(f"🔮 [密谋] 【{p['title']}】成功执行！")

    def trigger_inheritance(self):
        if self.children_count > 0:
            self.generation += 1; self.age = 18; self.is_married = False; self.children_count = 0
            self.year = 1
            self.active_statuses = []
            self.my_army_units = [{"id": 1, "title": "01.征召轻步兵", "type": "步兵", "power": 2} for _ in range(4)]
            if self.religion == "圣天主教派": self.gold += 80
        else:
            self.is_game_over = True
            self.log_history.append("[覆灭] 皇室绝嗣崩塌，帝国宣告沦陷！")

# ==================== 2. Kivy UI 渲染与排版层 ====================
class GameScreen(BoxLayout):
    def __init__(self, chosen_name, chosen_religion, chosen_diff, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 6; self.spacing = 4
        self.core = KingdomCore(chosen_name, chosen_religion, chosen_diff)

        # 1. 顶部状态监控板
        self.status_layout = GridLayout(cols=2, size_hint_y=0.25, spacing=2)
        self.lbl_lord = Label(text="", font_size='13sp', bold=True)
        self.lbl_age = Label(text="", font_size='12sp')
        self.lbl_resource = Label(text="", font_size='12sp', color=get_color_from_hex("#FFD700"))
        self.lbl_debuffs = Label(text="", font_size='11sp', color=get_color_from_hex("#E74C3C"))
        
        self.status_layout.add_widget(self.lbl_lord); self.status_layout.add_widget(self.lbl_age)
        self.status_layout.add_widget(self.lbl_resource); self.status_layout.add_widget(self.lbl_debuffs)
        self.add_widget(self.status_layout)

        # 2. 中央宏观战报记录流
        self.scroll_view = ScrollView(size_hint_y=0.30, do_scroll_x=False)
        self.lbl_log = Label(text="", font_size='11sp', size_hint_y=None, halign='left', valign='top', padding=(6, 6))
        self.lbl_log.bind(texture_size=lambda inst, val: setattr(inst, 'size', val))
        self.scroll_view.add_widget(self.lbl_log)
        self.add_widget(self.scroll_view)

        # 3. 核心内政交互决策手牌
        self.action_layout = BoxLayout(orientation='horizontal', size_hint_y=0.22, spacing=4)
        self.btn_c0 = Button(text="", background_color=get_color_from_hex("#2C3E50"), font_size='10sp')
        self.btn_c0.bind(on_press=lambda x: self.on_card_click(0))
        self.btn_c1 = Button(text="", background_color=get_color_from_hex("#2C3E50"), font_size='10sp')
        self.btn_c1.bind(on_press=lambda x: self.on_card_click(1))
        self.btn_rest = Button(text="[内政修养]", background_color=get_color_from_hex("#27AE60"), font_size='11sp', bold=True)
        self.btn_rest.bind(on_press=self.on_rest_click)
        self.action_layout.add_widget(self.btn_c0); self.action_layout.add_widget(self.btn_c1); self.action_layout.add_widget(self.btn_rest)
        self.add_widget(self.action_layout)

        # 4. 🧭 战术决策大本营
        self.sub_layout = BoxLayout(orientation='horizontal', size_hint_y=0.23, spacing=4)
        self.btn_pop_army = Button(text="⚔️ [皇家军事署]\n(正规军团)", background_color=get_color_from_hex("#C0392B"), font_size='10sp', bold=True, halign='center')
        self.btn_pop_army.bind(on_press=self.show_army_popup)
        
        self.btn_active_war = Button(text="🏹 [点兵远征]\n(疆土开拓)", background_color=get_color_from_hex("#D35400"), font_size='10sp', bold=True, halign='center')
        self.btn_active_war.bind(on_press=self.on_active_war_click)
        
        self.btn_pop_plot = Button(text="🔮 [暗夜影子密谋]\n(颠覆政体)", background_color=get_color_from_hex("#8E44AD"), font_size='10sp', bold=True, halign='center')
        self.btn_pop_plot.bind(on_press=self.show_plot_popup)
        
        self.sub_layout.add_widget(self.btn_pop_army); self.sub_layout.add_widget(self.btn_active_war); self.sub_layout.add_widget(self.btn_pop_plot)
        self.add_widget(self.sub_layout)

        self.update_ui()

    def update_ui(self):
        c = self.core
        raw_power, arm_counts = c.get_army_summary()
        self.lbl_lord.text = f"[领主] {c.lord_name} ({c.generation}代) | 难度: 👑{c.difficulty}\n⛪信仰: {c.religion} | 领土: {c.land} | 储君: {c.children_count}"
        self.lbl_age.text = f"[时间轴] {c.age}岁 | 统御第 {c.year} 年\n[科技] {c.get_tech_name()}"
        self.lbl_resource.text = f"💰 国库: {c.gold}   🌾 粮仓: {c.food}\n💂 军团: {len(c.my_army_units)}队 (总力: {raw_power}) [步:{arm_counts['步兵']} 骑:{arm_counts['骑兵']} 弓:{arm_counts['弓兵']}]"
        
        if c.active_statuses:
            status_desc = "🚨 危机状态：\n" + "\n".join([f"• {s['desc']}(剩{s['remains']}年)" for s in c.active_statuses])
            self.lbl_debuffs.text = status_desc
        else:
            self.lbl_debuffs.text = "☀️ 国泰民安，暂无连年浩劫"

        self.lbl_log.text = "\n".join(c.log_history[-12:])
        if c.is_game_over:
            self.btn_c0.disabled = self.btn_c1.disabled = self.btn_rest.disabled = True
            self.btn_pop_army.disabled = self.btn_active_war.disabled = self.btn_pop_plot.disabled = True
            return

        for i, btn in enumerate([self.btn_c0, self.btn_c1]):
            card = c.current_options[i]
            btn.text = f"{card['title']}\n{card['desc']}\n金:{card['gold']} 粮:{card['food']}"

    def on_card_click(self, idx):
        self.core.execute_card(self.core.current_options[idx])
        self.trigger_难度核心大灾变检测() 
        self.update_ui()

    def on_rest_click(self, inst):
        self.core.execute_rest()
        self.trigger_难度核心大灾变检测()
        self.update_ui()

    # ⏳ 核心升级：包含“简单/普通/地狱”三档规则的动态状态发生器
    def trigger_难度核心大灾变检测(self):
        c = self.core
        if c.is_game_over: return
        
        enemy = []
        enemy_name = ""
        is_historical = False

        # 👑 1. 世纪宏观浩劫判定
        if c.year == 50:
            enemy_name = "深渊毁灭魔神降临（50年天劫）"
            coef = 12 if c.difficulty == "地狱" else (5 if c.difficulty == "简单" else 8)
            enemy = [{"type": "步兵", "power": coef} for _ in range(5)] + [{"type": "骑兵", "power": coef} for _ in range(5)]
            is_historical = True
        elif c.year == 80:
            enemy_name = "诸神黄昏天劫铁骑（80年灭世）"
            coef = 18 if c.difficulty == "地狱" else (8 if c.difficulty == "简单" else 12)
            enemy = [{"type": "骑兵", "power": coef} for _ in range(8)]
            is_historical = True
        
        # 👑 2. 日常动态随机灾厄生成器
        if not is_historical:
            if c.year <= c.protection_years:
                return # 处于当前难度的襁褓保护期
            
            if random.randint(0, 100) < c.disaster_chance:
                raw_dis = random.choice(c.disaster_deck_raw)
                
                # 动态难度计算参数
                gold_dmg = raw_dis["gold"]
                food_dmg = raw_dis["food"]
                land_dmg = raw_dis["land"]
                
                if c.difficulty == "简单":
                    gold_dmg = int(gold_dmg * 0.5)
                    food_dmg = int(food_dmg * 0.5)
                    land_dmg = 0 # 简单模式不扣地
                elif c.difficulty == "地狱":
                    gold_dmg = int(gold_dmg * 1.5)
                    food_dmg = int(food_dmg * 1.5)
                    if land_dmg == 0 and random.random() < 0.3: land_dmg = -1

                c.gold = max(0, c.gold + gold_dmg)
                c.food = max(0, c.food + food_dmg)
                c.land = max(1, c.land + land_dmg)
                
                # 🔮 持续恶性 Buff 状态动态系数注入
                if raw_dis["s_name"]:
                    dur = raw_dis["s_dur"]
                    val = raw_dis["s_val"]
                    
                    if c.difficulty == "简单":
                        dur = max(1, dur - 2)
                        val *= 0.5
                    elif c.difficulty == "地狱":
                        dur += 3
                        val *= 1.5
                        
                    desc = f"【{raw_dis['s_name']}】({c.difficulty}增强): 影响{dur}年, 效果修正 {val*100:.0f}%"
                    
                    status_obj = {"name": raw_dis["s_name"], "type": raw_dis["s_type"], "value": val, "remains": dur, "desc": desc}
                    
                    if not any(active["name"] == status_obj["name"] for active in c.active_statuses):
                        c.active_statuses.append(status_obj)
                        c.log_history.append(f"🌪️ [国难连击] 爆发天灾【{raw_dis['title']}】！国家陷入长期灾害梦魇！")
                else:
                    c.log_history.append(f"💥 [突发意外] 遭遇【{raw_dis['title']}】(损失 金:{gold_dmg} 粮:{food_dmg})")
                
                # 简单模式下，天灾不会附带蛮族趁火打劫
                if c.difficulty != "简单":
                    etype = random.choice(["步兵", "骑兵", "弓兵"])
                    enemy_name = f"趁火打劫的【{etype}方阵】蛮族寇仇"
                    b_count = random.randint(5, 9) if c.difficulty == "地狱" else random.randint(3, 6)
                    enemy = [{"type": etype, "power": 4} for _ in range(b_count)]
        
        # ⚔️ 3. 战场合围判定
        if enemy:
            if len(c.my_army_units) == 0:
                c.is_game_over = True
                c.log_history.append(f"\n🚫【国门失守 💀】 强敌踏平王都！由于你没有任何编制度御敌，国家沦陷灭亡！")
                self.update_ui()
                return
            self.show_tactical_battle_popup(enemy_name, enemy, is_invasion=True)

    def on_active_war_click(self, inst):
        if len(self.core.my_army_units) == 0:
            self.core.log_history.append("[统帅部] 没有可以调遣的出征编制！")
            self.update_ui()
            return
        etype = random.choice(["步兵", "骑兵", "弓兵"])
        enemy_name = f"割据一方的【强力{etype}守备团】"
        enemy = [{"type": etype, "power": 5} for _ in range(random.randint(3, 6))]
        self.show_tactical_battle_popup(enemy_name, enemy, is_invasion=False)

    # 📊 战术推演多维动态沙盘
    def show_tactical_battle_popup(self, enemy_name, enemy_units, is_invasion=False):
        main_box = BoxLayout(orientation='vertical', padding=8, spacing=6)
        
        e_counts = {"步兵": 0, "骑兵": 0, "弓兵": 0, "特殊": 0}
        e_power = sum(e["power"] for e in enemy_units)
        for e in enemy_units: e_counts[e["type"]] += 1
        
        info_text = f"【战场前线情报】\n对决敌寇: {enemy_name} | 敌方账面战斗总力: {e_power}\n密探敌阵: 步兵×{e_counts['步兵']} | 骑兵×{e_counts['骑兵']} | 弓兵×{e_counts['弓兵']}\n\n💡 兵种相克：步克骑、骑克弓、弓克步。请勾选集结哪些主力方阵冲锋："
        main_box.add_widget(Label(text=info_text, font_size='12sp', color=get_color_from_hex("#E74C3C"), size_hint_y=0.25))
        
        scroll = ScrollView(size_hint_y=0.6)
        grid = GridLayout(cols=1, spacing=3, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        checkbox_map = [] 
        for u in self.core.my_army_units:
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=32)
            cb = CheckBox(size_hint_x=0.15, active=True) 
            lbl = Label(text=f"{u['title']} ({u['type']} | 战力:{u['power']})", font_size='11sp', halign='left', size_hint_x=0.85)
            row.add_widget(cb); row.add_widget(lbl)
            grid.add_widget(row)
            checkbox_map.append((cb, u))
            
        scroll.add_widget(grid)
        main_box.add_widget(scroll)

        def confirm_battle_dispatch(instance):
            selected_units = [unit for cb, unit in checkbox_map if cb.active]
            if not selected_units: return 
            
            popup.dismiss()
            win = self.core.calculate_selected_battle(enemy_name, enemy_units, selected_units)
            if win:
                if not is_invasion:
                    self.core.land += 2; self.core.gold += 60
                    self.core.log_history.append("🎖️【远征大捷】 成功兼并敌方2块沃土，掠夺60战利品金！")
            else:
                # 战败惩罚：根据难度产生连锁破坏
                if is_invasion:
                    if self.core.difficulty == "简单":
                        self.core.gold = max(0, self.core.gold - 20)
                        self.core.log_history.append("🚫【战败警告】 边境失守，好在亲卫队及时救援，仅损失20修缮金。")
                    elif self.core.difficulty == "地狱":
                        self.core.land = max(1, self.core.land - 4)
                        self.core.gold = max(0, self.core.gold - 150)
                        self.core.log_history.append("🚫【国破割地】 地狱诸侯溃败！强行割让4块大片疆土，暴扣150赔款金！")
                    else: # 普通
                        self.core.land = max(1, self.core.land - 2)
                        self.core.gold = max(0, self.core.gold - 80)
                        self.core.log_history.append("🚫【失地赔款】 敌军打破防线，强行划走2块疆土并洗劫80国库！")
            
            if not is_invasion: self.core.next_turn_phase()
            self.update_ui()

        btn_fight = Button(text="⚔️ 部署完毕，全军突击！", background_color=get_color_from_hex("#2980B9"), size_hint_y=0.15, bold=True)
        btn_fight.bind(on_press=confirm_battle_dispatch)
        main_box.add_widget(btn_fight)

        title_tag = "🚨 寇仇入侵！" if is_invasion else "🏹 统帅征伐"
        popup = Popup(title=f"{title_tag} - 【{enemy_name}】", content=main_box, size_hint=(0.95, 0.9))
        popup.open()

    def show_army_popup(self, inst):
        scroll = ScrollView(do_scroll_x=False)
        box = GridLayout(cols=1, spacing=4, size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))
        owned_titles = [exist.get("title", "") for exist in self.core.my_army_units]
        
        def make_click_handler(selected_unit):
            return lambda x: [self.core.execute_recruit(selected_unit), self.update_ui(), popup.dismiss()]

        for u in self.core.army_shop:
            is_owned = u["title"] in owned_titles
            suffix = " [全军在列]" if is_owned else ""
            cost = u["gold"]
            if self.core.difficulty == "简单": cost = int(cost * 0.7)
            btn = Button(text=f"{u['title']}{suffix} ({u['type']} | 耗资:{cost}金 | 战力:{u['army']})", size_hint_y=None, height=40, font_size='11sp')
            if is_owned: btn.background_color = get_color_from_hex("#7F8C8D")
            btn.bind(on_press=make_click_handler(u))
            box.add_widget(btn)
            
        scroll.add_widget(box)
        popup = Popup(title="⚔️ [皇家军事署 - 中世纪正规军王牌编制]", content=scroll, size_hint=(0.95, 0.85))
        popup.open()

    def show_plot_popup(self, inst):
        scroll = ScrollView(do_scroll_x=False)
        box = GridLayout(cols=1, spacing=4, size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))
        
        def make_plot_handler(selected_plot):
            return lambda x: [self.core.execute_plot_item(selected_plot), self.update_ui(), popup.dismiss()]

        for p in self.core.plot_shop:
            cost = p["cost_gold"]
            if self.core.religion == "隐秘唯金教" and cost > 0: cost = int(cost * 0.8)
            btn = Button(text=f"{p['title']} \n({p['desc']} | 暗中调度开销:{cost}金币)", size_hint_y=None, height=48, font_size='10sp', halign='center')
            btn.bind(on_press=make_plot_handler(p))
            box.add_widget(btn)
            
        scroll.add_widget(box)
        popup = Popup(title="🔮 [暗夜影子内阁 - 十大高级密谋策略卡]", content=scroll, size_hint=(0.95, 0.85))
        popup.open()

class LordApp(App):
    def __init__(self, name_input, religion_input, diff_input, **kwargs):
        super().__init__(**kwargs)
        self.name_input = name_input
        self.religion_input = religion_input
        self.diff_input = diff_input
    def build(self): return GameScreen(self.name_input, self.religion_input, self.diff_input)

if __name__ == '__main__':
    print("==================================================")
    print("        👑 《王权领主：沙盘推演》多难度重构版 👑     ")
    print("==================================================")
    user_name = input("请输入您神圣帝国的皇室御姓：").strip()
    if not user_name: user_name = "卡佩"
    
    print("\n请选择您的挑战难度级别：")
    print("1. 🟢 简单模式 (初始金粮极多、天灾时间及负荷折半、前20年绝对免战保底)")
    print("2. 🟡 普通模式 (标准数值博弈、机制平衡、适合稳健推进型策略玩家)")
    print("3. 🔴 地狱模式 (资源极度匮乏、超高连环灾厄爆发、战败强行割地灭国)")
    diff_choice = input("请输入难度编号 (1-3)：").strip()
    diff_map = {"1": "简单", "2": "普通", "3": "地狱"}
    chosen_diff = diff_map.get(diff_choice, "普通")

    print("\n请选择帝国的终极信仰：")
    print("1. ✝️ 圣天主教派 (正面: 繁衍耗粮减半/登基送80金 | 负面: 内政强征 25% 宗教什一税)")
    print("2. 🛡️ 战神铁血宗 (正面: 常备军战斗威力全线+1  | 负面: 举国不事农桑，内政卡粮食产量暴跌 35%)")
    print("3. 🪙 隐秘唯金教 (正面: 资本充沛卡收益增幅+20% | 负面: 佣兵毫无信仰，战败折损溃逃率翻倍)")
    choice = input("请输入信仰编号 (1-3)：").strip()
    rel_map = {"1": "圣天主教派", "2": "战神铁血宗", "3": "隐秘唯金教"}
    chosen_rel = rel_map.get(choice, "圣天主教派")
    
    print(f"\n沙盘核心重组完毕！")
    print(f"帝国难度设定为【{chosen_diff}】，国教正式立为【{chosen_rel}】。")
    print("沙盘引擎启动中，祝陛下旗开得胜！\n")
    LordApp(name_input=user_name, religion_input=chosen_rel, diff_input=chosen_diff).run()