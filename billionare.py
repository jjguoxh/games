import random
import os

class Property:
    def __init__(self, name, price, rent):
        self.name = name
        self.price = price
        self.rent = rent
        self.owner = None
        self.houses = 0
        self.hotel = False
    
    def buy(self, player):
        if player.money >= self.price:
            player.money -= self.price
            self.owner = player
            player.properties.append(self)
            return True
        return False
    
    def calculate_rent(self):
        if self.hotel:
            return self.rent * 5
        elif self.houses > 0:
            return self.rent * self.houses
        else:
            return self.rent
    
    def build_house(self):
        if self.owner and self.owner.money >= self.price // 2:
            if self.houses < 4 and not self.hotel:
                self.owner.money -= self.price // 2
                self.houses += 1
                return True
        return False
    
    def build_hotel(self):
        if self.owner and self.houses == 4 and not self.hotel:
            if self.owner.money >= self.price:
                self.owner.money -= self.price
                self.houses = 0
                self.hotel = True
                return True
        return False

class Player:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.position = 0
        self.money = 1500
        self.properties = []
        self.in_jail = False
        self.jail_turns = 0
    
    def move(self, steps, board_size):
        self.position = (self.position + steps) % board_size
        return self.position
    
    def pay_rent(self, amount, owner):
        if self.money >= amount:
            self.money -= amount
            owner.money += amount
            return True
        return False
    
    def can_afford(self, amount):
        return self.money >= amount

class Game:
    def __init__(self):
        self.players = []
        self.properties = []
        self.current_player_index = 0
        self.board_size = 20
        self.init_board()
    
    def init_board(self):
        # 创建地产
        property_names = [
            "地中海大道", "波罗的海大道", "东方大道", "佛蒙特大道", "康涅狄格大道",
            "圣查尔斯广场", "各州大道", "弗吉尼亚大道", "圣詹姆斯广场", "田纳西大道",
            "纽约大道", "肯塔基大道", "印第安纳大道", "伊利诺伊大道", "大西洋大道",
            "文特诺大道", "马尔林大道", "太平洋大道", "北卡罗来纳大道", "宾夕法尼亚大道"
        ]
        
        for i, name in enumerate(property_names):
            price = random.randint(50, 300)
            rent = price // 10
            self.properties.append(Property(name, price, rent))
    
    def add_player(self, name, color):
        self.players.append(Player(name, color))
    
    def roll_dice(self):
        return random.randint(1, 6) + random.randint(1, 6)
    
    def get_current_player(self):
        return self.players[self.current_player_index]
    
    def next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
    
    def handle_property(self, player, position):
        property = self.properties[position]
        if property.owner is None:
            # 无人拥有的地产，可以购买
            print(f"{player.name} 到达 {property.name}，价格: ${property.price}")
            if player.can_afford(property.price):
                choice = input("是否购买? (y/n): ")
                if choice.lower() == 'y':
                    if property.buy(player):
                        print(f"{player.name} 购买了 {property.name}")
                    else:
                        print("购买失败")
                else:
                    print(f"{player.name} 放弃购买 {property.name}")
            else:
                print(f"{player.name} 无法负担 {property.name} 的价格")
        elif property.owner != player:
            # 别人拥有的地产，需要付租金
            rent = property.calculate_rent()
            print(f"{player.name} 到达 {property.name}，需要付租金 ${rent} 给 {property.owner.name}")
            if player.pay_rent(rent, property.owner):
                print(f"{player.name} 支付了租金")
            else:
                print(f"{player.name} 无法支付租金，破产!")
                # 移除破产玩家
                self.players.remove(player)
        else:
            # 自己拥有的地产，可以建设
            print(f"{player.name} 回到了自己的地产 {property.name}")
            if property.houses < 4 and not property.hotel:
                print(f"可以建设房屋，费用: ${property.price // 2}")
                if player.can_afford(property.price // 2):
                    choice = input("是否建设房屋? (y/n): ")
                    if choice.lower() == 'y':
                        if property.build_house():
                            print("房屋建设成功!")
                        else:
                            print("房屋建设失败")
            elif property.houses == 4 and not property.hotel:
                print(f"可以建设酒店，费用: ${property.price}")
                if player.can_afford(property.price):
                    choice = input("是否建设酒店? (y/n): ")
                    if choice.lower() == 'y':
                        if property.build_hotel():
                            print("酒店建设成功!")
                        else:
                            print("酒店建设失败")
    
    def display_board(self):
        print("\n" + "="*50)
        print("地产列表:")
        for i, prop in enumerate(self.properties):
            owner_name = prop.owner.name if prop.owner else "无"
            print(f"{i:2d}. {prop.name:15s} 价格:${prop.price:3d} 租金:${prop.rent} 拥有者:{owner_name}")
        print("="*50)
    
    def display_players(self):
        print("\n玩家状态:")
        for player in self.players:
            properties_str = ", ".join([p.name for p in player.properties])
            print(f"{player.name}({player.color}): ${player.money} 位置:{player.position} 地产:[{properties_str}]")
    
    def play_turn(self):
        player = self.get_current_player()
        print(f"\n{player.name} 的回合")
        
        # 掷骰子
        dice_roll = self.roll_dice()
        print(f"{player.name} 掷出了 {dice_roll}")
        
        # 移动
        new_position = player.move(dice_roll, self.board_size)
        property = self.properties[new_position]
        print(f"{player.name} 移动到 {property.name}")
        
        # 处理地产
        self.handle_property(player, new_position)
        
        # 显示状态
        self.display_players()
        
        # 切换到下一个玩家
        self.next_player()
    
    def is_game_over(self):
        return len(self.players) <= 1
    
    def start_game(self):
        print("欢迎来到大富翁游戏!")
        print("游戏规则:")
        print("1. 每位玩家初始资金 $1500")
        print("2. 到达无主地产可以购买")
        print("3. 到达他人地产需要支付租金")
        print("4. 在自己地产上可以建设房屋和酒店")
        print("5. 玩家无法支付租金时破产")
        print("6. 最后剩下的玩家获胜!")
        
        # 添加玩家
        num_players = int(input(f"请输入玩家数量 (2-4): "))
        colors = ["红色", "蓝色", "绿色", "黄色"]
        for i in range(num_players):
            name = input(f"请输入玩家 {i+1} 的名字: ")
            self.add_player(name, colors[i])
        
        # 游戏主循环
        while not self.is_game_over():
            input("\n按回车键继续...")
            os.system('cls' if os.name == 'nt' else 'clear')
            self.display_board()
            self.play_turn()
        
        if self.players:
            print(f"\n游戏结束! {self.players[0].name} 获胜!")
        else:
            print("\n游戏结束!")

# 运行游戏
if __name__ == "__main__":
    game = Game()
    game.start_game()