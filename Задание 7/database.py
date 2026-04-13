from typing import Dict, List

fake_users_db: Dict[str, dict] = {}
resources_db: List[dict] = []

class Counter:
    def __init__(self):
        self.value = 1
    
    def get_and_increment(self):
        current = self.value
        self.value += 1
        return current

resource_id_counter = Counter()