import pygame
import random
import sys

# 初始化pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
CARD_WIDTH = 120
CARD_HEIGHT = 180
CARD_SPACING = 30
MINION_WIDTH = 100
MINION_HEIGHT = 100
MINION_SPACING = 20

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 128, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
BROWN = (139, 69, 19)

# 卡牌类型
CARD_TYPES = ['minion', 'spell', 'weapon']

# 随从类型
MINION_TYPES = [
    {'name': '鱼人战士', 'attack': 2, 'health': 1, 'cost': 1, 'color': BLUE},
    {'name': '狼骑兵', 'attack': 3, 'health': 1, 'cost': 2, 'color': GREEN},
    {'name': '石牙野猪', 'attack': 1, 'health': 1, 'cost': 1, 'color': GRAY},
    {'name': '狗头人地卜师', 'attack': 2, 'health': 2, 'cost': 2, 'color': PURPLE},
    {'name': '机械跃迁者', 'attack': 2, 'health': 3, 'cost': 3, 'color': LIGHT_GRAY},
    {'name': '暗鳞先知', 'attack': 2, 'health': 3, 'cost': 3, 'color': DARK_GRAY},
    {'name': '剃刀猎手', 'attack': 2, 'health': 3, 'cost': 3, 'color': BROWN},
    {'name': '碎雪机器人', 'attack': 2, 'health': 3, 'cost': 3, 'color': LIGHT_GRAY},
    {'name': '麦田傀儡', 'attack': 2, 'health': 3, 'cost': 3, 'color': YELLOW},
    {'name': '铁喙猫头鹰', 'attack': 2, 'health': 1, 'cost': 2, 'color': BROWN}
]


class Card:
    def __init__(self, card_type, data=None):
        self.card_type = card_type
        if card_type == 'minion' and data:
            self.name = data['name']
            self.cost = data['cost']
            self.attack = data['attack']
            self.health = data['health']
            self.color = data['color']
        elif card_type == 'spell':
            self.name = '火球术'
            self.cost = 4
            self.damage = 6
        elif card_type == 'weapon':
            self.name = '炽炎战斧'
            self.cost = 2
            self.attack = 3
            self.durability = 2


class Minion:
    def __init__(self, card):
        self.name = card.name
        self.attack = card.attack
        self.health = card.health
        self.max_health = card.health
        self.color = card.color
        self.can_attack = False  # 刚召唤的随从不能立即攻击

    def __str__(self):
        return f"{self.name} ({self.attack}/{self.health})"


class HearthstoneGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("炉石传说 - 简化版")
        self.clock = pygame.time.Clock()
        # 使用支持中文的字体
        font_paths = [
            "C:/Windows/Fonts/simhei.ttf",  # 黑体
            "C:/Windows/Fonts/simsun.ttc",  # 宋体
            "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
            "C:/Windows/Fonts/simkai.ttf",  # 楷体
        ]
        
        font_loaded = False
        for font_path in font_paths:
            try:
                self.font = pygame.font.Font(font_path, 24)
                self.large_font = pygame.font.Font(font_path, 36)
                self.small_font = pygame.font.Font(font_path, 20)
                print(f"成功加载字体: {font_path}")
                font_loaded = True
                break
            except:
                continue
        
        if not font_loaded:
            print("无法加载中文字体，使用默认字体")
            self.font = pygame.font.SysFont(None, 24)
            self.large_font = pygame.font.SysFont(None, 36)
            self.small_font = pygame.font.SysFont(None, 20)

        # 游戏状态
        self.player_mana = 1
        self.player_max_mana = 1
        self.enemy_mana = 1
        self.enemy_max_mana = 1

        # 卡牌和随从
        self.player_hand = []
        self.enemy_hand = []
        self.player_battlefield = []
        self.enemy_battlefield = []

        # 英雄
        self.player_hero_health = 30
        self.enemy_hero_health = 30
        self.player_hero_armor = 0
        self.enemy_hero_armor = 0

        # 拖拽状态
        self.dragging = False
        self.drag_card = None
        self.drag_offset = (0, 0)
        self.drag_source = None  # 'hand', 'battlefield'

        # 回合状态
        self.player_turn = True
        self.turn_number = 1

        # 游戏结束
        self.game_over = False
        self.player_won = False

        self.reset_game()

    def reset_game(self):
        # 重置游戏状态
        self.player_mana = 1
        self.player_max_mana = 1
        self.enemy_mana = 1
        self.enemy_max_mana = 1

        self.player_hand = []
        self.enemy_hand = []
        self.player_battlefield = []
        self.enemy_battlefield = []

        self.player_hero_health = 30
        self.enemy_hero_health = 30
        self.player_hero_armor = 0
        self.enemy_hero_armor = 0

        self.dragging = False
        self.drag_card = None
        self.drag_offset = (0, 0)
        self.drag_source = None

        self.player_turn = True
        self.turn_number = 1
        self.game_over = False
        self.player_won = False

        # 初始发牌
        self.draw_cards(3, 'player')  # 玩家初始3张牌
        self.draw_cards(4, 'enemy')  # 敌人初始4张牌

    def draw_cards(self, count, player):
        """抽牌"""
        for _ in range(count):
            if player == 'player':
                if len(self.player_hand) < 10:  # 手牌上限10张
                    card_data = random.choice(MINION_TYPES)
                    card = Card('minion', card_data)
                    self.player_hand.append(card)
            else:
                if len(self.enemy_hand) < 10:
                    card_data = random.choice(MINION_TYPES)
                    card = Card('minion', card_data)
                    self.enemy_hand.append(card)

    def end_turn(self):
        """结束回合"""
        if self.player_turn:
            # 玩家回合结束，轮到敌人
            self.player_turn = False

            # 敌人行动（简化AI）
            self.enemy_ai_turn()

            # 回到玩家回合
            self.player_turn = True
            self.turn_number += 1

            # 增加法力水晶
            if self.player_max_mana < 10:
                self.player_max_mana += 1
            if self.enemy_max_mana < 10:
                self.enemy_max_mana += 1

            self.player_mana = self.player_max_mana
            self.enemy_mana = self.enemy_max_mana

            # 抽牌
            self.draw_cards(1, 'player')
            self.draw_cards(1, 'enemy')

            # 随从可以攻击
            for minion in self.player_battlefield:
                minion.can_attack = True
            for minion in self.enemy_battlefield:
                minion.can_attack = True

    def enemy_ai_turn(self):
        """敌人AI回合（简化版）"""
        # 使用手牌
        for i, card in enumerate(self.enemy_hand):
            if card.card_type == 'minion' and card.cost <= self.enemy_mana:
                self.enemy_mana -= card.cost
                minion = Minion(card)
                self.enemy_battlefield.append(minion)
                self.enemy_hand.pop(i)
                break

    def can_play_card(self, card):
        """检查是否可以打出卡牌"""
        if not self.player_turn:
            return False
        return card.cost <= self.player_mana

    def play_card(self, card_index):
        """打出卡牌"""
        if not self.player_turn or card_index >= len(self.player_hand):
            return False

        card = self.player_hand[card_index]
        if not self.can_play_card(card):
            return False

        # 扣除法力值
        self.player_mana -= card.cost

        # 根据卡牌类型处理
        if card.card_type == 'minion':
            minion = Minion(card)
            minion.can_attack = False  # 新召唤的随从本回合不能攻击
            self.player_battlefield.append(minion)

        # 从手牌移除
        self.player_hand.pop(card_index)
        return True

    def attack(self, attacker_index, target_type, target_index):
        """攻击"""
        if not self.player_turn:
            return

        if attacker_index >= len(self.player_battlefield):
            return

        attacker = self.player_battlefield[attacker_index]
        if not attacker.can_attack:
            return

        # 处理攻击
        if target_type == 'minion':
            if target_index >= len(self.enemy_battlefield):
                return
            target = self.enemy_battlefield[target_index]

            # 互相造成伤害
            target.health -= attacker.attack
            attacker.health -= target.attack

            # 检查死亡
            if target.health <= 0:
                self.enemy_battlefield.pop(target_index)
            if attacker.health <= 0:
                self.player_battlefield.pop(attacker_index)
            else:
                attacker.can_attack = False

        elif target_type == 'hero':
            # 攻击敌方英雄
            if self.enemy_hero_armor > 0:
                if attacker.attack > self.enemy_hero_armor:
                    remaining_damage = attacker.attack - self.enemy_hero_armor
                    self.enemy_hero_armor = 0
                    self.enemy_hero_health -= remaining_damage
                else:
                    self.enemy_hero_armor -= attacker.attack
            else:
                self.enemy_hero_health -= attacker.attack

            attacker.can_attack = False

            # 检查游戏结束
            if self.enemy_hero_health <= 0:
                self.game_over = True
                self.player_won = True

    def get_card_at_pos(self, pos):
        """获取指定位置的卡牌"""
        x, y = pos

        # 检查手牌
        if self.player_turn:
            hand_start_x = (SCREEN_WIDTH - (len(self.player_hand) * (CARD_WIDTH + CARD_SPACING))) // 2
            hand_y = SCREEN_HEIGHT - CARD_HEIGHT - 20

            for i, card in enumerate(self.player_hand):
                card_x = hand_start_x + i * (CARD_WIDTH + CARD_SPACING)
                rect = pygame.Rect(card_x, hand_y, CARD_WIDTH, CARD_HEIGHT)
                if rect.collidepoint(x, y):
                    return ('hand', i, card)

        return None

    def get_minion_at_pos(self, pos):
        """获取指定位置的随从"""
        x, y = pos

        # 检查玩家战场随从
        battlefield_y = SCREEN_HEIGHT // 2 + 50
        if len(self.player_battlefield) > 0:
            total_width = len(self.player_battlefield) * (MINION_WIDTH + MINION_SPACING) - MINION_SPACING
            battlefield_start_x = (SCREEN_WIDTH - total_width) // 2

            for i, minion in enumerate(self.player_battlefield):
                minion_x = battlefield_start_x + i * (MINION_WIDTH + MINION_SPACING)
                rect = pygame.Rect(minion_x, battlefield_y, MINION_WIDTH, MINION_HEIGHT)
                if rect.collidepoint(x, y):
                    return ('player', i, minion)

        # 检查敌人战场随从
        battlefield_y = SCREEN_HEIGHT // 2 - MINION_HEIGHT - 50
        if len(self.enemy_battlefield) > 0:
            total_width = len(self.enemy_battlefield) * (MINION_WIDTH + MINION_SPACING) - MINION_SPACING
            battlefield_start_x = (SCREEN_WIDTH - total_width) // 2

            for i, minion in enumerate(self.enemy_battlefield):
                minion_x = battlefield_start_x + i * (MINION_WIDTH + MINION_SPACING)
                rect = pygame.Rect(minion_x, battlefield_y, MINION_WIDTH, MINION_HEIGHT)
                if rect.collidepoint(x, y):
                    return ('enemy', i, minion)

        return None

    def draw_card(self, card, x, y):
        """绘制卡牌"""
        rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        pygame.draw.rect(self.screen, WHITE, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 2)

        # 绘制费用
        cost_rect = pygame.Rect(x + 5, y + 5, 25, 25)
        pygame.draw.rect(self.screen, BLUE, cost_rect)
        pygame.draw.rect(self.screen, BLACK, cost_rect, 1)
        cost_text = self.font.render(str(card.cost), True, WHITE)
        self.screen.blit(cost_text, (x + 12, y + 8))

        # 绘制名称
        name_text = self.small_font.render(card.name, True, BLACK)
        self.screen.blit(name_text, (x + CARD_WIDTH // 2 - name_text.get_width() // 2, y + 40))

        if card.card_type == 'minion':
            # 绘制攻击力和生命值
            attack_rect = pygame.Rect(x + 5, y + CARD_HEIGHT - 30, 30, 25)
            pygame.draw.rect(self.screen, RED, attack_rect)
            pygame.draw.rect(self.screen, BLACK, attack_rect, 1)
            attack_text = self.font.render(str(card.attack), True, WHITE)
            self.screen.blit(attack_text, (x + 12, y + CARD_HEIGHT - 27))

            health_rect = pygame.Rect(x + CARD_WIDTH - 35, y + CARD_HEIGHT - 30, 30, 25)
            pygame.draw.rect(self.screen, GREEN, health_rect)
            pygame.draw.rect(self.screen, BLACK, health_rect, 1)
            health_text = self.font.render(str(card.health), True, WHITE)
            self.screen.blit(health_text, (x + CARD_WIDTH - 28, y + CARD_HEIGHT - 27))

    def draw_minion(self, minion, x, y, can_attack=False):
        """绘制战场随从"""
        rect = pygame.Rect(x, y, MINION_WIDTH, MINION_HEIGHT)
        pygame.draw.rect(self.screen, minion.color, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 2)

        # 如果可以攻击，添加边框
        if can_attack:
            pygame.draw.rect(self.screen, YELLOW, rect, 3)

        # 绘制名称
        name_text = self.small_font.render(minion.name, True, WHITE)
        self.screen.blit(name_text, (x + MINION_WIDTH // 2 - name_text.get_width() // 2, y + 10))

        # 绘制攻击力和生命值
        attack_text = self.font.render(str(minion.attack), True, WHITE)
        self.screen.blit(attack_text, (x + 10, y + MINION_HEIGHT - 30))

        health_text = self.font.render(str(minion.health), True, WHITE)
        self.screen.blit(health_text, (x + MINION_WIDTH - 20, y + MINION_HEIGHT - 30))

        # 绘制生命值条
        health_ratio = minion.health / minion.max_health
        health_bar_width = int(MINION_WIDTH * 0.8)
        health_bar_x = x + (MINION_WIDTH - health_bar_width) // 2
        pygame.draw.rect(self.screen, RED, (health_bar_x, y + MINION_HEIGHT - 15, health_bar_width, 8))
        pygame.draw.rect(self.screen, GREEN,
                         (health_bar_x, y + MINION_HEIGHT - 15, int(health_bar_width * health_ratio), 8))
        pygame.draw.rect(self.screen, BLACK, (health_bar_x, y + MINION_HEIGHT - 15, health_bar_width, 8), 1)

    def draw_hero(self, x, y, health, armor, is_player):
        """绘制英雄"""
        rect = pygame.Rect(x, y, 150, 80)
        color = BLUE if is_player else RED
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 2)

        # 绘制英雄名称
        name = "玩家" if is_player else "敌人"
        name_text = self.font.render(name, True, WHITE)
        self.screen.blit(name_text, (x + 75 - name_text.get_width() // 2, y + 10))

        # 绘制生命值
        health_text = self.font.render(f"生命值: {health}", True, WHITE)
        self.screen.blit(health_text, (x + 10, y + 35))

        # 绘制护甲值
        armor_text = self.font.render(f"护甲: {armor}", True, WHITE)
        self.screen.blit(armor_text, (x + 10, y + 55))

    def draw_mana_crystals(self, x, y, current, maximum):
        """绘制法力水晶"""
        for i in range(maximum):
            crystal_x = x + i * 25
            rect = pygame.Rect(crystal_x, y, 20, 30)
            if i < current:
                pygame.draw.rect(self.screen, BLUE, rect)
            else:
                pygame.draw.rect(self.screen, GRAY, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 1)

    def draw(self):
        self.screen.fill(GREEN)

        # 绘制标题
        title = self.large_font.render("炉石传说 - 简化版", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 10))

        # 绘制回合信息
        turn_text = self.font.render(f"回合: {self.turn_number}", True, WHITE)
        self.screen.blit(turn_text, (SCREEN_WIDTH // 2 - turn_text.get_width() // 2, 50))

        # 绘制玩家英雄
        self.draw_hero(50, SCREEN_HEIGHT - 150, self.player_hero_health, self.player_hero_armor, True)

        # 绘制敌人英雄
        self.draw_hero(50, 50, self.enemy_hero_health, self.enemy_hero_armor, False)

        # 绘制玩家法力水晶
        mana_text = self.font.render("玩家法力:", True, WHITE)
        self.screen.blit(mana_text, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 150))
        self.draw_mana_crystals(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 120, self.player_mana, self.player_max_mana)

        # 绘制敌人法力水晶
        enemy_mana_text = self.font.render("敌人法力:", True, WHITE)
        self.screen.blit(enemy_mana_text, (SCREEN_WIDTH - 200, 50))
        self.draw_mana_crystals(SCREEN_WIDTH - 200, 80, self.enemy_mana, self.enemy_max_mana)

        # 绘制玩家战场随从
        battlefield_y = SCREEN_HEIGHT // 2 + 50
        if len(self.player_battlefield) > 0:
            total_width = len(self.player_battlefield) * (MINION_WIDTH + MINION_SPACING) - MINION_SPACING
            battlefield_start_x = (SCREEN_WIDTH - total_width) // 2

            for i, minion in enumerate(self.player_battlefield):
                minion_x = battlefield_start_x + i * (MINION_WIDTH + MINION_SPACING)
                self.draw_minion(minion, minion_x, battlefield_y, minion.can_attack)

        # 绘制敌人战场随从
        battlefield_y = SCREEN_HEIGHT // 2 - MINION_HEIGHT - 50
        if len(self.enemy_battlefield) > 0:
            total_width = len(self.enemy_battlefield) * (MINION_WIDTH + MINION_SPACING) - MINION_SPACING
            battlefield_start_x = (SCREEN_WIDTH - total_width) // 2

            for i, minion in enumerate(self.enemy_battlefield):
                minion_x = battlefield_start_x + i * (MINION_WIDTH + MINION_SPACING)
                self.draw_minion(minion, minion_x, battlefield_y)

        # 绘制手牌
        if self.player_turn:
            hand_start_x = (SCREEN_WIDTH - (len(self.player_hand) * (CARD_WIDTH + CARD_SPACING))) // 2
            hand_y = SCREEN_HEIGHT - CARD_HEIGHT - 20

            for i, card in enumerate(self.player_hand):
                card_x = hand_start_x + i * (CARD_WIDTH + CARD_SPACING)
                # 如果法力值不足，绘制灰色遮罩
                if not self.can_play_card(card):
                    s = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
                    s.set_alpha(128)
                    s.fill(GRAY)
                    self.screen.blit(s, (card_x, hand_y))
                self.draw_card(card, card_x, hand_y)

        # 绘制拖拽的卡牌
        if self.dragging and self.drag_card:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            draw_x = mouse_x - self.drag_offset[0]
            draw_y = mouse_y - self.drag_offset[1]
            self.draw_card(self.drag_card, draw_x, draw_y)

        # 绘制结束回合按钮
        end_turn_button = pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT // 2 - 25, 120, 50)
        pygame.draw.rect(self.screen, ORANGE, end_turn_button)
        pygame.draw.rect(self.screen, BLACK, end_turn_button, 2)
        end_turn_text = self.font.render("结束回合", True, BLACK)
        self.screen.blit(end_turn_text, (SCREEN_WIDTH - 150 + 60 - end_turn_text.get_width() // 2,
                                         SCREEN_HEIGHT // 2 - 10))

        # 绘制操作提示
        hints = [
            "操作说明:",
            "点击手牌打出随从",
            "点击己方随从再点击目标进行攻击",
            "点击结束回合按钮切换回合",
            "按R键重新开始",
            "按ESC键退出"
        ]

        for i, hint in enumerate(hints):
            hint_text = self.font.render(hint, True, WHITE)
            self.screen.blit(hint_text, (50, SCREEN_HEIGHT // 2 - 100 + i * 25))

        # 绘制游戏结束信息
        if self.game_over:
            if self.player_won:
                result_text = self.large_font.render("恭喜获胜! 按R重新开始", True, YELLOW)
            else:
                result_text = self.large_font.render("游戏失败! 按R重新开始", True, RED)
            self.screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, SCREEN_HEIGHT // 2))

        pygame.display.flip()

    def run(self):
        selected_minion = None  # 用于攻击时选择随从

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                if not self.game_over:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        pos = pygame.mouse.get_pos()

                        # 检查是否点击结束回合按钮
                        end_turn_button = pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT // 2 - 25, 120, 50)
                        if end_turn_button.collidepoint(pos):
                            self.end_turn()
                            selected_minion = None
                            continue

                        if self.player_turn:
                            # 检查手牌点击
                            card_info = self.get_card_at_pos(pos)
                            if card_info:
                                _, card_index, card = card_info
                                if self.can_play_card(card):
                                    self.play_card(card_index)
                                    selected_minion = None
                                    continue  # 处理完就继续下一个事件

                            # 检查随从点击（用于攻击）
                            minion_info = self.get_minion_at_pos(pos)
                            if minion_info:
                                side, minion_index, minion = minion_info
                                if side == 'player' and minion.can_attack:
                                    # 选择攻击随从
                                    selected_minion = minion_index
                                elif side == 'enemy' and selected_minion is not None:
                                    # 攻击敌方随从
                                    self.attack(selected_minion, 'minion', minion_index)
                                    selected_minion = None
                                elif side == 'enemy' and selected_minion is not None:
                                    # 攻击敌方英雄（通过点击敌人英雄区域）
                                    # 这里我们简化处理，点击敌人随从区域就算攻击英雄
                                    enemy_hero_rect = pygame.Rect(50, 50, 150, 80)
                                    if enemy_hero_rect.collidepoint(pos):
                                        self.attack(selected_minion, 'hero', -1)
                                        selected_minion = None

                    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        # 取消选择
                        if selected_minion is not None:
                            # 检查是否点击在敌人英雄区域
                            enemy_hero_rect = pygame.Rect(50, 50, 150, 80)
                            if enemy_hero_rect.collidepoint(pygame.mouse.get_pos()):
                                self.attack(selected_minion, 'hero', -1)
                            selected_minion = None

            self.draw()
            self.clock.tick(60)


# 运行游戏
if __name__ == "__main__":
    game = HearthstoneGame()
    game.run()
