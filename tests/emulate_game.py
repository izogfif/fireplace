#!/usr/bin/env python
import copy
import sys
import json
from fireplace.card import Card, Enchantment, Minion, Hero, HeroPower, Weapon
from fireplace.game import Game
from fireplace.player import Player
from fireplace import cards
from fireplace.exceptions import GameOver
from fireplace.utils import *
from hearthstone.enums import GameTag, Zone, PlayState
from fireplace.logging import log

sys.path.append("..")


def get_class(x):
    return {
        'Mage': CardClass.MAGE,
        'Warrior': CardClass.WARRIOR,
        'Warlock': CardClass.WARLOCK,
        'Shaman': CardClass.SHAMAN,
        'Priest': CardClass.PRIEST,
        'Rogue': CardClass.ROGUE,
        'Paladin': CardClass.PALADIN,
        'Hunter': CardClass.HUNTER,
        'Druid': CardClass.DRUID
    }.get(x)


def get_tag(x):
    return {
        'HEALTH': GameTag.HEALTH,
        'ZONE': GameTag.ZONE,
        'CONTROLLER': GameTag.CONTROLLER,
        'ENTITY_ID': GameTag.ENTITY_ID,
        'FACTION': GameTag.FACTION,
        'CARDTYPE': GameTag.CARDTYPE,
        'RARITY': GameTag.RARITY,
        'NUM_TURNS_IN_PLAY': GameTag.NUM_TURNS_IN_PLAY,
        'DEFENDING': GameTag.DEFENDING,
        'PREDAMAGE': GameTag.PREDAMAGE,
        'LAST_AFFECTED_BY': GameTag.LAST_AFFECTED_BY,
        'DAMAGE': GameTag.DAMAGE,
        'COST': GameTag.COST,
        'CREATOR': GameTag.CREATOR,
        'CARD_TARGET': GameTag.CARD_TARGET,
        'EXHAUSTED': GameTag.EXHAUSTED,
        'ATTACHED': GameTag.ATTACHED,
        'NUM_ATTACKS_THIS_TURN': GameTag.NUM_ATTACKS_THIS_TURN,
        'ATK': GameTag.ATK,
        'ATTACKING': GameTag.ATTACKING,
        'PREHEALING': GameTag.PREHEALING,
        'DEATH_RATTLE': GameTag.DEATH_RATTLE,
        'JUST_PLAYED': GameTag.JUST_PLAYED,
        'ZONE_POSITION': GameTag.ZONE_POSITION,
        'BATTLECRY': GameTag.BATTLECRY,
        'ELITE': GameTag.ELITE,
        'AFFECTED_BY_SPELL_POWER': GameTag.AFFECTED_BY_SPELL_POWER,
        'PREMIUM': GameTag.PREMIUM,
        'PLAYSTATE': GameTag.PLAYSTATE,
        'HERO_ENTITY': GameTag.HERO_ENTITY,
        'MAXHANDSIZE': GameTag.MAXHANDSIZE,
        'STARTHANDSIZE': GameTag.STARTHANDSIZE,
        'PLAYER_ID': GameTag.PLAYER_ID,
        'TEAM_ID': GameTag.TEAM_ID,
        'MAXRESOURCES': GameTag.MAXRESOURCES,
        'NUM_TURNS_LEFT': GameTag.NUM_TURNS_LEFT,
        'NUM_CARDS_DRAWN_THIS_TURN': GameTag.NUM_CARDS_DRAWN_THIS_TURN,
        'MULLIGAN_STATE': GameTag.MULLIGAN_STATE,
        'CURRENT_PLAYER': GameTag.CURRENT_PLAYER,
        'RESOURCES': GameTag.RESOURCES,
        'RESOURCES_USED': GameTag.RESOURCES_USED,
        'NUM_RESOURCES_SPENT_THIS_GAME': GameTag.NUM_RESOURCES_SPENT_THIS_GAME,
        'NUM_CARDS_PLAYED_THIS_TURN': GameTag.NUM_CARDS_PLAYED_THIS_TURN,
        'NUM_MINIONS_PLAYED_THIS_TURN': GameTag.NUM_MINIONS_PLAYED_THIS_TURN,
        'LAST_CARD_PLAYED': GameTag.LAST_CARD_PLAYED,
        'COMBO_ACTIVE': GameTag.COMBO_ACTIVE,
        'NUM_OPTIONS_PLAYED_THIS_TURN': GameTag.NUM_OPTIONS_PLAYED_THIS_TURN,
        'NUM_MINIONS_PLAYER_KILLED_THIS_TURN': GameTag.NUM_MINIONS_PLAYER_KILLED_THIS_TURN,
        'NUM_FRIENDLY_MINIONS_THAT_DIED_THIS_TURN': GameTag.NUM_FRIENDLY_MINIONS_THAT_DIED_THIS_TURN,
        'NUM_FRIENDLY_MINIONS_THAT_DIED_THIS_GAME': GameTag.NUM_FRIENDLY_MINIONS_THAT_DIED_THIS_GAME,
        'TEMP_RESOURCES': GameTag.TEMP_RESOURCES,
        'NUM_FRIENDLY_MINIONS_THAT_ATTACKED_THIS_TURN': GameTag.NUM_FRIENDLY_MINIONS_THAT_ATTACKED_THIS_TURN,
        'OneTurnEffect': GameTag.OneTurnEffect,
        'HEROPOWER_ACTIVATIONS_THIS_TURN': GameTag.HEROPOWER_ACTIVATIONS_THIS_TURN,
        'NUM_TIMES_HERO_POWER_USED_THIS_GAME': GameTag.NUM_TIMES_HERO_POWER_USED_THIS_GAME,
        'TRIGGER_VISUAL': GameTag.TRIGGER_VISUAL,
        'DURABILITY': GameTag.DURABILITY,
        'TAG_SCRIPT_DATA_NUM_1': GameTag.TAG_SCRIPT_DATA_NUM_1,
        'TAG_SCRIPT_DATA_NUM_2': GameTag.TAG_SCRIPT_DATA_NUM_2,
        'TAUNT': GameTag.TAUNT,
        'POWERED_UP': GameTag.POWERED_UP,
        'FROZEN': GameTag.FROZEN,
        'SHOWN_HERO_POWER': GameTag.SHOWN_HERO_POWER,
        'DIVINE_SHIELD': GameTag.DIVINE_SHIELD,
        'AURA': GameTag.AURA,
        'ADJACENT_BUFF': GameTag.ADJACENT_BUFF,
        'CHARGE': GameTag.CHARGE,
        'WINDFURY': GameTag.WINDFURY,
        'DISPLAYED_CREATOR': GameTag.DISPLAYED_CREATOR,
        'CANT_BE_TARGETED_BY_OPPONENTS': GameTag.CANT_BE_TARGETED_BY_OPPONENTS,
        'CANT_BE_ATTACKED': GameTag.CANT_BE_ATTACKED,
        'STEALTH': GameTag.STEALTH,
        'COMBO': GameTag.COMBO,
        'SPELLPOWER': GameTag.SPELLPOWER,
        'CLASS': GameTag.CLASS,
        'SECRET': GameTag.SECRET,
        'RECALL': GameTag.RECALL,
        'RECALL_OWED': GameTag.RECALL_OWED,
        'ARMOR': GameTag.ARMOR,
        'RITUAL': GameTag.RITUAL,
    }.get(x, None)


def process_tags(player, tags):
    for tag in tags:
        cur_tag = get_tag(tag)
        tag_value = tags[tag]
        if cur_tag == GameTag.NUM_CARDS_DRAWN_THIS_TURN:
            player.cards_drawn_this_turn = tag_value
        elif cur_tag == GameTag.ENTITY_ID:
            player.entity_id = tag_value
        elif cur_tag == GameTag.FATIGUE:
            player.fatigue_counter = tag_value
        elif cur_tag == GameTag.HEALING_DOUBLE:
            player.healing_double = tag_value
        elif cur_tag == GameTag.HERO_POWER_DOUBLE:
            player.hero_power_double = tag_value
        # elif cur_tag == GameTag.RESOURCES:
        #     player.mana = tag_value
        elif cur_tag == GameTag.MAXHANDSIZE:
            player.max_hand_size = tag_value
        elif cur_tag == GameTag.RESOURCES:
            player._max_mana = tag_value
        elif cur_tag == GameTag.MAXRESOURCES:
            player.max_resources = tag_value
        elif cur_tag == GameTag.NUM_MINIONS_KILLED_THIS_TURN:
            player.minions_killed_this_turn = tag_value
        elif cur_tag == GameTag.OVERLOAD_LOCKED:
            player.overload_locked = tag_value
        elif cur_tag == GameTag.SPELLPOWER:
            player.spellpower_adjustment = tag_value
        elif cur_tag == GameTag.SPELLPOWER_DOUBLE:
            player.spellpower_double = tag_value
        elif cur_tag == GameTag.SPELLS_COST_HEALTH:
            player.spells_cost_health = tag_value
        elif cur_tag == GameTag.TEMP_RESOURCES:
            player.temp_mana = tag_value
        elif cur_tag == GameTag.NUM_TIMES_HERO_POWER_USED_THIS_GAME:
            player.times_hero_power_used_this_game = tag_value
        elif cur_tag == GameTag.RESOURCES_USED:
            player.used_mana = tag_value


def get_game_entity_by_id(game, entity_id):
    for entity in game.entities:
        if entity.entity_id == entity_id:
            return entity
    # assert False
    return None


def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def add_to_tags_verify_list(arr, minion, tags):
    pair = list()
    pair.append(minion)
    pair.append(tags)
    arr.append(pair)


def ensure_tags_are_same(cur_card, tags):
    assert not (cur_card is None) and not (tags is None)
    for tag in tags:
        cur_tag = get_tag(tag)
        tag_value = tags[tag]
        assert not (cur_tag is None) or is_number(tag)
        if cur_tag == GameTag.ATK:
            if not isinstance(cur_card, Hero):
                while cur_card.atk < tag_value:
                    cur_card._atk += 1
                while cur_card.atk > tag_value:
                    cur_card._atk -= 1
        elif cur_tag == GameTag.HEALTH:
            cur_card._max_health = tag_value


def set_card_tags(cur_card, tags, game):
    assert not (cur_card is None) and not (tags is None)
    for tag in tags:
        cur_tag = get_tag(tag)
        tag_value = tags[tag]
        assert not (cur_tag is None) or is_number(tag)
        if False:
            temp_value = 0
        # elif cur_tag == GameTag.COST:
        #     cur_card._cost = tag_value
        #     cur_card.cost = tag_value
        elif cur_tag == GameTag.CANNOT_ATTACK_HEROES:
            cur_card.cannot_attack_heroes = tag_value
        elif cur_tag == GameTag.CANT_BE_DAMAGED:
            cur_card.cant_be_damaged = tag_value
        elif cur_tag == GameTag.CANT_BE_TARGETED_BY_ABILITIES:
            cur_card.cant_be_targeted_by_abilities = tag_value
        elif cur_tag == GameTag.CANT_BE_TARGETED_BY_HERO_POWERS:
            cur_card.cant_be_targeted_by_hero_powers = tag_value
        elif cur_tag == GameTag.CANT_BE_TARGETED_BY_OPPONENTS:
            cur_card.cant_be_targeted_by_opponents = tag_value
        elif cur_tag == GameTag.CANT_PLAY:
            cur_card.cant_play = tag_value
        elif cur_tag == GameTag.CHARGE:
            cur_card.charge = tag_value
        elif cur_tag == GameTag.DAMAGE:
            cur_card.damage = tag_value
        elif cur_tag == GameTag.DIVINE_SHIELD:
            cur_card.divine_shield = tag_value
        elif cur_tag == GameTag.ENRAGED:
            cur_card.enraged = tag_value
        elif cur_tag == GameTag.ENTITY_ID:
            cur_card.entity_id = tag_value
        # elif cur_tag == GameTag.EXHAUSTED:
        #     cur_card.exhausted = bool(tag_value)
        elif cur_tag == GameTag.FORGETFUL:
            cur_card.forgetful = tag_value
        elif cur_tag == GameTag.FROZEN:
            cur_card.frozen = tag_value
        elif cur_tag == GameTag.BATTLECRY:
            cur_card.has_battlecry = tag_value
        elif cur_tag == GameTag.COMBO:
            cur_card.has_combo = tag_value
        elif cur_tag == GameTag.INSPIRE:
            cur_card.has_inspire = tag_value
        # elif cur_tag == GameTag.HEALTH:
        #     cur_card.health = tag_value
        elif cur_tag == GameTag.HEAVILY_ARMORED:
            cur_card.heavily_armored = tag_value
        elif cur_tag == GameTag.HEROPOWER_DAMAGE:
            cur_card.heropower_damage = tag_value
        elif cur_tag == GameTag.IMMUNE_WHILE_ATTACKING:
            cur_card.immune_while_attacking = tag_value
        elif cur_tag == GameTag.INCOMING_DAMAGE_MULTIPLIER:
            cur_card.incoming_damage_multiplier = tag_value
        # elif cur_tag == GameTag.HEALTH:
        #     cur_card.max_health = tag_value
        elif cur_tag == GameTag.IS_MORPHED:
            cur_card.morphed = tag_value
        elif cur_tag == GameTag.CHOOSE_ONE:
            cur_card.must_choose_one = tag_value
        elif cur_tag == GameTag.NUM_ATTACKS_THIS_TURN:
            cur_card.num_attacks = tag_value
        elif cur_tag == GameTag.OVERLOAD:
            cur_card.overload = tag_value
        elif cur_tag == GameTag.POISONOUS:
            cur_card.poisonous = tag_value
        # doesn't matter if powered_up set or not
        # elif cur_tag == GameTag.POWERED_UP:
        #     assert cur_card.powered_up == tag_value
        elif cur_tag == GameTag.PREDAMAGE:
            cur_card.predamage = tag_value
        elif cur_tag == GameTag.RARITY:
            cur_card.rarity = tag_value
        elif cur_tag == GameTag.SHOULDEXITCOMBAT:
            cur_card.should_exit_combat = tag_value
        elif cur_tag == GameTag.SILENCED:
            cur_card.silenced = tag_value
        elif cur_tag == GameTag.SPELLPOWER:
            cur_card.spellpower = tag_value
        elif cur_tag == GameTag.STEALTH:
            cur_card.stealthed = tag_value
        elif cur_tag == GameTag.TAUNT:
            cur_card.taunt = tag_value
        elif cur_tag == GameTag.TO_BE_DESTROYED:
            cur_card.to_be_destroyed = tag_value
        elif cur_tag == GameTag.NUM_TURNS_IN_PLAY:
            cur_card.turns_in_play = tag_value
        # elif cur_tag == GameTag.WINDFURY:
        #     cur_card.windfury = tag_value
        elif cur_tag == GameTag.DURABILITY:
            cur_card._max_durability = tag_value
        elif cur_tag == GameTag.ATTACHED:
            assert isinstance(cur_card, Enchantment)
            assert not (game is None)
            enchantment_target = get_game_entity_by_id(game, tag_value)
            assert not (enchantment_target is None)
            cur_card.owner = enchantment_target
        elif cur_tag == GameTag.CREATOR:
            assert not (game is None)
            card_creator = get_game_entity_by_id(game, tag_value)
            # assert not (card_creator is None)
            if not (card_creator is None):
                cur_card.source = card_creator
        elif cur_tag == GameTag.ZONE_POSITION:
            if isinstance(cur_card, Minion):
                cur_card._summon_index = tag_value - 1
        elif cur_tag == GameTag.ARMOR:
            assert isinstance(cur_card, Hero)
            cur_card.armor = tag_value


def my_add_buff(attached_to, card):
    cur_controller = attached_to.controller
    card.controller = cur_controller
    card._zone = Zone.PLAY
    card.play_counter = attached_to.game.play_counter
    attached_to.game.play_counter += 1
    attached_to.game.manager.new_entity(card)
    attached_to.buffs.append(card)
    return card


def my_summon(game, cur_controller, card):
    card.controller = cur_controller
    card._zone = Zone.PLAY
    card.play_counter = game.play_counter
    game.play_counter += 1
    game.manager.new_entity(card)
    # game.cheat_action(cur_controller, [Summon(cur_controller, card)])
    log.info("%s summons %r", cur_controller, card)
    assert isinstance(card, Enchantment) or card.is_summonable()
    card.controller = cur_controller
    cur_controller.field.append(card)
    return card


def show_board(game):
    log.info("")
    log.info("----- Board -----")
    assert not (game is None)
    for player in game.players:
        log.info("Player has hero %r with %d health out of %d", CardList([player.hero]), player.hero.health, player.hero.max_health)
        if len(player.field) == 0:
            log.info("Board of player %s is empty", player.name)
        else:
            log.info("%s has %d entities on board:", player.name, len(player.field))

        for minion in player.field:
            assert isinstance(minion, Minion)
            log.info("%s %d / %d (max %d)", minion.name, minion.atk, minion.health, minion.max_health)
    log.info("----- END of the board -----")
    log.info("")


# def save_game(game: Game) -> str:
#     playerObject = game.current_player
#     opponentObject = None
#     for player in game.players:
#         if player == game.current_player:
#             playerObject = player
#         else:
#             opponentObject = player
#
#     result = object()
#     player = object()
#     player["playerClass"] = game.current_player
#     for entity in game.entities:
#
#         pass
#     return result


def load_game():
    data = json.load(open("N://HSTracker//board_state-hunter.json"))
    assert "player" in data
    assert "opponent" in data
    player_name = data["player"]["name"]
    opponent_name = data["opponent"]["name"]
    player_class = get_class(data["player"]["playerClass"])
    opponent_class = get_class(data["opponent"]["playerClass"])
    player_deck = random_draft(player_class)
    opponent_deck = random_draft(opponent_class)

    # Keep just enough cards for mulligan
    while len(player_deck) > 4:
        player_deck.pop()
    while len(opponent_deck) > 4:
        opponent_deck.pop()

    player_controller_id = data["player"]["entity"]["Tags"]["CONTROLLER"]
    opponent_controller_id = data["opponent"]["entity"]["Tags"]["CONTROLLER"]
    player_player = Player(player_name, player_deck, player_class.default_hero)
    opponent_player = Player(opponent_name, opponent_deck, opponent_class.default_hero)
    game = None
    if player_controller_id == 1 and opponent_controller_id == 2:
        game = Game(players=(player_player, opponent_player))
    elif player_controller_id == 2 and opponent_controller_id == 1:
        game = Game(players=(opponent_player, player_player))

    game.start()

    # Don't redraw mulligan cards
    for player in game.players:
        if player.choice:
            player.choice.choose()
    assert "cardsInHand" in data["opponent"]
    cards_in_opponent_hand = data["opponent"]["cardsInHand"]
    game.players[player_controller_id - 1].discard_hand()
    game.players[opponent_controller_id - 1].discard_hand()

    # fill the hand of the opponent with the card which doesn't do anything on draw / reveal
    for i in range(0, cards_in_opponent_hand):
        game.players[opponent_controller_id - 1].give("OG_335")  # Shifting Shade

    assert "entity" in data["player"]
    assert "Tags" in data["player"]["entity"]
    process_tags(game.players[player_controller_id - 1], data["player"]["entity"]["Tags"])

    assert "entity" in data["opponent"]
    assert "Tags" in data["opponent"]["entity"]
    process_tags(game.players[opponent_controller_id - 1], data["opponent"]["entity"]["Tags"])

    cards_to_recheck = list()

    for entity in data["hand"]:
        assert "Tags" in entity
        assert "CONTROLLER" in entity["Tags"]
        controller = entity["Tags"]["CONTROLLER"]
        assert controller == player_controller_id
        assert "CardId" in entity
        cur_card_id = entity["CardId"]
        cur_card = game.players[controller - 1].give(cur_card_id)
        set_card_tags(cur_card, entity["Tags"], game)
        add_to_tags_verify_list(cards_to_recheck, cur_card, entity["Tags"])

    # first summon heroes and their powers
    for entity in data["board"]:
        assert "Tags" in entity and "CONTROLLER" in entity["Tags"]
        cur_controller_id = entity["Tags"]["CONTROLLER"]
        assert cur_controller_id == 1 or cur_controller_id == 2
        cur_controller = game.players[cur_controller_id - 1]

        assert "HasCardId" in entity and entity["HasCardId"] is True and "CardId" in entity
        cur_card_id = entity["CardId"]
        temp_card = Card(cur_card_id)
        if isinstance(temp_card, Hero) or isinstance(temp_card, HeroPower) or isinstance(temp_card, Weapon):
            cur_card = cur_controller.summon(cur_card_id)
            add_to_tags_verify_list(cards_to_recheck, cur_card, entity["Tags"])
            set_card_tags(cur_card, entity["Tags"], game)

    for entity in data["board"]:
        assert "Tags" in entity and "CONTROLLER" in entity["Tags"]
        cur_controller_id = entity["Tags"]["CONTROLLER"]
        assert cur_controller_id == 1 or cur_controller_id == 2
        cur_controller = game.players[cur_controller_id - 1]

        assert "HasCardId" in entity and entity["HasCardId"] is True and "CardId" in entity
        cur_card_id = entity["CardId"]
        temp_card = Card(cur_card_id)
        if isinstance(temp_card, Enchantment):
            if cur_card_id != 'EX1_059e' and cur_card_id != 'OG_281e':   # don't apply "Experiments!" (health swap) buff
                                                                         # don't apply "Fanatic Devotion" buff (must be C'thun's increased stats)
                if not ("ATTACHED" in entity["Tags"]): # sometimes enchantments stay in play while not being attached to anything
                    continue
                attached_id = entity["Tags"]["ATTACHED"]
                buff_attached_to = get_game_entity_by_id(game, attached_id)
                assert not (buff_attached_to is None)
                cur_card = my_add_buff(buff_attached_to, temp_card)
                set_card_tags(cur_card, entity["Tags"], game)
        elif not (isinstance(temp_card, Hero) or isinstance(temp_card, HeroPower)):
            cur_card = my_summon(game, cur_controller, temp_card)
            add_to_tags_verify_list(cards_to_recheck, cur_card, entity["Tags"])
            set_card_tags(cur_card, entity["Tags"], game)

    for t in cards_to_recheck:
        set_card_tags(t[0], t[1], game)
        ensure_tags_are_same(t[0], t[1])

    for player in game.players:
        sorted_cards = dict()
        for card in player.field:
            if isinstance(card, Weapon):
                continue
            zone_position = card._summon_index
            assert not zone_position in sorted_cards
            sorted_cards[zone_position] = card
        player.field = CardList()
        for pos in sorted(sorted_cards.keys()):
            assert pos == len(player.field)
            player.field.append(sorted_cards[pos])

    game.current_player = game.players[player_controller_id - 1]

    for player in game.players:
        player.cards_played_this_turn = 0
        player.minions_played_this_turn = 0
        player.minions_killed_this_turn = 0

    return game


class Move(object):
    
    m_should_skip_using_hero_power = False
    m_hero_power_target = 0

    m_cards_in_hand_to_skip = 0
    m_pre_play_card_choice = None
    m_play_card_target = 0
    m_minion_position = 0
    m_after_play_card_choice = None
    m_max_after_play_card_choice = None

    m_characters_who_can_attack_to_skip = 0
    m_attack_targets_to_skip = 0

    def __init__(self, other=None):
        if other is None:
            return
        # Hero power
        self.m_should_skip_using_hero_power = other.m_should_skip_using_hero_power
        self.m_hero_power_target = other.m_hero_power_target
        # Play card from hand
        self.m_cards_in_hand_to_skip = other.m_cards_in_hand_to_skip
        self.m_pre_play_card_choice = other.m_pre_play_card_choice
        self.m_play_card_target = other.m_play_card_target
        self.m_minion_position = other.m_minion_position
        self.m_after_play_card_choice = other.m_after_play_card_choice
        self.m_max_after_play_card_choice = other.m_max_after_play_card_choice
        # Attack using minions on the board
        self.m_characters_who_can_attack_to_skip = other.m_characters_who_can_attack_to_skip
        self.m_attack_targets_to_skip = other.m_attack_targets_to_skip

    def __str__(self):
        if not self.m_should_skip_using_hero_power:
            return "Using hero power. If possible, on target #%d" % self.m_hero_power_target

        result = "card=%d" % self.m_cards_in_hand_to_skip
        result += ", pre_choice=%d" % (self.m_pre_play_card_choice if not (self.m_pre_play_card_choice is None) else 0)
        result += ", target=%d" % self.m_play_card_target
        result += ", pos=%d" % self.m_minion_position
        result += ", after_choice={0} of {1}".format(
            self.m_after_play_card_choice if not (self.m_after_play_card_choice is None) else 0,
            self.m_max_after_play_card_choice if not (self.m_max_after_play_card_choice is None) else 0
        )
        result += ", {0} attacks {1}".format(self.m_characters_who_can_attack_to_skip, self.m_attack_targets_to_skip)
        return result


def play_move(game: Game, move: Move, silently: bool) -> [bool, Move]:
    """
    Tries to play the move
    :param game: Game object
    :param move: Move object
    :return: bool (True if move was possible to play) and the next move or None if no move available
    """

    play_message = ""
    next_move = Move()
    player = game.current_player
    assert player.playstate != PlayState.WON and player.playstate != PlayState.LOST and player.playstate != PlayState.TIED
    try:
        if not move.m_should_skip_using_hero_power:
            heropower = player.hero.power
            if not heropower.is_usable():
                next_move.m_should_skip_using_hero_power = True
                assert next_move.m_hero_power_target == 0
                assert next_move.m_cards_in_hand_to_skip == 0
                assert next_move.m_pre_play_card_choice is None
                assert next_move.m_play_card_target == 0
                assert next_move.m_minion_position == 0
                assert next_move.m_after_play_card_choice is None
                assert next_move.m_max_after_play_card_choice is None
                assert next_move.m_characters_who_can_attack_to_skip == 0
                assert next_move.m_attack_targets_to_skip == 0
                return [False, next_move]
            if heropower.has_target():
                if move.m_hero_power_target == len(heropower.targets):
                    next_move.m_should_skip_using_hero_power = True
                    assert next_move.m_hero_power_target == 0
                    assert next_move.m_cards_in_hand_to_skip == 0
                    assert next_move.m_pre_play_card_choice is None
                    assert next_move.m_play_card_target == 0
                    assert next_move.m_minion_position == 0
                    assert next_move.m_after_play_card_choice is None
                    assert next_move.m_max_after_play_card_choice is None
                    assert next_move.m_characters_who_can_attack_to_skip == 0
                    assert next_move.m_attack_targets_to_skip == 0
                    return [False, next_move]
                next_move.m_hero_power_target = move.m_hero_power_target + 1
                power_target = heropower.targets[move.m_hero_power_target]
                if silently is False:
                    print("Player {0} uses hero power {1} on {2}".format(player, heropower, power_target))
                heropower.use(target=power_target)
                return [True, next_move]
            else:
                next_move.m_should_skip_using_hero_power = True
                assert next_move.m_hero_power_target == 0
                assert next_move.m_cards_in_hand_to_skip == 0
                assert next_move.m_pre_play_card_choice is None
                assert next_move.m_play_card_target == 0
                assert next_move.m_minion_position == 0
                assert next_move.m_after_play_card_choice is None
                assert next_move.m_max_after_play_card_choice is None
                assert next_move.m_characters_who_can_attack_to_skip == 0
                assert next_move.m_attack_targets_to_skip == 0
                if silently is False:
                    print("Player {0} uses hero power {1}".format(player, heropower))
                heropower.use()
                return [True, next_move]

        # We didn't play Hero power - set fields in next_move accordingly
        next_move.m_should_skip_using_hero_power = True
        next_move.m_hero_power_target = 0

        if move.m_cards_in_hand_to_skip < len(player.hand):
            card = player.hand[move.m_cards_in_hand_to_skip]
            if not card.is_playable():
                assert next_move.m_should_skip_using_hero_power is True
                assert next_move.m_hero_power_target == 0
                next_move.m_cards_in_hand_to_skip = move.m_cards_in_hand_to_skip + 1
                assert next_move.m_pre_play_card_choice is None
                assert next_move.m_play_card_target == 0
                assert next_move.m_minion_position == 0
                assert next_move.m_after_play_card_choice is None
                assert next_move.m_max_after_play_card_choice is None
                assert next_move.m_characters_who_can_attack_to_skip == 0
                assert next_move.m_attack_targets_to_skip == 0
                return [False, next_move]

            play_message = "Player plays card {0}".format(card)
            orig_card = card
            if card.must_choose_one:
                if move.m_pre_play_card_choice is None:
                    move.m_pre_play_card_choice = 0
                if move.m_pre_play_card_choice == len(card.choose_cards):
                    assert next_move.m_should_skip_using_hero_power is True
                    assert next_move.m_hero_power_target == 0
                    next_move.m_cards_in_hand_to_skip = move.m_cards_in_hand_to_skip + 1
                    assert next_move.m_pre_play_card_choice is None
                    assert next_move.m_play_card_target == 0
                    assert next_move.m_minion_position == 0
                    assert next_move.m_after_play_card_choice is None
                    assert next_move.m_max_after_play_card_choice is None
                    assert next_move.m_characters_who_can_attack_to_skip == 0
                    assert next_move.m_attack_targets_to_skip == 0
                    return [False, next_move]
                else:
                    card = card.choose_cards[move.m_pre_play_card_choice]
                    play_message += ", chooses card {0}".format(card)
            else:
                next_move.m_pre_play_card_choice = None

            card_target = None
            if card.has_target():
                if move.m_play_card_target == len(card.targets):
                    if orig_card.must_choose_one:
                        assert next_move.m_should_skip_using_hero_power is True
                        assert next_move.m_hero_power_target == 0
                        next_move.m_cards_in_hand_to_skip = move.m_cards_in_hand_to_skip
                        next_move.m_pre_play_card_choice = move.m_pre_play_card_choice + 1
                        assert next_move.m_play_card_target == 0
                        assert next_move.m_minion_position == 0
                        assert next_move.m_after_play_card_choice is None
                        assert next_move.m_max_after_play_card_choice is None
                        assert next_move.m_characters_who_can_attack_to_skip == 0
                        assert next_move.m_attack_targets_to_skip == 0
                    else:
                        assert next_move.m_should_skip_using_hero_power is True
                        assert next_move.m_hero_power_target == 0
                        next_move.m_cards_in_hand_to_skip = move.m_cards_in_hand_to_skip + 1
                        assert next_move.m_pre_play_card_choice is None
                        assert next_move.m_play_card_target == 0
                        assert next_move.m_minion_position == 0
                        assert next_move.m_after_play_card_choice is None
                        assert next_move.m_max_after_play_card_choice is None
                        assert next_move.m_characters_who_can_attack_to_skip == 0
                        assert next_move.m_attack_targets_to_skip == 0

                    return [False, next_move]
                card_target = card.targets[move.m_play_card_target]
                play_message += ", picks target card {0}".format(card_target)

            zone_index = None
            if isinstance(card, Minion):
                if move.m_minion_position > len(player.field):
                    if card.has_target():
                        assert next_move.m_should_skip_using_hero_power is True
                        assert next_move.m_hero_power_target == 0
                        next_move.m_cards_in_hand_to_skip = move.m_cards_in_hand_to_skip
                        next_move.m_pre_play_card_choice = move.m_pre_play_card_choice
                        next_move.m_play_card_target = move.m_play_card_target + 1
                        assert next_move.m_minion_position == 0
                        assert next_move.m_after_play_card_choice is None
                        assert next_move.m_max_after_play_card_choice is None
                        assert next_move.m_characters_who_can_attack_to_skip == 0
                        assert next_move.m_attack_targets_to_skip == 0
                    elif orig_card.must_choose_one:
                        assert next_move.m_should_skip_using_hero_power is True
                        assert next_move.m_hero_power_target == 0
                        next_move.m_cards_in_hand_to_skip = move.m_cards_in_hand_to_skip
                        next_move.m_pre_play_card_choice = move.m_pre_play_card_choice + 1
                        assert next_move.m_play_card_target == 0
                        assert next_move.m_minion_position == 0
                        assert next_move.m_after_play_card_choice is None
                        assert next_move.m_max_after_play_card_choice is None
                        assert next_move.m_characters_who_can_attack_to_skip == 0
                        assert next_move.m_attack_targets_to_skip == 0
                    else:
                        assert next_move.m_should_skip_using_hero_power is True
                        assert next_move.m_hero_power_target == 0
                        next_move.m_cards_in_hand_to_skip = move.m_cards_in_hand_to_skip + 1
                        assert next_move.m_pre_play_card_choice is None
                        assert next_move.m_play_card_target == 0
                        assert next_move.m_minion_position == 0
                        assert next_move.m_after_play_card_choice is None
                        assert next_move.m_max_after_play_card_choice is None
                        assert next_move.m_characters_who_can_attack_to_skip == 0
                        assert next_move.m_attack_targets_to_skip == 0

                    return [False, next_move]
                else:
                    zone_index = next_move.m_minion_position
                    play_message += ", puts minion at position %d" % zone_index

            if (move.m_after_play_card_choice is None) or move.m_after_play_card_choice == move.m_max_after_play_card_choice:
                if isinstance(card, Minion):
                    assert next_move.m_should_skip_using_hero_power is True
                    assert next_move.m_hero_power_target == 0
                    next_move.m_cards_in_hand_to_skip = move.m_cards_in_hand_to_skip
                    next_move.m_pre_play_card_choice = move.m_pre_play_card_choice
                    next_move.m_play_card_target = move.m_play_card_target + 1
                    next_move.m_minion_position = move.m_minion_position + 1
                    assert next_move.m_after_play_card_choice is None
                    assert next_move.m_max_after_play_card_choice is None
                    assert next_move.m_characters_who_can_attack_to_skip == 0
                    assert next_move.m_attack_targets_to_skip == 0
                elif card.has_target():
                    assert next_move.m_should_skip_using_hero_power is True
                    assert next_move.m_hero_power_target == 0
                    next_move.m_cards_in_hand_to_skip = move.m_cards_in_hand_to_skip
                    next_move.m_pre_play_card_choice = move.m_pre_play_card_choice
                    next_move.m_play_card_target = move.m_play_card_target + 1
                    assert next_move.m_minion_position == 0
                    assert next_move.m_after_play_card_choice is None
                    assert next_move.m_max_after_play_card_choice is None
                    assert next_move.m_characters_who_can_attack_to_skip == 0
                    assert next_move.m_attack_targets_to_skip == 0
                elif orig_card.must_choose_one:
                    assert next_move.m_should_skip_using_hero_power is True
                    assert next_move.m_hero_power_target == 0
                    next_move.m_cards_in_hand_to_skip = move.m_cards_in_hand_to_skip
                    next_move.m_pre_play_card_choice = move.m_pre_play_card_choice + 1
                    assert next_move.m_play_card_target == 0
                    assert next_move.m_minion_position == 0
                    assert next_move.m_after_play_card_choice is None
                    assert next_move.m_max_after_play_card_choice is None
                    assert next_move.m_characters_who_can_attack_to_skip == 0
                    assert next_move.m_attack_targets_to_skip == 0
                else:
                    assert next_move.m_should_skip_using_hero_power is True
                    assert next_move.m_hero_power_target == 0
                    next_move.m_cards_in_hand_to_skip = move.m_cards_in_hand_to_skip + 1
                    assert next_move.m_pre_play_card_choice is None
                    assert next_move.m_play_card_target == 0
                    assert next_move.m_minion_position == 0
                    assert next_move.m_after_play_card_choice is None
                    assert next_move.m_max_after_play_card_choice is None
                    assert next_move.m_characters_who_can_attack_to_skip == 0
                    assert next_move.m_attack_targets_to_skip == 0

            if not (move.m_after_play_card_choice is None) and move.m_after_play_card_choice == move.m_max_after_play_card_choice:
                return [False, next_move]
            try:
                card.play(target=card_target, index=zone_index)
            except GameOver:
                if silently is False:
                    play_message += " and game is over"
                    print(play_message)
                raise

            if player.choice:
                if move.m_after_play_card_choice is None:
                    move.m_after_play_card_choice = 0
                    move.m_max_after_play_card_choice = len(player.choice.cards)
                    next_move.m_after_play_card_choice = 0
                    next_move.m_max_after_play_card_choice = len(player.choice.cards)
                assert move.m_after_play_card_choice < len(player.choice.cards)
                assert next_move.m_max_after_play_card_choice == len(player.choice.cards)

                assert next_move.m_should_skip_using_hero_power is True
                assert next_move.m_hero_power_target == 0
                next_move.m_cards_in_hand_to_skip = move.m_cards_in_hand_to_skip
                next_move.m_pre_play_card_choice = move.m_pre_play_card_choice
                next_move.m_play_card_target = move.m_play_card_target + 1
                next_move.m_minion_position = move.m_minion_position + 1
                next_move.m_after_play_card_choice = move.m_after_play_card_choice + 1
                next_move.m_max_after_play_card_choice = move.m_max_after_play_card_choice
                assert next_move.m_characters_who_can_attack_to_skip == 0
                assert next_move.m_attack_targets_to_skip == 0

                choice = player.choice.cards[move.m_after_play_card_choice]
                log.info("After play we're choosing card {0}".format(choice))
                try:
                    player.choice.choose(choice)
                except GameOver:
                    if silently is False:
                        play_message += " and game is over"
                        print(play_message)
                    raise

                play_message += ", selects card {0} as an afterplay choice".format(choice)

            if silently is False:
                print(play_message)
            return [True, next_move]

        assert next_move.m_should_skip_using_hero_power is True
        assert next_move.m_hero_power_target == 0
        next_move.m_cards_in_hand_to_skip = move.m_cards_in_hand_to_skip
        assert next_move.m_pre_play_card_choice is None
        assert next_move.m_play_card_target == 0
        assert next_move.m_minion_position == 0
        assert next_move.m_after_play_card_choice is None
        assert next_move.m_max_after_play_card_choice is None
        assert next_move.m_characters_who_can_attack_to_skip == 0
        assert next_move.m_attack_targets_to_skip == 0

        # No more characters left to attack with
        if move.m_characters_who_can_attack_to_skip == len(player.characters):
            return [False, None]

        character = player.characters[move.m_characters_who_can_attack_to_skip]
        assert not (character is None)
        if not character.can_attack():
            next_move.m_characters_who_can_attack_to_skip = move.m_characters_who_can_attack_to_skip + 1
            assert next_move.m_attack_targets_to_skip == 0
            return [False, next_move]
        if move.m_attack_targets_to_skip == len(character.targets):
            next_move.m_characters_who_can_attack_to_skip = move.m_characters_who_can_attack_to_skip + 1
            assert next_move.m_attack_targets_to_skip == 0
            return [False, next_move]
        target_to_attack = character.targets[move.m_attack_targets_to_skip]
        next_move.m_characters_who_can_attack_to_skip = move.m_characters_who_can_attack_to_skip
        next_move.m_attack_targets_to_skip = move.m_attack_targets_to_skip + 1
        try:
            character.attack(target_to_attack)
        finally:
            if silently is False:
                print("{0} attacks {1}".format(character, target_to_attack))

        return [True, next_move]

    except GameOver:
        if player.playstate == PlayState.WON:
            raise
        return [False, next_move]


class GameMove(object):
    move = Move()
    next_move = None

    def __repr__(self):
        return str(self.move)


class GameScore(object):
    player_health = 0
    opponent_health = 0
    total_attack_friendly_minions = 0
    total_attack_enemy_minions = 0
    total_health_friendly_minions = 0
    total_health_enemy_minions = 0

    def is_better(self, other) -> bool:
        if self.total_attack_enemy_minions != other.total_attack_enemy_minions:
            return self.total_attack_enemy_minions < other.total_attack_enemy_minions
        if self.total_health_enemy_minions != other.total_health_enemy_minions:
            return self.total_health_enemy_minions < other.total_health_enemy_minions
        if self.opponent_health != other.opponent_health:
            return self.opponent_health < other.opponent_health
        if self.total_attack_friendly_minions != other.total_attack_friendly_minions:
            return self.total_attack_friendly_minions > other.total_attack_friendly_minions
        if self.total_health_friendly_minions != other.total_health_friendly_minions:
            return self.total_health_friendly_minions > other.total_health_friendly_minions

        if self.player_health != other.player_health:
            return self.player_health > other.player_health
        return False

    def __str__(self):
        return "player[" + \
               str(self.player_health) + " / " + \
               str(self.total_attack_friendly_minions) + " / " + \
               str(self.total_health_friendly_minions) + "] vs opponent" + \
               "[" + \
               str(self.opponent_health) + " / " + \
               str(self.total_attack_enemy_minions) + " / " + \
               str(self.total_health_enemy_minions) + "]"



def get_game_score(game: Game) -> GameScore:
    game_score = GameScore()

    game_score.player_health = game.current_player.hero.health

    for minion in game.current_player.field:
        game_score.total_attack_friendly_minions += minion.atk
        game_score.total_health_friendly_minions += minion.health

    for player in game.players:
        if player != game.current_player:
            game_score.opponent_health = player.hero.health
            for minion in player.field:
                game_score.total_attack_enemy_minions += minion.atk
                game_score.total_health_enemy_minions += minion.health

    return game_score


def replay_game(moves, silently: bool):
    log.disabled = True
    game = load_game()
    if silently is False:
        log.disabled = False
        show_board(game)
        log.disabled = True

    # First replay everything we had already played
    for move_info in moves:
        try:
            temp = play_move(game, move_info.move, silently)
            assert len(temp) == 2
            play_result = temp[0]

            if play_result is False:
                # Something went wrong. Try to re-play the game once again
                # temp = play_move(game, move_info.move, False)
                return replay_game(moves, silently)
            # Moves have previously been played successfully, they MUST be re-played successfully once again
        except GameOver:
            assert game.current_player.playstate == PlayState.WON

    if not silently and len(moves) > 0:
        log.disabled = False
        log.info("Board state after playback:")
        show_board(game)

    log.disabled = False
    return game

def test_full_game():
    moves = list()
    reload_and_replay = True
    new_move = Move()

    best_move_sequence = list()
    best_game_score = None

    while True:
        if reload_and_replay:
            game = replay_game(moves, True)

        try:
            play_result = False
            next_move = None
            if not (new_move is None):
                play_move_silently = True
                log.disabled = play_move_silently
                temp = play_move(game, new_move, play_move_silently)
                log.disabled = False
                assert len(temp) == 2
                play_result = temp[0]
                next_move = temp[1]

            if play_result is False:  # Failed to play the move
                if next_move is None:  # There is no next move available
                    if len(moves) == 0:  # We've checked every possible move, job is done
                        log.info("")
                        log.info("")
                        log.info("")
                        log.info("")
                        log.info("Best game score: {0}, move sequence: {1}".format(best_game_score, best_move_sequence))
                        replay_game(best_move_sequence, False)
                        return
                    new_move = moves[len(moves) - 1].next_move
                    moves.pop()
                    reload_and_replay = True
                else:  # There is another possible move to try
                    new_move = next_move
                    reload_and_replay = False
            else:  # We've successfully played the move, add it to the list of the successfully played moves
                temp = GameMove()
                temp.move = new_move
                temp.next_move = next_move
                moves.append(temp)
                reload_and_replay = False
                move_score = get_game_score(game)
                if (best_game_score is None) or move_score.is_better(best_game_score):
                    best_game_score = move_score
                    best_move_sequence = copy.deepcopy(moves)
                new_move = Move()
        except GameOver:
            assert not (new_move is None)
            moves_played = list()
            moves_played.extend(moves)

            temp = GameMove()
            temp.move = new_move
            moves_played.append(temp)
            log.disabled = False
            for player in game.players:
                if player == game.current_player:
                    if player.playstate == PlayState.WON:
                        log.info("Player wins with this sequence of moves: %r", moves_played)
                    elif player.playstate == PlayState.LOST:
                        log.info("Player loses with this sequence of moves: %r", moves_played)
                    else:
                        log.info("Game ends with a tie")
                    break
            log.disabled = True
            replay_game(moves_played, False)
            if game.current_player.playstate == PlayState.WON:
                return
            else:
                assert len(moves) != 0
                new_move = moves[len(moves) - 1].next_move
                moves.pop()
                reload_and_replay = True


def main():
    cards.db.initialize()
    import time
    start = time.time()
    test_full_game()
    print("Finished in ", time.time() - start, " seconds")


if __name__ == "__main__":
    main()
