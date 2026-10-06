extends RefCounted
## Emoji packs: the shop sells characters and emoji packs, no items.
## In Matematik Savaşı players throw their equipped emojis at each other.
## A pack holds exactly TAUNT_SLOTS emojis, one per taunt button.

const TAUNT_SLOTS := 3
const FREE_PACK := "temel"

# price is in in-game coins; 0 = everyone owns it.
const PACKS := [
	{"id": "temel", "name": "Temel", "price": 0, "emojis": ["😎", "😂", "👍"]},
	{"id": "atesli", "name": "Ateşli", "price": 200, "emojis": ["🔥", "💪", "🏆"]},
	{"id": "alayci", "name": "Alaycı", "price": 300, "emojis": ["🤣", "🐢", "💤"]},
	{"id": "dahi", "name": "Dahi", "price": 400, "emojis": ["🧠", "🤓", "⚡"]},
	{"id": "dostane", "name": "Dostane", "price": 150, "emojis": ["🤝", "👏", "❤️"]},
]


static func find(pack_id: String) -> Dictionary:
	for pack in PACKS:
		if pack["id"] == pack_id:
			return pack
	return {}


## Emojis for a player's taunt buttons. Unknown packs fall back to the free one.
static func loadout(pack_id: String) -> Array:
	var pack := find(pack_id)
	if pack.is_empty():
		pack = find(FREE_PACK)
	return pack["emojis"]
