from sc2.bot_ai import BotAI, Race
from sc2.data import Result
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.unit import Unit
from sc2.units import Units

class CompetitiveBot(BotAI):
    NAME: str = "EggBot[Scripted]"
    """This bot's name"""

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
        
        #Build priority order:
        
        if self.supply_left < 4:
            if self.can_afford(UnitTypeId.SUPPLYDEPOT) and self.already_pending(UnitTypeId.SUPPLYDEPOT) < 1:
                await self.build(UnitTypeId.SUPPLYDEPOT, near=cc.position.towards(self.game_info.map_center, 5))
                
        elif self.can_afford(UnitTypeId.SCV) and self.supply_workers < 16 and cc.is_idle:
            cc.train(UnitTypeId.SCV)
            print('trainingSCV')
                
        elif self.structures(UnitTypeId.BARRACKS).amount < 4:
            if self.can_afford(UnitTypeId.BARRACKS):
                await self.build(UnitTypeId.BARRACKS, near=cc.position.towards(self.game_info.map_center, 5))
                
        #Create troops
            
        for rax in self.structures(UnitTypeId.BARRACKS).ready.idle:
            if self.can_afford(UnitTypeId.MARINE):
                rax.train(UnitTypeId.MARINE)
                
        #Send idle scvs to mine
                
        for scv in self.workers.idle:
            scv.gather(self.mineral_field.closest_to(cc))
            
        #Lower supply depots
        
        for depot in self.structures(UnitTypeId.SUPPLYDEPOT).ready.idle:
            depot(AbilityId.MORPH_SUPPLYDEPOT_LOWER)
            
        #Unit macro
        
        marines: Units = self.units(UnitTypeId.MARINE).idle
        if marines.amount > 30:
            point2 = self.enemy_structures.random_or(self.enemy_start_locations[0]).position
            for marine in marines:
                marine.attack(point2)
        
        pass

    async def on_end(self, result: Result):
        """
        This code runs once at the end of the game
        Do things here after the game ends
        """
        print("Game ended.")
