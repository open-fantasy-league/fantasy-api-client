# fantasy-api-client

Using backend notes:
Often need to provide own UUID unique ID's for entities, rather than server auto-generating these for you.
Havent written client-side update funcs yet (they're actually not needed much in fantasy, 
unless you fuck things up lol)
Havent written server-side "get" funcs, can just subcribe to all comps/leagues/etc and it'll return you
a full list of entities in db.
Havent written server-side remove funcs yet, just dont fuckup lol.
The dataclasses have some optional fields which seem weird to be optional,
this is because when you insert/send them, you have to specify that field, 
but when you get a published message about that entity, the field is missing
(Usually because it's an ID, where that ID has already been specified higher up the chain)

## TODO:

ThePianoDentist: i think checklist for having finished by monday morning is

@ThePianoDentist
- rules!
- help!
- scoring!

@everyone
- !draft order
- ~~!join~~

old stuff 

- ~~first get discord api keys/testing servers.~~
- tidy up clients (dataclasses might be better than named-tuples[type-safety, default-values, can use docstrings to document fields better])
- database
Need a simple db schema to store discord users, and map them to a UUID in the fantasy-league system

discord commands
- join league (public in a main channel)
- show leaderboard (public in a main channel)
- show my team (public in a main channel)
- pick X (public in a draft channel)
- set queue (private msg to discord bot)
- help! who to contact for more info, a sort of faq
- rules! lists how many players per team/per position
- scoring! ie 3 points assist, 4 points kill
- draft-info! show next drafters, and when user up next.


backend functionality
- auto-create discord channel for each draft (and add correct users to it?)
can the channel be locked from others getting in?

- dota result scraper (scrape results and update leaderboards)
- create-league script (basically the fake-data stuff but for a proper dota league)

[Initially we can just do raw python scripts. Later, want to say "hey you could run this in your discord server".
For this we probably want not just scripts but discord commands, that when done by an admin would let bot create-league/update-results
]

Extras if have the time:
- Daily leaderboard views/commands, as well as overall
- A Leaderboard view for that draft. i.e. if there's 32 players, and 8 players per draft,
!leaderboard-draft would show that leaderboard of 8 players

For now will have team == squad, no "benched players", so simplifies things.

## Discord bot

### Setup

- `cp default.env .env` and add bot token:
  - got to discord apps [page](https://discord.com/developers/applications)
  - *bot name* > settings > bot > copy token
- 
- profit

### Ideas

- Think the faq, rules, scoring stuff while we can leave commands for would be 
cool if bot creats read only channel(s) for them with the info
  - Could also do this for leaderboard. Have a read only channel that auto updates

### TODO

- discord api requirements
  - ~~create private channel~~
    - ~~create role~~
    - ~~add role to users~~
  - ~~destroy channel~~
  - ~~send pm~~
  - ~~receive pm~~ dont need to "recieve" pms so to speak. can use checks
  to decide which commands work in pms or in guild
- [format](https://stackoverflow.com/questions/45951224/how-to-remove-default-help-command-or-change-the-format-of-it-in-discord-py) default help message? 

### TOMAYBEDO

- Use nicks. Atm bot always uses `author.name` but if people have nick set might be confusing.
`author.nick` unforunately doesnt default to `name`, reutrns `None` if not set so cbf to deal with now.
- properly seperate handler async from bot async - [this](https://github.com/Rapptz/discord.py/blob/master/examples/background_task.py) might be releavnt (or relavant for something else anyway)
- use discord embeds for the info channels
- think of somethin gnicer than ascii tables for the leaderboards
- control what commands usable in which channels, eg. only draft related commands in draft channel (so help) not full of irrelavant stuff