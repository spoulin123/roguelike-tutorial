from game_messages import Message

class Breakable:
    def __init__(self, hp):
        self.max_hp = hp
        self.hp = hp

    def take_damage(self, amount):
        results = []
        self.hp -= amount
        if self.hp <= 0:
            results.append({'destroyed' : self.owner})
        return results

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp
