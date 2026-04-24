# apps/delivery/ouaga_zones.py
# Quartiers de Ouagadougou — données statiques
# Utilisées pour la sélection du quartier dans l'app Flutter

QUARTIERS_OUAGADOUGOU = [
    # Arrondissement 1
    "Dapoya", "Kamsaoghin", "Koulouba", "Larlé", "Niogsin",
    "Paspanga", "Peuloghin", "Samandin", "Wemtenga", "Zogona",
    # Arrondissement 2
    "Bilbalogho", "Cissin", "Gounghin", "Karpala", "Nongr-Masson",
    "Secteur 15", "Secteur 16", "Secteur 17",
    # Arrondissement 3
    "Baskuy", "Kuinima", "Ouidi", "Pabre", "Secteur 22",
    # Arrondissement 4
    "Hamdalaye", "Kalgondin", "Kill", "Nagrin", "Secteur 27",
    "Secteur 28", "Secteur 29", "Secteur 30",
    # Arrondissement 5
    "Bendogo", "Boassa", "Kalga", "Nioko 1", "Nioko 2",
    "Secteur 47", "Secteur 48", "Secteur 49", "Secteur 50",
    # Zones populaires
    "Zone du Bois", "Tampouy", "Tanghin", "Pissy",
    "Wogodogo", "Bilanga-yaar", "Dassasgho", "Kombissiri",
    "Koubri", "Pabré", "Saaba", "Ziniaré",
]

# Tarif unique Ouagadougou (pas de zones — même tarif partout en ville)
OUAGA_DELIVERY_RATES = {
    "standard": {
        "label":       "Standard",
        "description": "Livraison le jour même (2-6h)",
        "fee":         1000,  # XOF
        "icon":        "local_shipping",
        "color":       "0xFF4CAF50",
    },
    "express": {
        "label":       "Express",
        "description": "Livraison en moins de 2h",
        "fee":         2000,  # XOF
        "icon":        "bolt",
        "color":       "0xFFFF9800",
    },
}