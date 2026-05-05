import json

class_names = [
    'rice leaf roller','rice leaf caterpillar','paddy stem maggot',
    'asiatic rice borer','yellow rice borer','rice gall midge',
    'rice water weevil','rice leafhopper','grain spreader thrips',
    'rice shell pest','grub','mole cricket','wireworm',
    'white margined moth','black cutworm','large cutworm',
    'yellow cutworm','red spider','corn borer','army worm',
    'aphids','Potosiabre vitarsis','peach borer','english grain aphid',
    'green bug','bird cherry-oataphid','wheat blossom midge',
    'penthaleus major','longlegged spider mite','wheat phloeothrips',
    'wheat sawfly','cerodonta denticornis','beet fly','flea beetle',
    'cabbage army worm','beet army worm','Beet spot flies','meadow moth',
    'beet weevil','sericaorient alismots chulsky','alfalfa weevil',
    'flax budworm','alfalfa plant bug','tarnished plant bug','Locustoidea',
    'lytta polita','legume blister beetle','blister beetle',
    'therioaphis maculata Buckton','odontothrips loti','Thrips',
    'alfalfa seed chalcid','Pieris canidia','Apolygus lucorum',
    'Sternochetus frigidus','Cicadellidae'
]

HIGH_CROP = [
    'rice leaf roller','rice leaf caterpillar','paddy stem maggot',
    'asiatic rice borer','yellow rice borer','army worm','aphids',
    'english grain aphid','corn borer','black cutworm','large cutworm',
    'yellow cutworm','cabbage army worm','beet army worm','Locustoidea',
    'rice water weevil','rice leafhopper','wheat sawfly','beet weevil',
    'alfalfa weevil','white margined moth','wireworm','grub'
]

HIGH_HUMAN  = ['lytta polita','blister beetle','legume blister beetle']
MED_HUMAN   = ['red spider','longlegged spider mite','Thrips','flea beetle']

CROP_MAP = {
    'rice leaf roller':      ['rice'],
    'rice leaf caterpillar': ['rice'],
    'paddy stem maggot':     ['rice','paddy'],
    'asiatic rice borer':    ['rice','sugarcane'],
    'yellow rice borer':     ['rice'],
    'rice gall midge':       ['rice'],
    'rice water weevil':     ['rice'],
    'rice leafhopper':       ['rice'],
    'grain spreader thrips': ['rice','wheat'],
    'rice shell pest':       ['rice'],
    'grub':                  ['sugarcane','maize','vegetables'],
    'mole cricket':          ['vegetables','turf','crops'],
    'wireworm':              ['potato','maize','wheat','vegetables'],
    'white margined moth':   ['rice','wheat'],
    'black cutworm':         ['maize','turf','vegetables'],
    'large cutworm':         ['maize','vegetables'],
    'yellow cutworm':        ['maize','vegetables'],
    'red spider':            ['fruit trees','vegetables','cotton'],
    'corn borer':            ['maize','sorghum'],
    'army worm':             ['maize','wheat','rice','pasture'],
    'aphids':                ['wheat','rice','vegetables','fruit trees'],
    'Potosiabre vitarsis':   ['various crops'],
    'peach borer':           ['peach','cherry','plum','apricot'],
    'english grain aphid':   ['wheat','barley','oats'],
    'green bug':             ['wheat','sorghum','barley'],
    'bird cherry-oataphid':  ['wheat','oats','barley'],
    'wheat blossom midge':   ['wheat'],
    'penthaleus major':      ['wheat','clover','legumes'],
    'longlegged spider mite':['vegetables','fruit trees','cotton'],
    'wheat phloeothrips':    ['wheat'],
    'wheat sawfly':          ['wheat','barley'],
    'cerodonta denticornis': ['wheat','barley'],
    'beet fly':              ['beet','spinach'],
    'flea beetle':           ['vegetables','canola','potato'],
    'cabbage army worm':     ['cabbage','vegetables'],
    'beet army worm':        ['beet','vegetables'],
    'Beet spot flies':       ['beet','spinach'],
    'meadow moth':           ['alfalfa','vegetables','beet'],
    'beet weevil':           ['beet','sugarbeet'],
    'sericaorient alismots chulsky': ['various crops'],
    'alfalfa weevil':        ['alfalfa'],
    'flax budworm':          ['flax','linseed'],
    'alfalfa plant bug':     ['alfalfa'],
    'tarnished plant bug':   ['alfalfa','strawberry','cotton'],
    'Locustoidea':           ['all crops - devastating'],
    'lytta polita':          ['alfalfa','legumes'],
    'legume blister beetle': ['legumes','beans','soybeans'],
    'blister beetle':        ['alfalfa','potatoes','tomatoes'],
    'therioaphis maculata Buckton': ['alfalfa','clover'],
    'odontothrips loti':     ['alfalfa','legumes'],
    'Thrips':                ['onion','cotton','vegetables'],
    'alfalfa seed chalcid':  ['alfalfa'],
    'Pieris canidia':        ['cabbage','broccoli','cauliflower'],
    'Apolygus lucorum':      ['cotton','vegetables'],
    'Sternochetus frigidus': ['mango'],
    'Cicadellidae':          ['rice','maize','legumes'],
}

db = {}
for name in class_names:
    label = name.strip()

    if name in HIGH_HUMAN:
        h_level, h_color, danger = 'Critical', '#FF0000', True
        r_level, r_color = 'High Risk', '#FF3333'
    elif name in MED_HUMAN:
        h_level, h_color, danger = 'Moderate', '#FFA500', True
        r_level, r_color = 'Caution', '#FFA500'
    else:
        h_level, h_color, danger = 'Low', '#33CC33', False
        r_level, r_color = 'Safe', '#33CC33'

    eco_loss = 'High' if name in HIGH_CROP else 'Medium'
    crops = CROP_MAP.get(name, ['various crops'])

    db[name] = {
        'common_name': label.title(),
        'scientific_name': 'See literature',
        'risk_level': r_level,
        'risk_color': r_color,
        'rarity': 'Common',
        'active_season': 'Year-round',
        'ecological_role': 'Agricultural pest',
        'fun_fact': f'{label.title()} is a key pest monitored in the IP102 benchmark dataset.',
        'crop_impact': {
            'affected_crops': crops,
            'damage_type': ['feeding damage', 'yield loss', 'crop contamination'],
            'economic_loss_level': eco_loss,
            'loss_description': f'{label.title()} causes significant damage to {", ".join(crops)}. Early detection is critical.',
            'recommendations': {
                'low': [
                    f'Monitor {label} activity weekly using sticky traps',
                    'Encourage natural predators in the field',
                    'Record sightings and track population trends'
                ],
                'medium': [
                    f'Apply neem oil spray every 5-7 days for {label}',
                    'Remove and destroy heavily infested plant material',
                    'Use row covers to prevent further spread',
                    'Inspect neighbouring fields for spread'
                ],
                'high': [
                    f'Apply targeted insecticide for {label} immediately',
                    'Contact your local agricultural extension officer',
                    'Consider crop rotation to break pest cycle',
                    'Document damage for insurance or government support',
                    'Isolate affected area to prevent spread'
                ]
            },
            'organic_control': ['Neem oil', 'Pyrethrin', 'Diatomaceous earth', 'Garlic spray'],
            'chemical_control': ['Cypermethrin', 'Malathion', 'Imidacloprid'],
            'biological_control': ['Parasitic wasps', 'Predatory beetles', 'Lacewings']
        },
        'human_hazard': {
            'is_dangerous_to_humans': danger,
            'hazard_level': h_level,
            'hazard_color': h_color,
            'venom': name in HIGH_HUMAN,
            'bites': name in MED_HUMAN,
            'disease_transmission': False,
            'diseases_transmitted': [],
            'allergy_risk': danger,
            'symptoms_on_contact': ['Skin irritation', 'Redness', 'Blistering'] if name in HIGH_HUMAN else ['Skin irritation'] if name in MED_HUMAN else ['None expected'],
            'first_aid': 'Seek emergency medical attention immediately. Do not touch affected area.' if name in HIGH_HUMAN else 'Wash affected area with soap and water. Apply antihistamine if needed.' if danger else 'No action needed. Wash hands after contact.',
            'medical_attention': name in HIGH_HUMAN,
            'medical_note': 'Blister beetles contain cantharidin — extremely toxic. Seek emergency care immediately.' if name in HIGH_HUMAN else '',
            'vulnerable_groups': ['Children', 'Elderly', 'People with allergies'] if danger else []
        },
        'precautions': f'Wear gloves when handling plants affected by {label}. Avoid direct contact.'
    }

with open('insects_db.json', 'w') as f:
    json.dump(db, f, indent=2)

print(f'Generated {len(db)} insect entries!')
print('insects_db.json saved to backend folder!')