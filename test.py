from pprint import pprint
from dataclasses import make_dataclass

ast = {
    "absolutePath": "./contracts/CrowdFunding.sol",
    "exportedSymbols": {"CrowdFunding": [316], "Withdrawal": [3]},
    "id": 317,
    "license": "UNLICENSED",
    "nodeType": "SourceUnit",
    "nodes": [
        {
            "id": 1,
            "literals": ["solidity", "^", "0.8", ".9"],
            "nodeType": "PragmaDirective",
            "src": "39:23:0"
        },
        {
            "errorSelector": "70e44c6a",
            "id": 3,
            "name": "Withdrawal",
            "nameLocation": "70:10:0",
            "nodeType": "ErrorDefinition",
            "parameters": {
                "id": 2,
                "nodeType": "ParameterList",
                "parameters": [],
                "src": "80:2:0"
            },
            "src": "64:19:0"
        }
    ]
}

# def create_class()
# extract keys and values from ast
key_data = []
for key, value in ast.items():
    # get data type for each value
    key_data.append((key, type(value)))
pprint(key_data)

# # create a dataclass with each key and the value as the data type
class_name = f'{ast.get("nodeType")}Node'
new_class = make_dataclass(class_name, key_data)

obj = new_class(**ast)

pprint(obj)

print(obj.nodes)

# unpack dictionary into class
