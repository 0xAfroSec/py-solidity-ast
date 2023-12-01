# Py-Solidity-AST

A Python library for parsing and working with the Abstract Syntax Tree (AST) output of the [Solc](https://github.com/ethereum/solidity) compiler or any compiled solidity files.

## Table of Contents

- [Py-Solidity-AST](#py-solidity-ast)
  - [Table of Contents](#table-of-contents)
  - [Features 🧑‍💻](#features-)
  - [Installation 🛠️](#installation-️)
  - [Usage 💻](#usage-)
    - [Interacting with Nodes 🌐](#interacting-with-nodes-)
      - [Code Selection Documentation](#code-selection-documentation)
    - [Exploring the Tree 📊](#exploring-the-tree-)
    - [Interacting with Nodes and Source Code 📝](#interacting-with-nodes-and-source-code-)
  - [Contributing Guidelines 🤝](#contributing-guidelines-)
  - [Credits](#credits)
  - [License](#license)

## Features 🧑‍💻

- [x] Parse Solidity AST JSON output
- [x] Filter and search through nodes
- [x] Find parents, children and siblings of nodes
- [x] Fetch line numbers of nodes from source code
- [x] Generate code snippets from nodes

## Installation 🛠️

You can install the latest release via `pip`:

```bash
$ pip install py-solidity-ast
```

## Usage 💻

First, use [py-solc-x](https://github.com/iamdefinitelyahuman/py-solc-x) to compile your contracts to the [standard JSON output format](https://solidity.readthedocs.io/en/latest/using-the-compiler.html#output-description).

```python
import json
import solcx
input_json = json.load(open('input.json'))
output_json = solcx.compile_standard(input_json)
```

Next, import `py-solidity-ast` and initialize using `from_standard_output_json` or `from_standard_output`. This returns a list of `SourceUnit` objects, which each represent the base AST node in a Solidity source file.

```python
import py-solidity-ast

nodes = py-solidity-ast.from_standard_output(output_json)

nodes
#output: [<SourceUnit iterable 'contracts/Token.sol'>, <SourceUnit iterable 'contracts/SafeMath.sol'>]
```

You can also generate a single `SourceUnit` directly from that source's AST:

```python
import py-solidity-ast

node = py-solidity-ast.from_ast(output_json["sources"]["contracts/Token.sol"]["ast"])

node
# output: <SourceUnit iterable 'contracts/Token.sol'>
```

### Interacting with Nodes 🌐

Each node has the following attributes:

```python
node
# the current node is a FunctinoDefinition node with the name 'mul'
# output: <FunctionDefinition iterable 'mul'>

node.name
# output: "mul"

node.depth  # Number of nodes between this node and the SourceUnit
# output: 2

node.src  # The 'src' information of the node "start:length:1"
# output: "4948:1477:1"

node.contract_id  # Contract ID as given by the standard compiler JSON
# output: 2

node.fields  # List of fields for this node
['baseNodeType', 'documentation', 'id', 'implemented', 'kind', 'modifiers', 'name', 'nodeType', 'nodes', 'parameters', 'returnParameters', 'scope', 'src', 'stateMutability', 'superFunction', 'visibility']

```

Fields mostly follow the expected [AST grammar](https://docs.soliditylang.org/en/latest/grammar.html). One notable difference: `Block` nodes are omitted and the body of each `Block` is available within it's parent as the attribute `nodes`. Nodes containing a body are iterable and can be accessed with list-like syntax. Additionally, any child node with a `name` field is accessible using dict-like syntax.

The following additional fields are also available:

- Most nodes have a `baseNodeType` field as defined in [grammar.py](py-solidity-ast/grammar.py)
- `ContractDefinition` nodes have `dependencies` and `libraries` fields that point to related `ContractDefinition` nodes

Some Examples:

#### Code Selection Documentation

The code selection below demonstrates the use of the `py-solidity-ast` tool to extract information from a Solidity source code file.

The `source_node` variable represents the root node of the Solidity AST (Abstract Syntax Tree) for the source code file.

The `nodes` attribute of the `source_node` variable contains a list of all the nodes in the AST. In this case, it contains a `PragmaDirective` node and a `ContractDefinition` node.

The `source_node[1]` and `source_node['SafeMath']` expressions both retrieve the `ContractDefinition` node for the `SafeMath` contract.

The `nodes` attribute of the `source_node['SafeMath']` variable contains a list of all the nodes in the `SafeMath` contract. In this case, it contains five `FunctionDefinition` nodes.

The `source_node['SafeMath']['mul']` expression retrieves the `FunctionDefinition` node for the `mul` function in the `SafeMath` contract.

The `nodes` attribute of the `source_node['SafeMath']['mul']` variable contains a list of all the nodes in the `mul` function. In this case, it contains an `IfStatement` node, a `VariableDeclarationStatement` node, a `FunctionCall` node, and a `Return` node.

```python

source_node
# output: <SourceUnit iterable 'contracts/math/SafeMath.sol'>

source_node.nodes
# output: [<PragmaDirective object>, <ContractDefinition iterable 'SafeMath'>]

source_node[1]
# output: <ContractDefinition iterable 'SafeMath'>

source_node['SafeMath']
# output: <ContractDefinition iterable 'SafeMath'>

source_node['SafeMath'].fields
['baseContracts', 'children', 'contractDependencies', 'contractKind', 'contract_id', 'dependencies', 'depth', 'documentation', 'fullyImplemented', 'id', 'is_child_of', 'is_parent_of', 'keys', 'libraries', 'linearizedBaseContracts', 'name', 'nodeType', 'nodes', 'offset', 'parent', 'parents', 'scope', 'src']

source_node['SafeMath'].nodes
[<FunctionDefinition iterable 'add'>, <FunctionDefinition iterable 'sub'>, <FunctionDefinition iterable 'mul'>, # output: <FunctionDefinition iterable 'div'>, <FunctionDefinition iterable 'mod'>]

source_node['SafeMath']['mul']
# output: # output: <FunctionDefinition iterable 'mul'>

source_node['SafeMath']['mul']
# output: [<IfStatement object>, <VariableDeclarationStatement object>, <FunctionCall object>, <Return object>]
```

### Exploring the Tree 📊

The `Node.children()` method is used to search and filter through child nodes of a given node. It takes any of the following keyword arguments:

- `depth`: Number of levels of children to traverse. `0` returns only this node.
- `include_self`: Includes this node in the results.
- `include_parents`: Includes nodes that match in the results, when they also have child nodes that match.
- `include_children`: If True, as soon as a match is found it's children will not be included in the search.
- `required_offset`: Only match nodes with a source offset that contains this offset.
- `offset_limits`: Only match nodes when their source offset is contained inside this source offset.
- `filters`: Dictionary of `{'attribute': "value"}` that children must match. Can also be given as a list of dicts, children that match any of the dicts will be returned.
- `exclude_filter`: Dictionary of `{'attribute': "value"}` that children cannot match.

```python
node = s['Token']['transfer']
node.children(
    include_children=False,
    filters={'nodeType': "FunctionCall", "expression.name": "require"}
)
# output: [<FunctionCall>]
```

`Node.parent()` and `Node.parents()` are used to travel back up the tree. They take the following arguments:

- `depth`: Depth limit. If given as a negative value, it will be subtracted from this object's depth.
- `filters`: Dictionary of `{'attribute': "value"}` that parents must match.

`Node.parent()` returns one result, `Node.parents()` returns a list of matches.

```python
node.parents()
# output: [<ContractDefinition iterable 'Token'>, <SourceUnit iterable object 'contracts/Token.sol'>]
```

The `Node.find_node()` and `Node.find_nodes()` methods are used to search the tree for a node with desired attributes that has parent and children nodes that match the given filters. They take the following arguments:

- `node_filters`: Dictionary of `{'attribute': "value"}` that the node must match. Can also be a list of dicts, the node must match any of the dicts.
- `parent_filters`: Dictionary of `{'attribute': "value"}` that the node's parents must match. Can also be a list of dicts, the node's parents must match any of the dicts.
- `child_filters`: Dictionary of `{'attribute': "value"}` that the node's children must match. Can also be a list of dicts, the node's children must match any of the dicts.
- `node_depth`: Depth limit for the node. If given as a negative value, it will be subtracted from this object's depth.
- `parent_depth`: Depth limit for the node's parents. If given as a negative value, it will be subtracted from this object's depth.
- `child_depth`: Depth limit for the node's children. If given as a negative value, it will be subtracted from this object's depth.

`find_node()` returns a `True` and a tuple of the node, its parent and its child; returns `False` and None if no match. `find_nodes()` returns the same as `find_node()`, but returns a list of all matches.

```python
node.find_node(
    node_filters={'nodeType': "Identifier","name": "require"},
    parent_filters={'kind': "FunctionCall"},
    child_filters={'typeString': "BinaryOperation", "operator": "!="},
    node_depth=1,
    parent_depth=-1,
    child_depth=1
)
# output: False, (None, None, None)
```

The `child_has_attributes()` and `children_have_attributes` methods are used to check if a node has a child or children with the given attributes.

```python
node.child_has_attributes({'nodeType': "Identifier", "expression.name": "require"})

# output: True, <Identifier object 'require'>
```

`parent_has_attributes()` and `parents_have_attributes()` function the same way as `child_has_attributes()`and`children_have_attributes()`, but search up the tree instead of down.

### Interacting with Nodes and Source Code 📝

The AST parser can also generate code snippets from the AST using the source code of the contract.
`Node.extract_code()` returns a string of the code at the node's src location. It takes the following arguments:

- `source_code`: The source code of the contract
- `loc`: If True, the code will be returned with line numbers. If False, the code will be returned without line numbers. Defaults to True.
- `tags`: If True, the code will be returned with tags like '//@audit' and '//@info' that can be used to annotate the code. If False, the code will be returned without tags. Defaults to True.

```python
contract_node = from_ast(file['ast'])

contract_node
# output: <SourceUnit iterable 'contracts/Token.sol'>

success, child = contract_node.child_has_attributes({'nodeType': "Identifier", "expression.name": "require"})
# output: success = True, child = <Identifier object 'require'>

child.extract_code(source_code, loc=True)
# output: 99: require(success, "RdpxReserve: transfer failed");
```

Lastly, you can fetch the line numbers of a node using the `Node.get_line_numbers()` . It returns the start and end lines of the node as a tuple.

## Contributing Guidelines 🤝

We welcome contributions to this project! To contribute, please follow these guidelines:

1. Fork the repository and create a new branch for your contribution.
2. Make your changes and ensure that tthey are working properly.
3. Submit a pull request with a clear description of your changes and why they are needed.
4. Your pull request will be reviewed by the maintainers, who may request changes or ask for additional information.
5. Once your pull request is approved, it will be merged into the main branch.

If you have any questions or need help with your contribution, please don't hesitate to reach out to us by opening an issue or contacting one of the maintainers directly.

## Credits

Big thank you to [iamdefinitelyahuman](https://github.com/iamdefinitelyahuman) for creating [py-solc-ast](https://github.com/iamdefinitelyahuman/py-solc-ast), which this project is based on.

## License

This project is licensed under the [MIT license](LICENSE).
