import json
import hashlib

def hash_dict(data):
    canonical_str = json.dumps(data , sort_keys = True)

    return hashlib.sha256(canonical_str.encode()).hexdigest()
                          

if __name__ == "__main__":
    sample = {"name": "Raju", "skill": "plastering"}
    sample2 = {"skill":"plasterng", "name" : "raju"}
    print(hash_dict(sample2))