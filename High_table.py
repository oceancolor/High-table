import openpyxl
from openpyxl import load_workbook
import random
from  pandas import *

#静态配置数据
ROUND_COST = 10 #每团队成员每回合固定成本开销，类似于公司每月人力成本开支
ROUND_LIMIT = 25 #回合数限制为最大25，到达此值后无论位于哪个环节都强制结束并计算得分和横向对比
INIT_RESOURCE = 10 #初始项目可配资源点
products = []

class Product:
    def __init__(self):
        #类型数据
        self.type = 0
        self.name = ''
        ####积累型数值的权重值用于计算总体评价分
        self.user_pool = 0
        self.user_weight = 0.0
        self.money = 0
        self.money_weight = 0.0
        self.team_numbers = 0
        self.team_weight = 0.0
        self.tech = 0
        self.tech_weight = 0.0
        ########成本消耗值，也是积累型，不同产品的成本系数不同，在一个回合中消耗的量也不一样
        self.cost = 0
        self.cost_rate = 0.0
        #################以下为动态系数数值
        self.risk_rate = 0.0
        self.risk_value = 0
        self.income_ability = 0.0
        self.income_exp = 0
        self.life_exp = 0
        self.life_factor = 0.0
        self.state = 0
        self.quality = 0
        self.opportunity = 0
        self.expirence = 0
        self.reputation = 0
        self.score = 0
        #回合数据和活动选择属性
        self.round_count = 0
        self.past_block = 0
        self.current_block = 0
        self.pre_block = 0
        self.activity = 0
        self.bonus = 0

    def update(self):
        #除了activity中不同活动的数值改变之外，每个回合例行的改变在此函数中处理
        #显示当前回合数，当前所在的地图块是何种性质，如果是pk回合，则说明PK的对方有哪些，PK的结果会怎样
        self.round_count += 1
        self.past_block = self.current_block
        self.current_block = self.pre_block
        #用户值变化
        self.user_pool += 0
        #金钱值变化
        #self.cost_rate已经在activity.do函数中改变过了
        round_cost = ROUND_COST * self.team_numbers * self.cost_rate
        self.money -= round_cost
        #产品状态
        if self.state == 0:
            print("产品状态 - 初始态")
        elif self.state == 1:
            print("产品状态 - 预备态")
        elif self.state == 2:
            print("产品状态 - 关键态")
        elif self.state == 3:
            print("产品状态 - 完整态")
        elif self.state == 4:
            print("产品状态 - 运营态")

    def summary(self):
        print("当前数据统计")
        #产品状态
        print("    产品状态: ", self.state)
        if self.state == 0:
            print("        初始态")
        elif self.state == 1:
            print("        预备态")
        elif self.state == 2:
            print("        关键态")
        elif self.state == 3:
            print("        完整态")
        elif self.state == 4:
            print("        运营态")
        print("           总评分: ", self.score)
        print("               资金实力: ", self.money)
        print("               团队规模: ", self.team_numbers)
        print("               核心用户: ", self.user_pool)
        print("               技术壁垒: ", self.team_numbers)
        print("               质量:", self.quality)
        print("               机会:", self.opportunity)
        print("               体验:", self.expirence)
        print("               美誉:", self.reputation)
        print("               预期收入规模:", self.income_exp)
        print("               预期生命周期:", self.life_exp)

    def after_update(self):
        if self.current_block == 18 or self.round_count >= ROUND_LIMIT:
            print("已经完成最后一个回合，或当前所在位置：Block", self.current_block, "已达结束游戏")
            self.summary()
        else:
            self.pre_block = int(input("请选择你下一回合去往哪个区块？(必须是相邻且不能后退到前一回合的区块）"))
            if self.pre_block < 0:
                self.pre_block = 0
            while self.pre_block == self.past_block:
                print("你返回了前一回合所在区块，请重新选择")
                self.pre_block = int(input("请选择你下一回合去往哪个区块？(必须是相邻且不能后退到前一回合的区块）"))
            #检查相邻性

class Activity:
    def __init__(self, id):
        self.name = ""
        #短期资源,增减效果立即呈现
        self.money_change = 0.0
        self.user_change = 0.0
        self.team_change = 0.0
        self.tech_change = 0.0
        #系数变化涉及长期潜力
        self.risk_change = 0.0
        self.earn_change = 0.0
        self.life_change = 0.0
        self.cost_rate_change = 0.0
        #四项隐藏属性的变化
        self.quanlity_change = 0.0
        self.opportunity_change = 0.0
        self.experience_change = 0.0
        self.reputation_change = 0.0

        if id == 1:
            self.name = "业务建模" #花钱，增加团队成员，降低风险，增加盈利能力，增加生命周期，降低成本消耗率，机会增加
            self.money_change = -1.0
            self.team_change = +1.0
            self.risk_change = -0.2
            self.earn_chenge = +0.2
            self.life_chenge = +0.3
            self.cost_rate_change = -0.1
            self.opportunity_change = +0.1
        elif id == 2:
            self.name = "市场营销" #花钱，增加用户，损失技术积累，增加风险，增加盈利能力，增加生命周期， 美誉度增加
            self.money_change = -3.0
            self.user_change = +1.0
            self.tech_change = -0.1
            self.risk_change = +0.1
            self.earn_change = +0.3
            self.life_change = +0.1
            self.reputation_change = +0.1
        elif id == 3:
            self.name = "竞品分析" #花钱，团队跳槽，增加技术积累，降低风险，增加盈利能，增加成本消耗率,  机会增加
            self.money_change = -1.0
            self.team_change = -0.5
            self.tech_change = +0.1
            self.risk_change = -0.3
            self.earn_change = +0.1
            self.cost_rate_change = +0.1
            self.opportunity_change = +0.1
        elif id == 4:
            self.name = "产品体验" #损失团队，花钱，降低风险，增加盈利能力，增加生命周期,  用户体验增加
            self.team_change = -0.1
            self.money_change = -0.1
            self.risk_change = -0.1
            self.earn_change = +0.1
            self.life_change = +0.1
            self.experience_change = +0.1
        elif id == 5:
            self.name = "技术评审" #耗用户，团队炒人，花钱，增加技术积累，降低风险，降低成本消耗率, 质量增加
            self.user_change = -0.1
            self.team_change = -0.1
            self.money_change = -0.1
            self.tech_change = +0.2
            self.risk_change = -0.5
            self.cost_rate_change = -0.1
            self.quanlity_change = +0.1
        elif id == 6:
            self.name = "用户参与" #花钱，耗用户，降低风险，增加盈利能力，增加生命周期，增加成本消耗率, 用户体验增加
            self.money_change = -1.0
            self.user_change = -0.1
            self.risk_change = -0.2
            self.earn_change = +0.1
            self.life_change = +0.1
            self.cost_rate_change = +0.2
            self.experience_change = +0.2
        elif id == 7:
            self.name = "研发攻坚" #花钱，增加用户数，团队离职，增加技术积累，增加风险, 增加质量
            self.money_change = -1.0
            self.user_change = +0.1
            self.team_change = -0.3
            self.tech_change = +0.2
            self.risk_change = +0.1
            self.quanlity_change = +0.2

    def do(self, product):
        print(product.name, " 选择了 ", self.name, " 项活动来进行此轮")
        product.cost += self.money_change
        product.money -= product.cost

        print("你成功进行了", self.name, "结算如下:\n")

        print("系统提出了 ", self.name, "相关的挑战问题, 你的回答是正确的吗？")
        result = input("N. 错误,  Y.正确\n")
        if result == 'Y':
            product.bonus = 2
            #print("回答正确获得可分配点数:"，product.bonus)
        else:
            print("回答错误，未获得分配点数")
      
        if product.money < 0:
            print("损失已经无可挽回,你已出局")
        #产生随机事件


#游戏局面作为一个类
class GameSituation:
    def __init__(self):
        self.round = 0
        self.vc_money = 1000
        self.game_market_risk = 10
        self.social_market_risk = 20
        self.eshop_market_risk = 2
        self.fundamental_market_risk = 8
        self.products = []
        self.player_count = 1

    def run(self, products):
        _temp = INIT_RESOURCE
        print("game running now...")
        self.player_count = int(input("几个玩家? [允许范围1-6]"))
        for i in range(self.player_count):
            products.append(Product())
            print("玩家 ", i, " 选择的产品类型是？[1-游戏, 2-社交, 3-电商, 4-基础]")
            products[i].type = int(input("请输入选择数字: "))
            if products[i].type > 4 or products[i].type < 1:
                products[i].type = 4
            products[i].name = input("给你的产品起个名字吧: ")
            print("给你的项目分配初始资源吧，共有[", INIT_RESOURCE, "点可分配在资金、用户池、技术壁垒、团队规模四项基本属性上，每项至少为1，计算好怎么分配吧！")
            #有INIT_RESOURCE个点可分配
            #分配资金值
            while products[i].money < 1 or products[i].money > INIT_RESOURCE - 3:
                products[i].money = int(input("初始资金:"))
            _temp -= products[i].money
            print(">还剩", _temp, "点可分配")
            #分配用户值
            while products[i].user_pool < 1 or products[i].user_pool > _temp - 2:
                products[i].user_pool = int(input("初始用户池:"))
            _temp -= products[i].user_pool
            print(">>还剩", _temp, "点可分配")
            #分配技术壁垒值
            while products[i].tech < 1 or products[i].tech > _temp - 1:
                products[i].tech = int(input("初始技术实力:"))
            _temp -= products[i].tech
            print(">>>剩", _temp, "点， 分配给团队规模")
            #分配团队规模值
            products[i].team_numbers = _temp
            _temp = INIT_RESOURCE

    def poll(self, products):
        for i in range(self.player_count):
            while products[i].bonus > 0:
                print("产品 : ", products[i].name, "有可分配点数 :", products[i].bonus , " 点可分配, 请输入要分配的项的序号[1-金钱， 2-用户， 3-团队， 4-技术]")
                item = int(input("请输入序号 :"))
                point = int(input("请输入分配的点数数字 :"))
                if products[i].bonus - point <= 0:
                    point = products[i].bonus
                products[i].bonus -= point

    def update(self, products):
        global business_modeling, marketing, competation_analyst, product_eval, technical_review, ce_activity, development
        self.round += 1
        #随机事件
        self.vc_money += random.randint(-20, 20)
        for i in range(self.player_count):
            print("第 ", i, " 号玩家，请为你的产品: ",  products[i].name, " 做出本回合工作规划，选择进行一项活动")
            products[i].activity = int(input("请选择做何种活动: [1-业务建模, 2-市场营销, 3-竞品分析, 4-产品体验, 5-技术评审, 6-用户参与, 7-研发攻坚]"))
            if products[i].activity == 1:
                business_modeling.do(products[i])
            elif products[i].activity == 2:
                marketing.do(products[i])
            elif products[i].activity == 3:
                competation_analyst.do(products[i])
            elif products[i].activity == 4:
                product_eval.do(products[i])
            elif products[i].activity == 5:
                technical_review.do(products[i])
            elif products[i].activity == 6:
                ce_activity.do(products[i])
            else:
                products[i].activity = 7
                development.do(products[i])
            #更新状态
            products[i].update()
            products[i].after_update()

    def show_state(self, products):
        print("目前回合数:",  self.round)
        print("当前盘面总结: ")
        for i in range(self.player_count):
            products[i].summary()

def main():
    global products
    global business_modeling
    global marketing
    global competation_analyst
    global product_eval
    global technical_review
    global ce_activity
    global development

    situation = GameSituation()
    situation.run(products)

    business_modeling = Activity(1)
    marketing = Activity(2)
    competation_analyst = Activity(3)
    product_eval = Activity(4)
    technical_review = Activity(5)
    ce_activity = Activity(6)
    development = Activity(7)

    while True:
        situation.poll(products)#plan
        situation.update(products)#deploy
        situation.show_state(products)#check

if __name__ == "__main__":
    main()
