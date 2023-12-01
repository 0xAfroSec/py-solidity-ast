#!/usr/bin/python3
"""
This module provides classes for representing nodes within the Solidity Abstract Syntax Tree (AST). 
It also provides methods for traversing nodes and finding parent and child nodes with desired attributes.
Additionally, it provides methods for extracting source code from the AST using 'src' information 
"""

import functools
from copy import deepcopy
from typing import Union, Tuple
from solidity_parser.grammar import BASE_NODE_TYPES


class NodeBase:
    """
    Represents a node within the Solidity Abstract Syntax Tree (AST).

    Attributes:
        depth (int): Number of nodes between this node and the SourceUnit.
        offset (tuple): Absolute source offsets as a (start, stop) tuple.
        contract_id (int): Contract ID as given by the standard compiler JSON.
        fields (list): List of attributes for this node.
    """

    def __init__(self, ast, parent):
        """
            Initializes a NodeBase instance.

            Args:
                ast (dict): The AST node.
                parent (NodeBase): The parent node, or None if this is the root.
        """
        self.depth = parent.depth + 1 if parent is not None else 0
        self._parent = parent
        self._children = set()
        src = [int(i) for i in ast["src"].split(":")]
        self.offset = (src[0], src[0] + src[1])
        self.contract_id = src[2]
        self.fields = sorted(ast.keys())

        for key, value in ast.items():
            if isinstance(value, dict) and value.get("nodeType") == "Block":
                value = value["statements"]
            elif key == "body" and not value:
                value = []
            if isinstance(value, dict):
                item = node_class_factory(value, self)
                if isinstance(item, NodeBase):
                    self._children.add(item)
                setattr(self, key, item)
            elif isinstance(value, list):
                items = [node_class_factory(i, self) for i in value]
                setattr(self, key, items)
                self._children.update(
                    i for i in items if isinstance(i, NodeBase))
            else:
                setattr(self, key, value)

    def __hash__(self):
        """
        Computes the hash value of the node.

        Returns:
            int: Hash value.
        """
        return hash(f"{self.nodeType}{self.depth}{self.offset}")

    def __repr__(self):
        """
        Returns a string representation of the node.

        Returns:
            str: String representation of the node.
        """
        repr_str = f"<{self.nodeType}"
        if hasattr(self, "nodes"):
            repr_str += " iterable"
        if hasattr(self, "type"):
            if isinstance(self.type, str):
                repr_str += f" {self.type}"
            else:
                repr_str += f" {self.type._display()}"
        if self._display():
            repr_str += f" '{self._display()}'"
        else:
            repr_str += " object"
        return f"{repr_str}>"

    def _display(self):
        """
        Get a string representation for display purposes.

        Returns:
            str: String representation for display.
        """
        if hasattr(self, "name") and hasattr(self, "value"):
            return f"{self.name} = {self.value}"
        for attr in ("name", "value", "absolutePath"):
            if hasattr(self, attr):
                return f"{getattr(self, attr)}"
        return ""

    def children(
        self,
        depth=None,
        include_self=False,
        include_parents=True,
        include_children=True,
        required_offset=None,
        offset_limits=None,
        filters=None,
        exclude_filter=None,
    ):
        """Get childen nodes of this node.

        Arguments:
          depth: Number of levels of children to traverse. 0 returns only this node.
          include_self: Includes this node in the results.
          include_parents: Includes nodes that match in the results, when they also have
                        child nodes that match.
          include_children: If True, as soon as a match is found it's children will not
                            be included in the search.
          required_offset: Only match nodes with a source offset that contains this offset.
          offset_limits: Only match nodes when their source offset is contained inside
                           this source offset.
          filters: Dictionary of {attribute: value} that children must match. Can also
                   be given as a list of dicts, children that match one of the dicts
                   will be returned.
          exclude_filter: Dictionary of {attribute:value} that children cannot match.

        Returns:
            List of node objects."""
        if filters is None:
            filters = {}
        if exclude_filter is None:
            exclude_filter = {}
        if isinstance(filters, dict):
            filters = [filters]
        filter_fn = functools.partial(
            _check_filters, required_offset, offset_limits, filters, exclude_filter
        )
        find_fn = functools.partial(
            _find_children, filter_fn, include_parents, include_children)
        result = find_fn(find_fn, depth, self)
        if include_self or not result or result[0] != self:
            return result
        return result[1:]

    def parents(self, depth=-1, filters=None):
        """Get parent nodes of this node.

        Arguments:
            depth: Depth limit. If given as a negative value, it will be subtracted
                   from this object's depth.
            filters: Dictionary of {attribute: value} that parents must match.

        Returns: list of nodes"""
        if filters and not isinstance(filters, dict):
            raise TypeError("Filters must be a dict")
        if depth < 0:
            depth = self.depth + depth
        if depth >= self.depth or depth < 0:
            raise IndexError("Given depth exceeds node depth")
        node_list = []
        parent = self
        while True:
            parent = parent._parent
            if not filters or _check_filter(parent, filters, {}):
                node_list.append(parent)
            if parent.depth == depth:
                return node_list

    def parent(self, depth=-1, filters=None):
        """Get a parent node of this node.

        Arguments:
            depth: Depth limit. If given as a negative value, it will be subtracted
                   from this object's depth. The parent at this exact depth is returned.
            filters: Dictionary of {attribute: value} that the parent must match.

        If a filter value is given, will return the first parent that meets the filters
        up to the given depth. If none is found, returns None.

        If no filter is given, returns the parent at the given depth."""
        if filters and not isinstance(filters, dict):
            raise TypeError("Filters must be a dict")
        if depth < 0:
            depth = self.depth + depth
        if depth >= self.depth or depth < 0:
            raise IndexError("Given depth exceeds node depth")
        parent = self
        while parent.depth > depth:
            parent = parent._parent
            if parent.depth == depth and not filters:
                return parent
            if filters and _check_filter(parent, filters, {}):
                return parent
        return None

    def is_child_of(self, node):
        """Checks if this object is a child of the given node object."""
        if node.depth >= self.depth:
            return False
        return self.parent(node.depth) == node

    def is_parent_of(self, node):
        """Checks if this object is a parent of the given node object."""
        if node.depth <= self.depth:
            return False
        return node.parent(self.depth) == self

    def get(self, key, default=None):
        """
        Gets an attribute from this node, if that attribute exists.

        Arguments:
            key: Field name to return. May contain decimals to return a value
                 from a child node.
            default: Default value to return.

        Returns: Field value if it exists. Default value if not.
        """
        if key is None:
            raise TypeError("Cannot match against None")
        obj = self
        for k in key.split("."):
            if isinstance(obj, dict):
                obj = obj.get(k)
            else:
                obj = getattr(obj, k, None)
        return obj or default

    # checks if node has parents with a specific attribute

    def parent_has_attributes(self, filters, depth=-1):
        """
        Check if the parent node has the specified attributes.

        Args:
            filters (dict or list): A dictionary or list of dictionaries containing the attributes to check for.
            depth (int, optional): The maximum depth to search for the parent node. Defaults to -1 (unlimited depth).

        Returns:
            tuple: A tuple containing a boolean indicating whether the parent node has the attributes, and the parent node itself.
        Raises:
            ValueError: If filters is not a dictionary or list.
        """
        parent = None
        # if filters is a list, iterate over each filter and check if the parent node has the attribute
        if isinstance(filters, list):
            for filter in filters:
                parent = self.parent(depth=depth, filters=filter)
                # if a parent node is found with the attribute, return True and the parent node
                if parent:
                    return True, parent
        # if filters is a dictionary, check if the parent node has all the attributes in the dictionary
        elif isinstance(filters, dict):
            parent = self.parent(depth=depth, filters=filters)
            # if a parent node is found with all the attributes, return True and the parent node
            if parent:
                return True, parent
        # if filters is not a list or dictionary, raise a ValueError
        else:
            raise ValueError("filters must be either a dict or list")
        # if no parent node is found with the attributes, return False and None
        return False, parent

    # checks if node has parents with specific attributes and returns a list of the matching parent nodes

    def parents_have_attributes(self, filters, depth=-1):
        """
        Check if the parent node has the specified attributes.

        Args:
            filters (dict or list): A dictionary or list of dictionaries containing the attributes to check for.
            depth (int, optional): The maximum depth to search for the parent node. Defaults to -1 (unlimited depth).

        Returns:
            tuple: A tuple containing a boolean indicating whether the parent nodes have the attributes, and a list of the parent nodes.
        Raises:
            ValueError: If filters is not a dictionary or list.
        """
        parents = []
        # if filters is a list, iterate over each filter and check if the parent node has the attribute
        if isinstance(filters, list):
            for filter in filters:
                parent = self.parent(depth=depth, filters=filter)
                # if a parent node is found with the attribute, add it to the list of parents
                if parent:
                    parents.append(parent)
        # if filters is a dictionary, check if the parent node has all the attributes in the dictionary
        elif isinstance(filters, dict):
            parent = self.parent(depth=depth, filters=filters)
            # if a parent node is found with all the attributes, add it to the list of parents
            if parent:
                parents.append(parent)
        # if filters is not a list or dictionary, raise a ValueError
        else:
            raise ValueError("filters must be either a dict or list")
        # if at least one parent node is found with the attributes, return True and the list of parent nodes
        if parents:
            return True, parents
        # if no parent node is found with the attributes, return False and an empty list
        else:
            return False, parents

    # checks if the current node has a child with the given filters and returns the child node if it exists

    def child_has_attributes(self, filters, depth=1):
        """
        Check if a child node exists with the given filters and depth.

        Args:
            filters (dict): A dictionary of filters to apply to the child nodes.
            depth (int): The depth to search for child nodes.

        Returns:
            tuple: A tuple containing a boolean indicating if a child node exists with the given filters,
            and the child node itself if it exists, otherwise None.
        """
        # initialize child to None
        child = None
        # get the children of the current node with the given filters and depth
        child = self.children(
            depth=depth, include_children=False, filters=filters)
        # if a child node exists with the given filters, return True and the child node
        if child:
            return True, child[0]
        # otherwise, return False and None
        else:
            return False, child

    # checks if the current node has children with the given filters and returns a list of the matching child nodes

    def children_have_attributes(self, filters, depth=1):
        """
        Check if a child node exists with the given filters and depth.

        Args:
            filters (dict): A dictionary of filters to apply to the child nodes.
            depth (int): The depth to search for child nodes.

        Returns:
            tuple: A tuple containing a boolean indicating if a child node exists with the given filters,
            and a list of the child nodes themselves if they exist, otherwise an empty list.
        """
        # initialize children to an empty list
        children = []
        # get the children of the current node with the given filters and depth
        children = self.children(
            depth=depth, include_children=False, filters=filters)
        # if at least one child node exists with the given filters, return True and the list of child nodes
        if children:
            return True, children
        # otherwise, return False and an empty list
        else:
            return False, children

    # checks if the current node has parents and children nodes with the given filters

    def parent_child_has_attributes(self, parent_filters, child_filters, parent_depth=-1, child_depth=1):
        """
        Check if the current node has a parent and child with the given filters.

        Args:
            parent_filters (dict): A dictionary of filters to apply to the parent node.
            child_filters (dict): A dictionary of filters to apply to the child node.
            parent_depth (int): The depth to search for the parent node. Defaults to -1 (unlimited depth).
            child_depth (int): The depth to search for the child node. Defaults to 1.

        Returns:
            tuple: A tuple containing a boolean indicating whether both parent and child nodes exist with the given filters,
            and a tuple of the parent and child nodes (or None values if either node does not exist).
        """
        # check if the current node has a parent with the given filters
        parent_success, parent = self.parent_has_attributes(
            parent_filters, depth=parent_depth)
        # check if the current node has a child with the given filters
        child_success, child = self.child_has_attributes(
            child_filters, depth=child_depth)

        # if both parent and child nodes exist with the given filters, return True and a tuple of the parent and child nodes
        if parent_success and child_success:
            return True, (parent, child)
        # otherwise, return False and a tuple of None values
        else:
            return False, (None, None)

    # Finds a child node with a parent node that matches the given filters.

    def find_child_with_parent(self, child_filters, parent_filters, parent_depth=-1, child_depth=1):
        """
        Args:
            child_filters (list or dict): Filters to apply to child nodes.
            parent_filters (list or dict): Filters to apply to parent nodes.
            parent_depth (int): Maximum depth to search for parent nodes.
            child_depth (int): Maximum depth to search for child nodes.

        Returns:
            Tuple[bool, Optional[NodeBase], Optional[NodeBase]]: A tuple containing a boolean indicating whether a
            matching child node was found, the matching child node (if found), and the matching parent node (if found).
        """
        children = self.children(
            filters=child_filters)  # get all children nodes that match the given filters
        for child in children:
            # check if the parent node of the child node matches the given filters
            success, parent = child.parent_has_attributes(
                filters=parent_filters, depth=parent_depth)
            if success:
                # return the child node and the parent node if a match is found
                return True, child, parent

        # return False and None for both child and parent nodes if no match is found
        return False, None, None

    # Finds a node that matches the given filters.

    def find_node(self, node_filters, parent_filters, child_filters, node_depth=1, parent_depth=-1, child_depth=1):
        """
        Args:
            node_filters (dict): A dictionary of filters to apply to the node.
            parent_filters (dict): A dictionary of filters to apply to the parent node.
            child_filters (dict): A dictionary of filters to apply to the child node.
            node_depth (int): The depth to search for the node.
            parent_depth (int): The depth to search for the parent node.
            child_depth (int): The depth to search for the child node.

        Returns:
            A tuple containing a boolean indicating whether a matching node was found, and the matching node, parent and child nodes.
        """
        # get the desired nodes based on the node filters and depth
        desired_nodes = self.children(filters=node_filters, depth=node_depth)

        # check if the desired node has the specified parent and child nodes with the specified filters and depths
        for desired_node in desired_nodes:
            success, (parent, child) = desired_node.parent_child_has_attributes(
                parent_filters=parent_filters, child_filters=child_filters, parent_depth=parent_depth, child_depth=child_depth)
            # if a matching node is found, return it
            if success:
                return success, (desired_node, parent, child)

        # if no matching node is found, return False
        return False, (None, None)

    # Find nodes that match the given filters

    def find_nodes(self, node_filters, parent_filters, child_filters, node_depth=1, parent_depth=-1, child_depth=1):
        """
        Args:
            node_filters (dict|list): A dictionary of filters or a list of dictionaries to apply to the node.
            parent_filters (dict|list): A dictionary of filters or a list of dictionaries to apply to the parent node.
            child_filters (dict|list): A dictionary of filters or a list of dictionaries to apply to the child node.
            node_depth (int): The depth to search for the node.
            parent_depth (int): The depth to search for the parent node.
            child_depth (int): The depth to search for the child node.

        Returns:
            A tuple containing a boolean indicating whether a matching node was found, and the matching nodes, with their parent and child nodes.
        """
        # instantiate a list to store the matching nodes
        matching_nodes = []

        # get the desired nodes based on the node filters and depth
        desired_nodes = self.children(filters=node_filters, depth=node_depth)

        # check if the desired node has the specified parent and child nodes with the specified filters and depths
        for desired_node in desired_nodes:
            success, (parent, child) = desired_node.parent_child_has_attributes(
                parent_filters=parent_filters, child_filters=child_filters, parent_depth=parent_depth, child_depth=child_depth)
            # if match, add the nodes to the list of matching nodes
            if success:
                matching_nodes.append(desired_node, parent, child)

        # if a matching node is found, return it
        if matching_nodes:
            return True, matching_nodes

        # if no matching node is found, return False
        return False, matching_nodes

    def get_line_numbers(self, source_code: str) -> tuple:
        '''
        Returns the starting and ending line numbers for the code block for the current node.

        Args:
            file_content (str): The source code of the AST.

        Returns:
            tuple: A tuple containing the starting and ending line numbers for the code block.
        '''
        # Split the source code location into its components and convert to integers
        start, length, _ = map(int, (self.src.split(':')))
        end = start + length - 1
        start_line = 1 + source_code[:start].count('\n')
        end_line = 1 + source_code[:end].count('\n')

        return start_line, end_line

    def extract_code(self, source_code: str, loc: bool = True, tags: bool = True) -> str:
        """
        Extracts source code from the full source code using 'src' information.

        Args:
            source_code (str): The entire Solidity source code.
            loc (bool)(optional): If True, includes line numbers in extracted code blocks
            tags (bool)(optional): If True, includes tags("//@") in extracted code blocks

        Returns:
            str: The extracted source code segment.
        """
        # Raise an error if 'src' information is missing
        if self.src is None:
            raise ValueError("Missing 'src' information.")

        # Get the start and end line numbers of the code block
        start, end = self.get_line_numbers(source_code)

        # Get the start and length of the code block
        start_index, length, _ = map(int, self.src.split(':'))
        # Extract the code block
        extracted_code = source_code[start_index:start_index + length]

        # Add line numbers to the code block
        if loc:
            # Add line numbers to the code block
            extracted_code = insert_line_numbers((start, end), extracted_code)

        return extracted_code

# find sibling node with the given filters

    def find_sibling(self, parent_filters, sibling_filters, parent_depth=-1, sibling_depth=1):
        """
        Finds the sibling node of the current node that matches the given filters.

        Args:
            parent_filters (dict or list): a dictionary or list of dictionaries containing the attributes to check for.
            sibling_filters (dict or list): a dictionary or list of dictionaries containing the attributes to check for.
            parent_depth (int): the maximum depth to search for the parent node. Defaults to -1 (unlimited depth).
            sibling_depth (int): the maximum depth to search for the sibling node. Defaults to 1.

        Returns:
            A tuple containing three values:
            - A boolean indicating whether a sibling node was found.
            - The sibling node (if found), or None.
            - The parent node of the sibling node (if found), or None.
        """
        # get the parent node with the given filters
        parent_sucess, parent = self.parent_has_attributes(
            parent_filters, depth=parent_depth)
        if parent_sucess:
            # get the sibling node with the given filters
            sibling_sucess, sibling = parent.child_has_attributes(
                sibling_filters, depth=sibling_depth)
            if sibling_sucess:
                # return the sibling and parent node
                return sibling_sucess, sibling, parent
        # return None for both sibling and parent nodes if no match is found
        return False, None, None

    # find sibling nodes with the given filters
    def find_siblings(self, sibling_filters, parent_filters, sibling_depth=1, parent_depth=-1):
        """
        Finds the sibling nodes of the current node that match the given filters.

        Args:
            sibling_filters (dict or list): a dictionary or list of dictionaries containing the attributes to check for.
            parent_filters (dict or list): a dictionary or list of dictionaries containing the attributes to check for.
            sibling_depth (int): the maximum depth to search for the sibling node. Defaults to 1.
            parent_depth (int): the maximum depth to search for the parent node. Defaults to -1 (unlimited depth).

        Returns:
            A tuple containing three values:
            - A boolean indicating whether a sibling node was found.
            - The sibling nodes (if found), or None.
            - The parent nodes of the sibling nodes (if found), or None.
        """
        # get the parent nodes with the given filters
        parent_sucess, parent = self.parent_has_attributes(
            parent_filters, depth=parent_depth)
        if parent_sucess:
            # get the sibling nodes with the given filters
            sibling_sucess, siblings = parent.children_have_attributes(
                sibling_filters, depth=sibling_depth)
            if sibling_sucess:
                # return the sibling and parent nodes
                return sibling_sucess, siblings, parent

        # return None for both sibling and parent nodes if no match is found
        return False, None, None


class IterableNodeBase(NodeBase):
    """
    Represents an iterable version of NodeBase, allowing for convenient iteration
    and access to child nodes.
    """

    def __getitem__(self, key):
        """
        Get a child node by name.

        Args:
            key (str): The name of the child node.

        Returns:
            NodeBase: The child node.

        Raises:
            KeyError: If the child node is not found.
        """
        if isinstance(key, str):
            try:
                return next(i for i in self.nodes if getattr(i, "name", None) == key)
            except StopIteration:
                raise KeyError(key)
        return self.nodes[key]

    def __iter__(self):
        """
        Get an iterator for child nodes.

        Returns:
            iter: An iterator for child nodes.
        """
        return iter(self.nodes)

    def __len__(self):
        """
        Get the number of child nodes.

        Returns:
            int: The number of child nodes.
        """
        return len(self.nodes)

    def __contains__(self, obj):
        """
        Check if a child node exists in this iterable node.

        Args:
            obj (NodeBase): The child node to check.

        Returns:
            bool: True if the child node exists, False otherwise.

        """
        return obj in self.nodes


def node_class_factory(ast, parent):
    """
    Create a NodeBase or IterableNodeBase instance based on the given AST node.

    Args:
        ast (dict): The AST node.
        parent (NodeBase): The parent node, or None if this is the root.

    Returns:
        NodeBase or IterableNodeBase: The created node instance.
    """
    ast = deepcopy(ast)
    if not isinstance(ast, dict) or "nodeType" not in ast:
        return ast
    if "body" in ast:
        ast["nodes"] = ast.pop("body")
    base_class = IterableNodeBase if "nodes" in ast else NodeBase
    base_type = next((k for k, v in BASE_NODE_TYPES.items()
                     if ast["nodeType"] in v), None)
    if base_type:
        ast["baseNodeType"] = base_type
    return type(ast["nodeType"], (base_class,), {})(ast, parent)


def _check_filters(required_offset, offset_limits, filters, exclude, node):
    if required_offset and not is_inside_offset(required_offset, node.offset):
        return False
    if offset_limits and not is_inside_offset(node.offset, offset_limits):
        return False
    for f in filters:
        if _check_filter(node, f, exclude):
            return True
    return False


def _check_filter(node, filters, exclude):
    for key, value in filters.items():
        if node.get(key) != value:
            return False
    for key, value in exclude.items():
        if node.get(key) == value:
            return False
    return True


def _find_children(filter_fn, include_parents, include_children, find_fn, depth, node):
    if depth is not None:
        depth -= 1
        if depth < 0:
            return [node] if filter_fn(node) else []
    if not include_children and filter_fn(node):
        return [node]
    node_list = []
    for child in node._children:
        node_list.extend(find_fn(find_fn, depth, child))
    if (include_parents or not node_list) and filter_fn(node):
        node_list.insert(0, node)
    return node_list


def is_inside_offset(inner, outer):
    """Checks if the first offset is contained in the second offset

    Args:
        inner: inner offset tuple
        outer: outer offset tuple

    Returns: bool"""
    return outer[0] <= inner[0] <= inner[1] <= outer[1]


def insert_line_numbers(line_numbers: Union[int, Tuple[int, int]], code: str) -> str:
    """
    Insert line numbers in front of each line of code based on the provided range or single line number.

    Args:
        line_numbers (int or tuple): A single line number or a tuple of start and end line numbers.
        code (str): The code block as a string.

    Returns:
        str: The code block with inserted line numbers.
    """
    # Split the code into individual lines
    code_lines = code.split('\n')

    if isinstance(line_numbers, int):
        # If a single line number is provided, set it as both the start and end line
        start = line_numbers
        end = line_numbers
    elif isinstance(line_numbers, tuple) and len(line_numbers) == 2:
        # If a tuple of start and end line numbers is provided, unpack them
        start, end = line_numbers
    else:
        raise ValueError("Invalid input for line numbers.")

    i = 0
    for index in range(start, end + 1):
        # Add line numbers to each line of code
        code_lines[i] = f"{index}: {code_lines[i]}"
        i += 1
    # Rejoin the lines to form the code block with line numbers
    code_with_line_numbers = '\n'.join(code_lines)

    return code_with_line_numbers
