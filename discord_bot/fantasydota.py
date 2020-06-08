"""
Fantasy Dota cog
"""
import logging
import uuid
from pprint import pformat

from discord import PermissionOverwrite
from discord.ext import commands
from discord.utils import get as dget  # This cant go wrong surely


from messages.fantasy_msgs import DraftQueue, ExternalUser, FantasyTeam, DraftPick
from utils.channel_text import SCORING_TEXT, HELP_TEXT, RULES_TEXT
from utils.errors import ApiException
from utils.utils import simplified_str
from data.dota_ids import FANTASY_LEAGUE_ID


logger = logging.getLogger(__name__)

CATEGORY_NAME = 'Fantasy Dota'
HELP_CHANNELS = {
    'Help': HELP_TEXT,
    'Rules': RULES_TEXT,
    'Scoring': SCORING_TEXT
}
PRIVATE_CHANNELS = ['Leaderboard', 'Pro Leaderboard']
PUBLIC_CHANNELS = ['Chat']


class FantasyDota(commands.Cog):
    """An awesome fantasy dota 2 dota league"""
    def __init__(self, bot):
        self.bot = bot
        self.confirm_flag = False

    @property
    def fantasy_handler(self):
        return self.bot.fantasy_handler

    @property
    def player_handler(self):
        return self.bot.player_handler

    # Listeners

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # TODO welcome member suggest they join bla bla
        pass
        # channel = member.guild.system_channel
        # if channel is not None:
        #     await channel.send('Welcome {0.mention}.'.format(member))

    @commands.Cog.listener()
    async def on_ready(self):
        """Initial discord related set up 

        TODO:
        - Do we need to worry about the below warning?
            Warning This function is not guaranteed to be the first event called.
            Likewise, this function is not guaranteed to only be called once.
            This library implements reconnection logic and thus will end up calling
            this event whenever a RESUME request fails.
        """
        logger.info("Cog: On Ready enter")
        for guild in self.bot.guilds:
            # TODO create method for this
            logger.info(f"Cog: Checking required channels for {guild.name}")
            category = dget(guild.categories, name=CATEGORY_NAME)
            if category:
                logger.info(f"Cog: Help category found")
                # For now just assume if catgeory is there we're done
            else:
                logger.info(f'Cog: Category not found - creating')
                # TODO force category at top?
                overwrites = {
                    guild.default_role: PermissionOverwrite(send_messages=False),
                }
                new_category = await guild.create_category(CATEGORY_NAME, overwrites=overwrites)
                logger.info(f'Cog: New category created - adding and populating channels')
                for name in HELP_CHANNELS:
                    new_channel = await guild.create_text_channel(name, category=new_category,
                                                                  overwrites=overwrites)
                    await new_channel.send(HELP_CHANNELS[name])
                logger.info(f'Cog: All help channels added and populated succsfully')
                for name in PRIVATE_CHANNELS:
                    await guild.create_text_channel(name, category=new_category)
                overwrites = {
                    guild.default_role: PermissionOverwrite(send_messages=True),
                }
                for name in PUBLIC_CHANNELS:
                    await guild.create_text_channel(name, category=new_category,
                                                    overwrites=overwrites)
                logger.info(f"Cog: All other channels created")
        logger.info("Cog On Ready leave")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Handle joining a guild

        Does nothing atm but will want to run the same kind of create channels init
        set up we run on all guilds in on ready probs
        """
        

    # TODO show we allow the public commands to also be called form dms?
    # TODO maybe group rules/scoring by eg info - `info scoring/rules`
    # TODO if get fancy, make a custom check for whether the rules/scoring/help
    # commands are useable. for now only owner can use
    @commands.command()
    @commands.is_owner()
    async def rules(self, ctx):
        """List the rules"""
        await ctx.send(RULES_TEXT)

    @commands.command()
    @commands.is_owner()
    async def scoring(self, ctx):
        """List the scoring system"""
        await ctx.send(SCORING_TEXT)

    @commands.command()
    async def teams(self, ctx):
        """Display all teams. If used in draft channel shows only drafters teams."""
        # TODO
        draft_id = self.fantasy_handler.channel_ids_to_draft_ids.get(ctx.channel.id)
        teams = await self.fantasy_handler.client.send_get_latest_teams()
        team_ids_to_player_ids = teams["data"]
        printy = ""
        for team_id, player_ids in team_ids_to_player_ids.items():
            if not draft_id or self.fantasy_handler.team_id_to_draft_id.get(team_id) == draft_id:
                user = self.fantasy_handler.get_user_by_team_id(team_id)
                players = [self.player_handler.player_id_to_names[pid] for pid in player_ids]
                printy += f'**{user.name}**:  {", ".join(players)}\n\n'
        await ctx.send(printy)

    @commands.group()
    async def show(self, ctx):
        """Display various information"""
        if ctx.invoked_subcommand is None:
            await ctx.send("What would you like to show?")
    
    @show.command()
    async def leaderboard(self, ctx):
        """Display current leaderboard"""
        # TODO
        await ctx.send("Nice leaderboard you got here")

    @show.command()
    async def team(self, ctx):
        """Display your team"""
        # TODO
        await ctx.send(f'{ctx.author.name} wants to see their team right about now')

    # TODO CT display all teams (maybe a read-only channel rather than commands)

    @commands.command()
    async def join(self, ctx):
        """Join the league!
        """
        # TODO:
        # - get proper fantasy id from somewhere
        # - other error handling?
        # - move this stuff into listener? or somewhere more sensible
        # @IMPROVE
        # - better api call to check user exists rather than keeping state
        new_username = f'{ctx.author.name}#{ctx.author.discriminator}'  # do we want to use discriminator?
        new_user_id = ctx.author.id  # should this be string? (doesnt matter what type)
        if new_user_id in self.fantasy_handler.discord_user_id_to_fantasy_id:
            logger.warning(f'existing user {ctx.author.name} tried to join league')
            await ctx.send(f"Hey {ctx.author.name}, you're already in this league. Ya chump")
            return

        user = ExternalUser(str(uuid.uuid4()), new_username, meta={'discord_id': new_user_id})
        team = FantasyTeam(
            str(uuid.uuid4()), user.external_user_id, FANTASY_LEAGUE_ID,
            f'{new_username}', meta={'discord_id': new_user_id}
        ) 
        await self.fantasy_handler.add_user(ctx, user, team, new_user_id)

    @commands.command()
    async def players(self, ctx):
        """Print out available players to pick from.

        If called from the draft channel, shows only unpicked players left.
        """
        printy = ""
        if is_draft_channel(ctx.channel):
            draft_id = self.fantasy_handler.channel_ids_to_draft_ids.get(ctx.channel.id)
            # @WEAK this will fail if bot restarts mid draft
            already_picked = self.fantasy_handler.draft_players_picked[draft_id]
            for team in self.player_handler.teams_and_players:
                players_left = [tp for tp in team["players"] if tp["player"]["player_id"] not in already_picked]
                if players_left:
                    printy += f'**{team["names"][0]["name"]}**:  {", ".join(p["player"]["names"][0]["name"] for p in players_left)}\n\n'
        else:
            for team in self.player_handler.teams_and_players:
                # print(team)
                logger.error(pformat(team))
                printy += f'**{team["names"][0]["name"]}**:  {", ".join(p["player"]["names"][0]["name"] for p in team["players"])}\n\n'
        await ctx.send(printy)

    # @commands.group()
    # async def draft(self, ctx):
    #     """Commands to use in a draft"""
    #     if ctx.invoked_subcommand is None:
    #         # just print the info
    #         await self.info(ctx)
    
    @commands.command()
    async def info(self, ctx):
        """Shows draft ordering and deadlines for picking"""
        draft_id = self.fantasy_handler.channel_ids_to_draft_ids.get(ctx.channel.id)
        if draft_id is None:
            return await ctx.send(f'Please use `!pick` command in your draft channel')
        await ctx.send(self.fantasy_handler.future_draft_choices(draft_id, filter_first=False, limit=9))

    @commands.command()
    @commands.guild_only() # TODO make usable in draft channel. maybe make only visible their too?
    async def pick(self, ctx, player):
        """Make your pick"""
        # TODO
        try:
            player_id = self.player_handler.simplified_player_names_to_id[simplified_str(player)]
        except KeyError:
            return await ctx.send(f'Invalid pick {player}. `!players ` to see available picks')
        try:
            fantasy_team_id = self.fantasy_handler.get_user_team(ctx.author.id).fantasy_team_id
            draft_id = self.fantasy_handler.channel_ids_to_draft_ids.get(ctx.channel.id)
            if draft_id is None:
                return await ctx.send(f'Please use `!pick` command in your draft channel')
            try:
                await self.fantasy_handler.client.send_insert_draft_pick(DraftPick(player_id, fantasy_team_id, draft_id))
            except ApiException as e:
                logger.info("Invalid pick: ", exc_info=True)
                if 'NotFound' in str(e):  # so fucking hacky
                    await ctx.send(f'Not your turn {ctx.author.name}')
                    return await ctx.send(self.fantasy_handler.future_draft_choices(draft_id, filter_first=False))
                else:
                    return await ctx.send(f'Invalid pick. Select a different player. See !players')
            await ctx.send(f'{ctx.author.name} picked {player}')
            await ctx.send(self.fantasy_handler.future_draft_choices(draft_id))
        except Exception:
            logger.exception("Pick error: ")
            return await ctx.send(f'Something went horribly wrong!')

    @commands.command()
    @commands.dm_only()
    async def order(self, ctx, *args):
        """Preset draft preferences for if you miss draft, or a pick.
        I.e. **!draft order micke w33 s4 **
        """
        # Can do this if there is a particular reason for wanting csv
        # order(self, ctx, *, heros) will return heros as whatever is typed
        # after "order"
        # I now think space-separated is fine (was imaging sometimes pros had spaces in their names, but
        # a) they actually dont when checking wiki. b) even if they do can just say "dont use spaces")
        if len(args) > 0:
            player_names = args
            try:
                player_ids = [self.player_handler.simplified_player_names_to_id[simplified_str(n)] for n in player_names]
            except KeyError as e:
                # TOMAYBEDO return full player-typed name, not simplified.
                return await ctx.send(
                    f'Invalid player: {e}. `!players` to see available picks. '
                    f'I.e. `!draft order puppey fng zai micke`'
                )
            discord_id = ctx.author.id
            try:
                draft_queue = DraftQueue(self.fantasy_handler.get_user_team(discord_id).fantasy_team_id, player_ids)
            except KeyError:
                # TOMAYBEDO could auto join league on any interaction like this.
                return await ctx.send(
                    'You are not currently registered to this league. Please type join! in main channel'
                )
            try:
                await self.fantasy_handler.client.send_insert_draft_queues([draft_queue])
                return await ctx.send(f'Success!')
            except ApiException:
                await ctx.send(f'Something went horribly wrong. Please DM a mod to investigate')
        else:
            await ctx.send(f'Provide a space separated list. I.e. Ex. order! puppey fng zai micke')


    @commands.group()
    @commands.has_role("admin")
    async def admin(self, ctx):
        """Important admin stuff"""
        # Some admin commands. They all use same confirm flag. Pretty hack way, sue me...
        # TOMAYBEDO
        # - move confirm stuff into top level, store last command
        if ctx.invoked_subcommand is None:
            await ctx.send("Admin what?")

    @admin.command(name="draft")
    async def clear_draft_channels(self, ctx):
        """Delete finished draft channels

        TODO Only a temporary way to do things. Should handle better.
        """
        if not self.confirm_flag:
            await ctx.send("Are you sure? (type command again to confirm)")
            self.confirm_flag = True
            return
        logger.info(f'{ctx.author} tidied up the draft channels')
        for channel in ctx.guild.channels:
            if is_draft_channel(channel):
                await channel.delete()
        self.confirm_flag = False

    @admin.command(name="nuke")
    async def delete_fantasydota_channels(self, ctx):
        """Delete all channels"""
        if not self.confirm_flag:
            await ctx.send("Are you sure? (type command again to confirm)")
            self.confirm_flag = True
            return
        category = dget(ctx.guild.categories, name=CATEGORY_NAME)
        for channel in category.channels:
            await channel.delete()
        await category.delete()
        await ctx.send("Finished cleaning. Bery nice.")
        self.confirm_flag = False
    
def is_draft_channel(channel):
    """Why do I exist?"""
    return channel.name.startswith("draft")



def setup(bot):
    """
    :param bot:
    :return:
    """
    logger.info('cog setup')
    cog = FantasyDota(bot)
    bot.add_cog(cog)

def teardown(bot):
    logger.info('cog teardown')