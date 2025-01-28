import random
import time
import os
import platform

class Fighter:
    def __init__(self, name, attack, defense, title="Novice",  fighter_class="Berserker", maxTraits=3):
        self.name = name
        self.attack = attack
        self.defense = defense
        self.alive = True
        self.title = title
        self.fighter_class = fighter_class  
        self.title_levels = [
            "Novice",        # Level 1
            "Trainee",       # Level 2
            "Apprentice",    # Level 3
            "Journeyman",    # Level 4
            "Adept",         # Level 5
            "Veteran",       # Level 6
            "Elite",         # Level 7
            "Champion",      # Level 8
            "Master",        # Level 9
            "Legend",         # Level 10
            "Mythical",      # Level 11
            "Godlike",        # Level 12
            "Divine",        # Level 13 
        ]
        self.unique_traits = {
            # Unique traits that fighters can have 1-3 of when they are created
            "Unstoppable": f"Gains 5 defense when attacked.",
            "Swift": f"Gains 5 attack when attacking.",
            "Fierce": f"Has a 5% chance of attacking twice.",
            "Cunning": f"Has a 5% chance to dodge attacks.",
            "Mighty": f"Has a 5% chance to deal double damage.",
            "Stalwart": f"Gains 2 more defense and damage when meditating.",
            "Thorns": f"Deal 3% damage back to attacker, minimum of 1 damage.",
            "Vengeful": f"1% chance to attack an enemy that attacked you.",
            "Mystic": f"Gain 5% of damage dealt as defense.",
            "Untrustworthy": f"Reflect 10% of damage taken onto teammates.",
            "Noble": f"Gains 8 defense and 8 attack when another fighter is defeated",
            "Savage": f"Deal 10% more damage when attacking defense stat",
            "Brutal": f"Deal 10% more damage when attacking attack stat",
            "Perceptive": f"Attack 2 enemies instead of 1 dealing 55% damage to each"
        }
        # Randomly assign 1-3 unique traits to the fighter, there cannot be duplicate traits
        self.traits = random.sample(list(self.unique_traits.keys()), random.randint(1, maxTraits))
        self.sword = None  # Stores the equipped sword stats (int)
        self.shield = None  # Stores the equipped shield stats (int)

    def take_damage(self, damage, attacker):
        if self.defense > 0:
            damage_to_defense = min(damage, self.defense)
            self.defense -= damage_to_defense
            if (self.fighter_class == "Tank"):
                damage = max(0, damage - damage_to_defense//2)
            else:
                damage = max(0, damage - damage_to_defense)

        if damage > 0:
            damage_to_attack = damage // 3
            self.attack -= damage_to_attack
            if self.attack <= 0:
                self.alive = False
                self.attack = 0
        if "Unstoppable" in self.traits:
            self.defense += 5
        if "Swift" in attacker.traits:
            attacker.attack += 5
        
        if self.sword or self.shield:
            self.check_destroy_items()
        if not self.alive:
            print(f"{self.name} has been defeated!")
            attacker.upgrade_title()
            time.sleep(1)

    def equip_item(self, item_type, stat_bonus):
        if item_type == "sword":
            old_item = self.sword
            # Calculate the stat difference
            stat_difference = stat_bonus - (old_item if old_item else 0)
            self.attack += stat_difference
            self.attack = max(0, self.attack)  # Ensure attack is not negative
            self.sword = stat_bonus
            print(f"{self.name} equipped a sword with +{stat_bonus} Attack!")
            if old_item:
                print(f"Replaced old sword with +{old_item} Attack.")
                print(f"{self.name}'s attack adjusted by {stat_difference}.")
        elif item_type == "shield":
            old_item = self.shield
            # Calculate the stat difference
            stat_difference = stat_bonus - (old_item if old_item else 0)
            self.defense += stat_difference
            self.defense = max(0, self.defense)  # Ensure defense is not negative
            self.shield = stat_bonus
            print(f"{self.name} equipped a shield with +{stat_bonus} Defense!")
            if old_item:
                print(f"Replaced old shield with +{old_item} Defense.")
                print(f"{self.name}'s defense adjusted by {stat_difference}.")

    def check_destroy_items(self):
        # Skip checking for enemies since they don't have items
        if not self.sword and not self.shield:
            return

        # Destroy sword if attack is less than 1
        if self.sword and self.attack < 1:
            print(f"{self.name}'s sword with +{self.sword} Attack was destroyed!")
            self.sword = None

        # Destroy shield if defense is less than 1
        if self.shield and self.defense < 1:
            print(f"{self.name}'s shield with +{self.shield} Defense was destroyed!")
            self.shield = None

            
    def upgrade_title(self):
        if self.alive:
            current_index = self.title_levels.index(self.title)
            # Calculate the chance of upgrading based on the current title level
            upgrade_chance = 0.25 - (current_index * 0.02)
            if (upgrade_chance < 0.01):
                upgrade_chance = 0.01

            # Attempt to upgrade the title
            if random.random() <= upgrade_chance:
                if current_index < len(self.title_levels) - 1:
                    self.title = self.title_levels[current_index + 1]
                    print(f"{self.name} has earned the prestigious title of {self.title}!")
                    
    def calculate_damage(self):
        """Calculate attack damage based on class-specific traits."""
        if self.fighter_class == "Berserker":
            return random.randint(self.attack, int(self.attack * 1.4))
        elif self.fighter_class == "Tank":
            return random.randint(self.attack // 2, self.attack)
        elif self.fighter_class == "Rogue":
            critical_chance = 0.25
            damage = random.randint(round(self.attack/1.5), self.attack)
            if random.random() < critical_chance:
                damage *= 2
                print(f"Critical hit by {self.name}!")
            return damage
        elif self.fighter_class == "Mage":
            # Mages deal damage to all enemies at once
            return random.randint(round(self.attack/8), round(self.attack/4))
        elif self.fighter_class == "Healer":
            #Check if healer is the only one alive, if so they will attack instead of heal.
            if len([f for f in self.team if f.alive]) == 1:
                return random.randint(self.attack//4, self.attack//2)
            else:
                return 0  # Healers don't deal damage unless they are the only one alive.
        else:
            return self.attack  # Default case

    def HealTeammate(self, team):
        target = min([f for f in team if f.alive and f != self], key=lambda f: f.defense)
        heal_amount = random.randint(round(self.attack/7), round(self.attack/3))
        #Check if the target's defense is going to be greater than the healer's attack stat after they are healed.
        if target.defense + heal_amount > self.attack:
            target.defense = self.attack
        else:
            target.defense += heal_amount
        print(f"{self.name} healed {target.name} for {heal_amount} defense!")
        time.sleep(1)

    def __str__(self):
        sword_info = f"Sword: +{self.sword} Attack" if self.sword else "No Sword"
        shield_info = f"Shield: +{self.shield} Defense" if self.shield else "No Shield"
        return f"{self.name} the {self.title} {self.fighter_class} - Attack: {self.attack}, Defense: {self.defense} ({sword_info}, {shield_info})"


class Game:
    def __init__(self):
        self.day = 1
        self.team = [Fighter(self.get_player_name(), 150, 100, title="Apprentice")]
        self.max_team_size = 5
        self.running = True
        self.first_event = True  # A flag to ensure the first event is a recruitment event
        self.gold = 300 
        self.fighter_names = [
            "Shadow", "Blaze", "Steel", "Rogue", "Fang", "Bolt", "Hawk", "Viper", "Phantom", "Claw",
            "Dagger", "Storm", "Venom", "Ghost", "Flame", "Hunter", "Wolf", "Lynx", "Raven", "Scorpion",
            "Eagle", "Tiger", "Cobra", "Sabre", "Crusher", "Sniper", "Falcon", "Phoenix", "Inferno", "Blade",
            "Warrior", "Gladiator", "Thunder", "Zephyr", "Reaper", "Cyclone", "Razor", "Kraken", "Titan", "Predator",
            "Serpent", "Maverick", "Berserker", "Executioner", "Drake", "Archer", "Warden", "Sphinx", "Tempest", "Leopard",
            "Shredder", "Griffin", "Juggernaut", "Raptor", "Hydra", "Avenger", "Destroyer", "Nightmare", "Overlord", "Mercenary",
            "Samurai", "Knight", "Centurion", "Vanguard", "Sentinel", "Paladin", "Champion", "Barbarian", "Seeker", "Slayer",
            "Saber", "Commander", "Demolisher", "Wraith", "Assassin", "Sparrow", "Valkyrie", "Banshee", "Vindicator", "Tracker",
            "Hunter", "Dominator", "Ranger", "Scout", "Warlord", "Conqueror", "Tactician", "Gunner", "Marksman", "Brawler",
            "Invoker", "Guardian", "Shaman", "Oracle", "Visionary", "Crusader", "Pathfinder", "Striker", "Pioneer", "Fury",
            "Breaker", "Rogue", "Shadowblade", "Darkfang", "Bloodfang", "Venomblade", "Ironclad", "Steelsoul", "Blackthorn", "Ironfang",
            "Silentfang", "Stormbringer", "Thundersoul", "Darkflame", "Flamefang", "Lunarblade", "Solarfang", "Voidwalker", "Netherfang", "Celestial",
            "Eclipse", "Nova", "Radiant", "Dawnblade", "Duskfang", "Starlight", "Moonshadow", "Sunfire", "Nightstalker", "Lightbringer",
            "Skybreaker", "Earthshaker", "Seafang", "Wavebringer", "Tsunami", "Cyclonefang", "Hurricane", "Typhoon", "Avalanche", "Quake",
            "Rockfang", "Firestorm", "Blizzardfang", "Frostfang", "Glacier", "Iceshard", "Winterfang", "Snowstalker", "Frostclaw", "Coldfang",
            "Wildfang", "Savageclaw", "Primefang", "Ancientclaw", "Beastfang", "Natureclaw", "Junglefang", "Woodfang", "Swampfang", "Riverclaw",
            "Volcanofang", "Desertclaw", "Sandfang", "Oasisfang", "Duneclaw", "Mountainfang", "Peakclaw", "Skyfang", "Cloudclaw", "Stormclaw",
            "Zephyrfang", "Galeclaw", "Breezeclaw", "Tempestfang", "Thunderfang", "Shockclaw", "Surgefang", "Boltclaw", "Lightningfang", "Flashclaw",
            "Energyfang", "Sparkclaw", "Voltclaw", "Powerfang", "Magnetclaw", "Steelclaw", "Copperclaw", "Ironclaw", "Bronzeclaw", "Silverfang",
            "Goldfang", "Platinumclaw", "Diamondfang", "Gemclaw", "Rubyfang", "Emeraldclaw", "Sapphirefang", "Topazclaw", "Crystalclaw", "Quartzfang",
            "Amethystclaw", "Opalfang", "Pearlclaw", "Obsidianfang", "Onyxclaw", "Moonstonefang", "Sunstoneclaw", "Starstonefang", "Meteorclaw", "Astrofang",
            "Cometclaw", "Nebulafang", "Galaxyclaw", "Cosmofang", "Orbclaw", "Etherealfang", "Spiritclaw", "Soulfang", "Ghostclaw", "Phantomfang",
            "Specterclaw", "Wraithfang", "Bansheefang", "Demonclaw", "Hellfang", "Infernalclaw", "Abyssfang", "Voidclaw", "Shadowfang", "Darkclaw",
            "Blackfang", "Nightclaw", "Twilightfang", "Eclipticclaw", "Solarflare", "Darkstorm", "Netherstorm", "Shadowstorm", "Bloodstorm", "Firestorm",
            "Icestorm", "Wildstorm", "Primalstorm", "Savagestorm", "Earthstorm", "Skyfury", "Ironfury", "Goldfury", "Silverfury", "Gemfury",
            "Rubyfury", "Emeraldfury", "Sapphirefury", "Topazfury", "Diamondfury", "Crystalstorm", "Obsidianfury", "Onyxfury", "Moonstonefury", "Sunstonefury",
            "Starfury", "Meteorstorm", "Astrofury", "Cometfury", "Nebulafury", "Galaxyfury", "Cosmofury", "Etherealfury", "Soulstorm", "Phantomstorm",
            "Wraithstorm", "Spectralstorm", "Demonstorm", "Infernalstorm", "Abyssstorm", "Voidstorm", "Darkstorm", "Nightfury", "Twilightfury", "Eclipsefury",
            "Lightstorm", "Radiantfury", "Dawnstorm", "Duskstorm", "Starlitstorm", "Moonshadowstorm", "Sunfirestorm", "Wildfire", "Blazefury", "Froststorm",
        ]


    def get_player_name(self):
        return input("Enter the name of your first fighter: ").strip()
    
    def random_event(self):
        if self.first_event:
            # First event is always a recruitment event
            self.recruit_event()
            self.first_event = False
        else:
            # Weighted random event selection
            event_type = random.choices(
                ["fight", "recruit", "find_item", "shop", "meditate", "boss"],
                # Percentage chance of each event type that is balanced and totals 100%
                weights=[25, 15, 5, 15, 35, 5],  
                k=1
            )[0]

            if event_type == "fight":
                self.fight_event()
            elif event_type == "recruit":
                self.recruit_event()
            elif event_type == "find_item":
                self.find_item_event()
            elif event_type == "shop":
                self.shop_event()
            elif event_type == "meditate":
                self.meditate_event()
            elif event_type == "boss":
                self.boss_event()

    def shop_event(self):
        print(f"You encounter a shop!")
        self.display_team(show_items=True, show_traits=False)
        items = []

        # Generate 3 random items (swords or shields)
        for _ in range(3):
            item_type = random.choice(["sword", "shield"])
            stat_bonus = random.randint(10 + self.day, 20 + (self.day * 4))
            base_price = round(stat_bonus * 1.25)
            sale = None
            discount_percentage = 0

            # 20% chance for the item to be on sale
            if random.random() <= 0.20:
                discount_percentage = random.randint(10, 70)  # 10%-90% discount
                sale = round(base_price * (1 - discount_percentage / 100))
            
            items.append({
                "type": item_type,
                "bonus": stat_bonus,
                "price": base_price,
                "sale": sale,
                "discount": discount_percentage,
                "sold_out": False  # Track if the item is sold out
            })

        # Display items in the shop
        while True:
            print(f"\nYour gold: {self.gold}")
            print("\nItems available in the shop:")
            for i, item in enumerate(items, start=1):
                if item["sold_out"]:
                    print(f"{i}. SOLD OUT")
                else:
                    if item["sale"]:
                        sale_info = f"({item['discount']}% off!)"
                        price_display = f"{item['sale']} gold"
                    else:
                        sale_info = ""
                        price_display = f"{item['price']} gold"

                    print(f"{i}. {item['type'].capitalize()} (+{item['bonus']} {'Attack' if item['type'] == 'sword' else 'Defense'}) - {price_display} {sale_info}")

            # Allow the player to buy items
            choice = input("Enter the number of the item to buy (1-3) or 0 to skip: ").strip()
            clear_screen()
            if not choice.isdigit() or not (0 <= int(choice) <= 3):
                print("Invalid input. Please choose a valid option.")
                continue

            choice = int(choice)
            if choice == 0:
                print("You leave the shop.")
                return

            selected_item = items[choice - 1]

            # Check if the item is already sold out
            if selected_item["sold_out"]:
                print("This item is already sold out. Please choose another option.")
                continue

            item_price = selected_item["sale"] or selected_item["price"]

            if self.gold >= item_price:
                self.gold -= item_price
                clear_screen()
                print(f"You bought the {selected_item['type']} for {item_price} gold!")
                
                # Let the player equip the item
                self.display_team(show_items=True, show_traits=False)
                fighter_choice = input(f"Choose a fighter to equip the {selected_item['type']} (1-{len(self.team)}) or 0 to discard: ").strip()
                clear_screen()
                if fighter_choice.isdigit() and 1 <= int(fighter_choice) <= len(self.team):
                    fighter_choice = int(fighter_choice) - 1
                    self.team[fighter_choice].equip_item(selected_item["type"], selected_item["bonus"])
                    print(f"{selected_item['type'].capitalize()} equipped to {self.team[fighter_choice].name}!")
                else:
                    print("Item discarded.")

                # Mark the item as sold out
                selected_item["sold_out"] = True
            else:
                print("You don't have enough gold to buy this item!")


    def fight_event(self):
        enemy_count = random.randint(1, 5)
        stat_multiplier = {1: 1.2, 2: 1.0, 3: 0.85, 4: 0.75, 5: 0.65}

        enemies = [
            Fighter(
                f"Enemy {i+1}",
                int(random.randint(75 + self.day * 2, 140 + self.day * 4) * stat_multiplier[enemy_count]),
                int(random.randint(50 + self.day * 2, 100 + self.day * 4) * stat_multiplier[enemy_count]),
                #Random title chance for enemies, as more days progress the chance for a better title increases
                title=random.choices(
                    ["Novice", "Trainee", "Apprentice", "Journeyman", "Adept", "Veteran", "Elite", "Champion", "Master", "Legend"],
                    weights=[50, 20, 10, 5, 5, 3, 3, 2, 1, 1],
                    k=1
                )[0],
                fighter_class=random.choice(["Berserker", "Tank", "Healer", "Rogue", "Mage"])
            )
            for i in range(enemy_count)
        ]
        print(f"\nDay {self.day}: A fight has started against {enemy_count} enemies!")
        self.turn_based_combat(enemies)

    def boss_event(self):
        print(f"Day {self.day}: A boss fight has started!")
        boss = Fighter("Boss", 150 + self.day * 5, 200 + self.day * 6)
        self.turn_based_combat([boss])



    def recruit_event(self):
        if not self.fighter_names:
            print("\nNo more random names available. Recruitment event skipped.")
            return

        fighter_classes = ["Berserker", "Tank", "Healer", "Rogue", "Mage"]
        fighter_options = []
        for _ in range(3):
            name = self.fighter_names.pop(random.randint(0, len(self.fighter_names) - 1))
            attack = random.randint(25 + self.day, 100 + self.day * 2)
            defense = random.randint(20 + self.day, 80 + self.day * 2)
            fighter_class = random.choice(fighter_classes)
            cost = round(((attack*1.5) + (defense*1.1)))
            if random.random() <= 0.1:  # 10% chance the fighter is free
                cost = 0
            fighter_options.append({
                "fighter": Fighter(name, attack, defense, fighter_class=fighter_class),
                "cost": cost,
                "sold": False  # Track whether the fighter is sold
            })

        while True:
            clear_screen()
            self.display_team(show_items=False, show_traits=True)
            print(f"\nDay {self.day}: You have encountered potential recruits!")
            print(f"Your gold: {self.gold}\n")

            # Display the 3 fighter options
            for i, option in enumerate(fighter_options, start=1):
                if option["sold"]:
                    print(f"{i}. SOLD")
                else:
                    cost_display = "Willing to be on your team for free!" if option["cost"] == 0 else f"{option['cost']} gold"
                    #Print fighter without showing equipped sword or shield and show the fighter's unique traits
                    traits_display = ", ".join(option['fighter'].traits)
                    print(f"{i}. {option['fighter'].name} the {option['fighter'].fighter_class} - Attack: {option['fighter'].attack}, Defense: {option['fighter'].defense} | Traits: {traits_display} - Costs: {cost_display}.")

            print("\nYou may recruit multiple fighters, as long as you can afford them and stay within the team limit.")
            choice = input("Enter the number of the fighter to recruit (1-3) or 0 to skip: ").strip()

            if not choice.isdigit() or not (0 <= int(choice) <= 3):
                print("Invalid input. Please enter a valid number.")
                continue

            choice = int(choice)
            if choice == 0:
                print("Recruitment event ended.")
                return

            selected_option = fighter_options[choice - 1]

            # Check if the fighter is already sold
            if selected_option["sold"]:
                print("This fighter has already been recruited. Please choose another.")
                continue

            cost = selected_option["cost"]

            # Check if the fighter is affordable
            if cost > self.gold:
                print("You don't have enough gold to recruit this fighter.")
                continue

            # Deduct gold if applicable and add the fighter to the team
            self.gold -= cost
            clear_screen()
            print(f"\nYou recruited {selected_option['fighter'].name} ({selected_option['fighter'].fighter_class} for {'free' if cost == 0 else f'{cost} gold'}!")

            # If the team has room, add the new fighter directly
            if len(self.team) < self.max_team_size:
                self.team.append(selected_option["fighter"])
                print(f"{selected_option['fighter'].name} has joined your team!")
            else:
                # If the team is full, ask the player to replace an existing fighter
                print("\nYour team is full! Choose a fighter to replace or skip recruitment.")
                self.display_team(show_items=False, show_traits=True)
                while True:
                    replace_choice = input("Enter the number of the fighter to replace (1-3) or 0 to skip: ").strip()
                    if not replace_choice.isdigit() or not (0 <= int(replace_choice) <= len(self.team)):
                        print("Invalid input. Please enter a valid number.")
                        continue

                    replace_choice = int(replace_choice) - 1
                    if replace_choice == -1:  # Skip replacement
                        print("Recruitment skipped.")
                        break

                    print(f"{self.team[replace_choice]} has been replaced by {selected_option['fighter']}.")
                    self.team[replace_choice] = selected_option["fighter"]
                    break

            # Mark the recruited fighter as sold
            selected_option["sold"] = True

            # Show updated team
            print("\nUpdated Team:")


    def meditate_event(self):
        print(f"Your fighters meditate to enhance their stats!\n")
        for fighter in self.team:
            max_boost = 10 + self.fighter_title_bonus(fighter.title)
            attack_boost = random.randint(5, max_boost)
            defense_boost = random.randint(5, max_boost)
            fighter.attack += attack_boost
            fighter.defense += defense_boost
            print(f"{fighter.name} ({fighter.title}) gained {attack_boost} Attack and {defense_boost} Defense through meditation.")
        self.display_team(show_items=False, show_traits=False)

    def find_item_event(self):
        clear_screen()
        item_type = random.choice(["sword", "shield"])  # Determine item type
        max_stat_bonus = 10 + (self.day*3)  # Stat bonus scales with the current day
        stat_bonus = random.randint(5, max_stat_bonus)  # Random stat bonus
        item_name = f"{item_type.capitalize()} (+{stat_bonus} {'Attack' if item_type == 'sword' else 'Defense'})"
        print(f"\nDay {self.day}: You found a {item_name}!")

        # Let the player choose a fighter to give the item to
        print("\nCurrent Fighter Stats:")
        self.display_team(show_items=True, show_traits=False)
        choice = int(input(f"Choose a fighter to give the {item_name} (1-{len(self.team)}) or 0 to skip: ")) - 1
        if choice.isdigit() and 1 <= int(choice) <= len(self.team):
            clear_screen()
            if 0 <= choice < len(self.team):
                self.team[choice].equip_item(item_type, stat_bonus)
            else:
                print("Item skipped.")


    def fighter_title_bonus(self, title):
        #Calculate bonus to stat boosts based on fighter title. Each bonus increases by 5 from previous title
        title_bonus = {
            "Novice": 0,         # Level 1
            "Trainee": 5,        # Level 2 (+5 from Novice)
            "Apprentice": 10,    # Level 3 (+6 from Trainee)
            "Journeyman": 15,    # Level 4 (+7 from Apprentice)
            "Warrior": 20,       # Level 5 (+8 from Journeyman)
            "Veteran": 25,       # Level 6 (+9 from Warrior)
            "Elite": 30,         # Level 7 (+10 from Veteran)
            "Champion": 35,      # Level 8 (+11 from Elite)
            "Master": 40,        # Level 9 (+12 from Champion)
            "Legend": 45,         # Level 10 (+13 from Master)
            "Mythical": 50,      # Level 11 (+14 from Legend)
            "Godlike": 55,       # Level 12 (+15 from Mythical)
            "Divine": 60        # Level 13 (+16 from Godlike)
        }
        return title_bonus.get(title, 0)

    def turn_based_combat(self, enemies):
        while any(f.alive for f in self.team) and any(e.alive for e in enemies):
            clear_screen()
            print("\n--- Battle Round ---")
            self.display_combatants("Team", self.team)
            self.display_combatants("Enemies", enemies)
            print(f"\n")

            def combat_turn(attacker, targets, is_team):
                if attacker.alive and any(t.alive for t in targets):
                    if attacker.fighter_class == "Healer" and len([f for f in self.team if f.alive]) > 1:
                        attacker.HealTeammate(self.team if is_team else targets)
                    elif attacker.fighter_class == "Mage":
                        damage = attacker.calculate_damage()
                        print(f"{attacker.name} the {attacker.title} {attacker.fighter_class} attacks all enemies for {damage} damage!")
                        for target in targets:
                            if target.alive:
                                target.take_damage(damage, attacker)
                        if "Fierce" in attacker.traits and random.random() < 0.05:
                            print(f"{attacker.name} attacks again due to Fierce trait!")
                            for target in targets:
                                if target.alive:
                                    target.take_damage(damage, attacker)
                    else:
                        target = random.choice([t for t in targets if t.alive])
                        damage = attacker.calculate_damage()
                        print(f"{attacker.name} the {attacker.title} {attacker.fighter_class} attacks {target.name} for {damage} damage!")
                        target.take_damage(damage, attacker)
                        if "Fierce" in attacker.traits and random.random() < 0.05:
                            print(f"{attacker.name} attacks again due to Fierce trait!")
                            target = random.choice([t for t in targets if t.alive])
                            damage = attacker.calculate_damage()
                            print(f"{attacker.name} the {attacker.title} {attacker.fighter_class} attacks {target.name} for {damage} damage!")
                            target.take_damage(damage, attacker)
                    time.sleep(1)

            # Team's turn to attack
            for fighter in list(self.team):  # Use a copy of the team to prevent modification issues
                combat_turn(fighter, enemies, is_team=True)

            # Enemies' turn to attack
            for enemy in enemies:
                combat_turn(enemy, self.team, is_team=False)

            # Remove defeated fighters from the team
            self.team = [fighter for fighter in self.team if fighter.alive]
            # Remove defeated enemies from the enemy group
            enemies = [enemy for enemy in enemies if enemy.alive]
            #Pause and wait for any input so the player can see the results of the round
            input("\nPress Enter to continue to the next round...")
        print("\n--- Battle Results ---")
        if all(not e.alive for e in enemies):
            print("You won the fight!")
            #Check if the enemy is a boss.
            if len(enemies) == 1 and enemies[0].name == "Boss":
                goldMultiplier = 6
                itemChance = 0.20
            else:
                goldMultiplier = 4
                itemChance = 0.15
            earnedGold = self.day * goldMultiplier
            self.gold += earnedGold
            if random.random() <= itemChance:
                self.find_item_event()
            print(f"You earned {earnedGold} gold! Current gold: {self.gold}")
        else:
            print("Your team lost the fight and died!")
            self.running = False


    def display_combatants(self, group_name, fighters):
        print(f"\n{group_name}:")
        # get terminal height for both windows and linux
        if platform.system() == "Windows":
            rows, columns = os.popen('mode con', 'r').read().split()[1:3]
        else:
            rows, columns = os.popen('stty size', 'r').read().split()
        # two modes , compact and full
        if int(rows) < 30:
            for fighter in fighters:
                fighterTitle = f"{fighter.name} the {fighter.title} {fighter.fighter_class}"
                sword_info = f"Sword: +{fighter.sword} Attack" if fighter.sword else "No Sword"
                shield_info = f"Shield: +{fighter.shield} Defense" if fighter.shield else "No Shield"
                trait_info = f" | Traits: {', '.join(fighter.traits)} "
                print(f"  {fighterTitle} - Attack: {fighter.attack}, Defense: {fighter.defense} | Items: {sword_info}, {shield_info} {trait_info}")
        else:
            for fighter in fighters:
                print(f"  {fighter}")
                sword_info = f"    {fighter.sword} Attack" if fighter.sword else "No Sword"
                shield_info = f"    {fighter.shield} Defense" if fighter.shield else "No Shield"
                print(f"    {sword_info}, {shield_info}")
                print(f"    Traits: {', '.join(fighter.traits)}")

    def display_compact_team(self, show_items=True, show_traits=True):
        print("\nYour Team:")
        for i, fighter in enumerate(self.team, start=1):
            fighterTitle = f"{fighter.name} the {fighter.title} {fighter.fighter_class}"
            if show_items:
                sword_info = f"Sword: +{fighter.sword} Attack" if fighter.sword else "No Sword"
                shield_info = f"Shield: +{fighter.shield} Defense" if fighter.shield else "No Shield"
                item_info = f" | Items: {sword_info}, {shield_info} "
            else:
                item_info = ""
            if show_traits:
                trait_info = f" | Traits: {', '.join(fighter.traits)} "
            else:
                trait_info = ""
            print(f"{i}. {fighterTitle} - Attack: {fighter.attack}, Defense: {fighter.defense}{item_info}{trait_info}")
    
    def display_full_team(self, show_items=True, show_traits=True):
        print("\nYour Team:")
        for fighter in self.team:
            print(f"  {fighter}")
            if show_items:
                sword_info = f"    {fighter.sword} Attack" if fighter.sword else "No Sword"
                shield_info = f"    {fighter.shield} Defense" if fighter.shield else "No Shield"
                print(f"    {sword_info}, {shield_info}")
            if show_traits:
                print(f"    Traits: {', '.join(fighter.traits)}")

    def display_team(self, show_items=True, show_traits=True):
        # get terminal hight for both windows and linux
        if platform.system() == "Windows":
            rows, columns = os.popen('mode con', 'r').read().split()[1:3]
        else:
            rows, columns = os.popen('stty size', 'r').read().split()
        # two modes , compact and full
        if int(rows) < 30:
            self.display_compact_team(show_items, show_traits)
        else:
            self.display_full_team(show_items, show_traits)


    def play(self):
        while True:  # Keep restarting the game on defeat
            print("Welcome to the Fighter Game!")
            self.running = True  # Ensure the game loop runs
            while self.running:
                clear_screen()
                print(f"\n--- Day {self.day} ---")
                self.random_event()
                self.day += 1
                input("Press Enter to continue to the next day...")

            print("Game Over! You survived for", self.day - 1, "days.")
            self.reset_game()  # Restart the game after defeat


    def reset_game(self):
        """Reset the game state to start a new playthrough."""
        print("\nRestarting the game...")
        game = Game()
        game.play()



def clear_screen():
    """Clear the console screen."""
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

if __name__ == "__main__":
    game = Game()
    game.play()
