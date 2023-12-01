
"""
    This module provides functions for generating SourceUnit objects from Solidity source code.

    Functions:
        from_standard_output_json(path: str) -> set:
            Generates SourceUnit objects from a standard output json file.

        from_standard_output(output_json: dict) -> set:
            Generates SourceUnit objects from a standard output json as a dict.

        from_ast(ast: dict) -> SourceUnit:
            Generates a SourceUnit object from the given AST. Dependencies are not set.
"""

import json
from pathlib import Path

from solidity_parser.dependencies import set_dependencies
from solidity_parser.nodes import node_class_factory


def from_standard_output_json(path):
    """
    Generates SourceUnit objects from a standard output json file.

    Arguments:
        path: path to the json file
    """

    output_json = json.load(Path(path).open())
    return from_standard_output(output_json)


def from_standard_output(output_json):
    """
    Generates SourceUnit objects from a standard output json as a dict.

    This function takes a dictionary of standard compiler output as input and generates SourceUnit objects from it.
    The output is a set of SourceUnit objects that represent the Solidity source code.

    Arguments:
        output_json (dict): A dictionary of standard compiler output.

    Returns:
        set: A set of SourceUnit objects that represent the Solidity source code.
    """

    source_nodes = [node_class_factory(v["ast"], None)
                    for v in output_json["sources"].values()]
    source_nodes = set_dependencies(source_nodes)
    return source_nodes


def from_ast(ast):
    """
    Generates a SourceUnit object from the given AST. Dependencies are not set.
    """

    return node_class_factory(ast, None)
