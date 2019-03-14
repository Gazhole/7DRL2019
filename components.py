from copy import deepcopy
from message_log import Message
from entities import Item
from random import choice


class Fighter:
    def __init__(self, hits, left_hand=None, right_hand=None):
        self.hits = hits
        self.max_hits = hits
        self.left_hand = left_hand
        self.right_hand = right_hand

        if self.right_hand and not self.left_hand:
            self.selected_hand = "right"
        elif self.left_hand and not self.right_hand:
            self.selected_hand = "left"
        else:
            self.selected_hand = choice(["left", "right"])

    def get_active_hand(self):
        if self.selected_hand == "right":
            return self.right_hand
        elif self.selected_hand == "left":
            return self.left_hand

    def discard_item(self):
        if self.selected_hand == "right":
            self.right_hand = None
        elif self.selected_hand == "left":
            self.left_hand = None

    def equip_item(self, item):
        if self.selected_hand == "right":
            self.right_hand = item
        elif self.selected_hand == "left":
            self.left_hand = item

    def pickup_item(self, entities):
        active_hand = self.get_active_hand()

        if active_hand:
            return Message("You're already holding something in this hand.", (255, 255, 255))
        else:
            for entity in entities:
                if isinstance(entity, Item):
                    if entity.map_x == self.owner.map_x and entity.map_y == self.owner.map_y:
                        if entity.room_x == self.owner.room_x and entity.room_y == self.owner.room_y:
                            self.equip_item(entity)
                            item_name = entity.name
                            entities.remove(entity)
                            return Message("You pickup the {}".format(item_name), (255, 255, 255))
            else:
                return Message("There's nothing here to pick up.", (255, 255, 255))

    def drop_item(self, game_map, entities):
        active_hand = self.get_active_hand()

        if active_hand:
            dropped_item = deepcopy(active_hand)
            self.discard_item()
            dropped_item.current_room = self.owner.current_room
            dropped_item.set_map_position(game_map)
            dropped_item.room_x = self.owner.room_x
            dropped_item.room_y = self.owner.room_y
            entities.append(dropped_item)
            return Message("You drop the {}.".format(dropped_item.name), (255, 255, 255))
        else:
            return Message("You have nothing in that hand to drop.", (255, 255, 255))

    def take_damage(self, amount):
        results = []

        if self.hits - amount < 0:
            self.hits = 0
        else:
            self.hits -= amount

        if self.hits <= 0:
            results.append({"dead": self.owner})

        return results

    def attack(self, target):
        results = []
        damage = 0

        active_hand = self.get_active_hand()

        if not active_hand:
            pass
        elif active_hand.weapon:
            damage += active_hand.weapon.power
            active_hand.weapon.uses -= 1

        if damage > 0:
            results.append({"message": Message('{} attacks {} ({})'
                                               .format(self.owner.name.capitalize(), target.name.capitalize(), str(damage)),
                                               (255, 255, 255))})
            results.extend(target.fighter.take_damage(damage))
        else:
            results.append({"message": Message('{} attacks without a weapon (0)'
                                               .format(self.owner.name.capitalize(), target.name), (255, 255, 255))})

        if not active_hand:
            pass
        elif active_hand.weapon.uses <= 0:
            item_name = active_hand.name
            results.append({"message": Message("{}'s {} breaks!"
                                               .format(self.owner.name, item_name), (255, 255, 255))})
            self.discard_item()

        return results


class BasicMonster:
    def take_turn(self, target, game_map, entities):
        results = []

        monster = self.owner

        if game_map.rooms[target.map_x][target.map_y].fov[monster.room_x, monster.room_y]:
            if monster.distance_to(target) >= 2:
                monster.move_towards(target.map_x, target.map_y, target.room_x, target.room_y, game_map, entities)

            elif target.fighter.hits > 0:
                attack_results = monster.fighter.attack(target)
                results.extend(attack_results)

        return results


# Item Components
class Weapon:
    def __init__(self, power, uses):
        self.power = power
        self.uses = uses
        self.max_uses = uses
