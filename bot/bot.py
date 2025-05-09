from sc2.bot_ai import BotAI, Race
from sc2.data import Result
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.unit import Unit
from sc2.units import Units

class CompetitiveBot(BotAI):
    NAME: str = "EggBot[Scripted]"
    """This bot's name"""

    PROPERTIES: dict = {
        "Processing Build Order" : True,
        "Currently Attacking": False,
        "Under Attack": False,
        "Attack Destination": -1
    }

    RACE: Race = Race.Terran
    """This bot's Starcraft 2 race.
    Options are:
        Race.Terran
        Race.Zerg
        Race.Protoss
        Race.Random
    """

    async def on_start(self):
        """
        This code runs once at the start of the game
        Do things here before the game starts
        """
        
        print("Game started.")

    async def on_step(self, iteration: int):
        """
        This code runs continually throughout the game
        Populate this function with whatever your bot should do!
        """
        
        ccs: Units = self.townhalls(UnitTypeId.COMMANDCENTER)
        cc: Unit = ccs.first

        self.PROPERTIES['Attack Destination'] = self.enemy_structures.random_or(self.enemy_start_locations[0]).position
        
        #Build priority order:
        
        if self.supply_left < 4:
            if self.can_afford(UnitTypeId.SUPPLYDEPOT) and self.already_pending(UnitTypeId.SUPPLYDEPOT) < 1:
                await self.build(UnitTypeId.SUPPLYDEPOT, near=cc.position.towards(self.game_info.map_center, 5))
                
        elif self.can_afford(UnitTypeId.SCV) and self.supply_workers < 16 and cc.is_idle:
            cc.train(UnitTypeId.SCV)
                
        elif self.structures(UnitTypeId.BARRACKS).amount < 4:
            if self.can_afford(UnitTypeId.BARRACKS):
                await self.build(UnitTypeId.BARRACKS, near=cc.position.towards(self.game_info.map_center, 5))
                
        elif self.can_afford(UnitTypeId.COMMANDCENTER) and len(self.townhalls) < 2 and self.already_pending(UnitTypeId.COMMANDCENTER) < 1:
            await self.expand_now()
            
                
        #Create troops
            
        # for rax in self.structures(UnitTypeId.BARRACKS).ready.idle:
        #     if self.can_afford(UnitTypeId.MARINE):
        #         rax.train(UnitTypeId.MARINE)
                
        #Send idle scvs to mine
                
        for scv in self.workers.idle:
            scv.gather(self.mineral_field.closest_to(cc))
            
        #Lower supply depots
        
        for depot in self.structures(UnitTypeId.SUPPLYDEPOT).ready.idle:
            depot(AbilityId.MORPH_SUPPLYDEPOT_LOWER)
            
        #Unit macro
        
        marines: Units = self.units(UnitTypeId.MARINE).idle
        if marines.amount > 30:
            self.PROPERTIES['Currently Attacking'] = True

        if self.PROPERTIES['Currently Attacking'] == True:
            for marine in marines:
                marine.attack(self.PROPERTIES['Attack Destination'])
        
        pass

    async def on_end(self, result: Result):
        """
        This code runs once at the end of the game
        Do things here after the game ends
        """
        print("Game ended.")
