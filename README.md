# fantasy-api-client

Using backend notes:
Often need to provide own UUID unique ID's for entities, rather than server auto-generating these for you.
Havent written client-side update funcs yet (they're actually not needed much in fantasy, 
unless you fuck things up lol)
Havent written server-side "get" funcs, can just subcribe to all comps/leagues/etc and it'll return you
a full list of entities in db.
Havent written server-side remove funcs yet, just dont fuckup lol.

TODO:
- first get discord api keys/testing servers.
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