from dataclasses import dataclass
from typing import Dict, List, Optional

# Create classes to handle the different types of nodes in the ast


# Base data type for all ast classes. These parameters are available for all node types
@dataclass
class BaseNodeType:
    id_num: int
    node_type: str
    src: str


# Base class definition for nodes that have name fields
@dataclass
class BaseNodeName(BaseNodeType):
    name: str
    name_location: Optional[str] = None


# Base Class for TypeDescription data type
@dataclass
class TypeDescriptions:
    type_identifier: str
    type_string: str


# Base class definition for ParameterList node type
@dataclass
class ParameterListNode(BaseNodeType):
    parameters: list


# Base class definition for Literal Node types
@dataclass
class LiteralNode(BaseNodeType):
    hex_value: Optional[str] = None
    is_constant: bool
    is_lvalue: bool
    is_pure: bool
    kind: str
    lvalue_requested: bool
    type_descriptions: TypeDescriptions
    value: str


# Base Class for TypeName data type
@dataclass
class TypeName(BaseNodeType):
    name: str
    state_mutability: Optional[str] = None
    type_descriptions: TypeDescriptions


# Every ast starts with a source unit. Class defintion for all source unit node types
@dataclass
class SourceUnit(BaseNodeType):
    absolute_path: str
    exported_symbols: dict
    license_type: str
    nodes: list


# Class definiton for PragmaDirective node type
@dataclass
class PragmaDirectiveNode(BaseNodeType):
    literals: list


# ErrorDefinition node type class
@dataclass
class ErrorDefinitionNode(BaseNodeName):
    error_selector: str
    parameters: ParameterListNode


# Class properties for contract definition type nodes
@dataclass
class ContractDefinitionNode(BaseNodeName):
    abstract: bool
    base_contracts: list
    canonical_name: str
    contract_dependencies: list
    contract_kind: str
    fully_implemented: bool
    linearized_base_contracts: list
    nodes: list
    scope: int
    used_errors: list
    used_events: list


# class properties for Event type nodes
@dataclass
class EventDefinitionNode(BaseNodeName):
    anonymous: bool
    event_selector: str
    parameters: ParameterListNode


# Class properties for Variable Declaration type nodes
@dataclass
class VariableDeclarationNode(BaseNodeName):
    constant: bool
    function_selector: Optional[str] = None
    indexed: Optional[bool] = None
    mutability: str
    scope: int
    state_variable: bool
    storage_location: str
    type_descriptions: TypeDescriptions
    type_name: Optional[TypeName] = None
    value: Optional[LiteralNode] = None
