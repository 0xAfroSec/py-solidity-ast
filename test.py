from pprint import pprint
from dataclasses import make_dataclass, dataclass

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


def create_nodes(node_list):
    # nodes = []
    # for i in node_list:
    key_data = []
    for key, value in node_list.items():
        # get data type for each value
        key_data.append((key, type(value)))

    # Create class_name from Node Type
    node_name = f'{node_list.get("nodeType", "no_node_type")}Node'
    # create a dataclass with each key and the value as the data type
    new_node = make_dataclass(node_name, key_data)

    # nodes.append(new_node)
    return new_node


'''
Given a dictionary as input, Dynamically creates a data class object with the keys as attributes and the values as data type for the attributes. Returns a data class object.
and
'''


def create_class(ast_dict):
    # extract keys and values from dictionary
    key_data = []
    for key, value in ast.items():
        # get data type for each value
        key_data.append((key, type(value)))

    # Create class_name from Node Type
    class_name = f'{ast.get("nodeType", "no_node_type")}Node'
    # create a dataclass with each key and the value as the data type
    new_class = make_dataclass(class_name, key_data)

    # if new_class.nodes != []:
    #     nodes = create_nodes(new_class.nodes)

    # Method to return node type
    def node_type(self):
        print(f"The Node Type is: {self.nodeType}")
        return self.nodeType

    # add node_type method to new class instance
    new_class.node_type = node_type

    return new_class  # nodes


# @dataclass
# class AstClass:
#     SourceUnit: create_class(ast)

# unit2 = AstClass(ast)
# print(unit2)


# create a new class object
unit = create_class(ast)
# create new class instance
sourceunit = unit(**ast)
if sourceunit.nodes:
    for node in sourceunit.nodes:
        nodes = create_nodes(node)
        node_class = nodes(**node)
        pprint(node_class)
# print(sourceunit.node_type())
