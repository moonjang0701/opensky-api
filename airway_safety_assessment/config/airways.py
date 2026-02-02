"""
Airway Configuration Module
항공로 설정 모듈
"""

# Korean Airways Configuration
# 대한민국 항공로 설정

KOREAN_AIRWAYS = {
    'Y711': {
        'name': 'Y711',
        'description': 'Domestic airway route',
        'waypoints': [
            {'name': 'OLMEN', 'lat': 37.5, 'lon': 126.5},
            {'name': 'BULTI', 'lat': 36.5, 'lon': 127.5},
            {'name': 'GIKDO', 'lat': 35.5, 'lon': 128.5},
        ],
        'separation_nm': 160.0,
        'type': 'parallel',
        'active': True
    },
    'Y579': {
        'name': 'Y579',
        'description': 'Jeju-Busan route (Before duplication)',
        'waypoints': [
            {'name': 'MAKET', 'lat': 33.5, 'lon': 126.5},
            {'name': 'TOPAX', 'lat': 35.0, 'lon': 129.0},
        ],
        'separation_nm': 160.0,
        'type': 'single',
        'active': False,
        'notes': 'Replaced by Y571/Y572 duplication'
    },
    'Y571': {
        'name': 'Y571',
        'description': 'Jeju-Busan route (Busan direction)',
        'waypoints': [
            {'name': 'AKPON', 'lat': 33.5, 'lon': 126.5},
            {'name': 'ANROD', 'lat': 35.0, 'lon': 129.0},
        ],
        'separation_nm': 6.0,  # Separation from Y572
        'type': 'parallel',
        'active': True,
        'parallel_route': 'Y572'
    },
    'Y572': {
        'name': 'Y572',
        'description': 'Jeju-Busan route (Jeju direction)',
        'waypoints': [
            {'name': 'UPGOS', 'lat': 33.5, 'lon': 126.5},
            {'name': 'ENGOT', 'lat': 35.0, 'lon': 129.0},
        ],
        'separation_nm': 6.0,  # Separation from Y571
        'type': 'parallel',
        'active': True,
        'parallel_route': 'Y571'
    }
}


# Safety Assessment Parameters
SAFETY_PARAMETERS = {
    'TLS': 5e-9,  # Target Level of Safety (collisions per flight hour)
    'Pz_0': 0.538,  # Vertical overlap probability (JASMA/BOBASMA standard)
    'y_dot': 75.0,  # Cross-track speed (knots)
    'z_dot': 1.5,   # Vertical speed (knots)
    'Sx': 80.0,     # Half of longitudinal separation (nm)
}


# Distribution Models for Lateral Deviation Fitting
DISTRIBUTION_MODELS = [
    'DE',   # Double Exponential (Laplace)
    'N',    # Gaussian (Normal)
    'NN',   # Mixture of Gaussians
    'DDE',  # Mixture of Double Exponentials
    'NDE'   # Mixture of Gaussian and Double Exponential
]


def get_airway_config(airway_name: str) -> dict:
    """
    Get configuration for specific airway
    
    Checks custom_airways.json first, then falls back to built-in config
    
    Parameters:
    -----------
    airway_name : str
        Name of the airway (e.g., 'Y711', 'Y571')
    
    Returns:
    --------
    dict : Airway configuration
    """
    import json
    import os
    
    # Try loading custom airways first
    custom_path = os.path.join(os.path.dirname(__file__), 'custom_airways.json')
    if os.path.exists(custom_path):
        try:
            with open(custom_path, 'r', encoding='utf-8') as f:
                custom_airways = json.load(f)
                if airway_name in custom_airways:
                    return custom_airways[airway_name]
        except Exception:
            pass
    
    # Fall back to built-in config
    return KOREAN_AIRWAYS.get(airway_name, {})


def list_available_airways() -> list:
    """
    Get list of available airways
    
    Returns:
    --------
    list : List of airway names
    """
    return list(KOREAN_AIRWAYS.keys())


def get_active_airways() -> list:
    """
    Get list of active airways
    
    Returns:
    --------
    list : List of active airway names
    """
    return [name for name, config in KOREAN_AIRWAYS.items() if config.get('active', False)]
