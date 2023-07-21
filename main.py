from dataclasses import dataclass
from typing import Dict, List, Optional

# Create classes to handle the different types of nodes in the ast


@dataclass
class BaseNode:
    name: str
    name_location: Optional[str] = None
    node_type: str
    src: str


# top level class, every ast starts with a source unit
@dataclass
class SourceUnit:
    absolute_path: str
    exported_symbols: dict
    id_num: int
    license_type: str
    node_type: str
    nodes: list
    src: str


# pragma directive class for source unit
@dataclass
class PragmaDirectiveNode:
    id_num: int
    literals: list
    node_type: str
    src: str


# error definition class for source unit
@dataclass
class ErrorDefinitionNode(BaseNode):
    error_selector: str
    id_num: int
    parameters: dict


@dataclass
class ContractDefinitionNode(BaseNode):
    abstract: bool
    base_contracts: list
    canonical_name: str
    contract_dependencies: list
    contract_kind: str
    fully_implemented: bool
    id_num: int
    linearized_base_contracts: list
    nodes: list
    scope: int
    used_errors: list
    used_events: list


@dataclass
class VariableDeclarationNode:
    constant: bool
    id_num: int
    mutability: str
