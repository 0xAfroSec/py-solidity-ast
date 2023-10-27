

# This list is incomplete - feel free to add to it and open a pull request
# https://solidity.readthedocs.io/en/latest/miscellaneous.html#language-grammar

BASE_NODE_TYPES = {
    "SourceUnit": [
        "ImportDirective", 
        "LibraryDefinition", 
        "ContractDefinition", 
        "InterfaceDefinition"
        ],
    "ContractPart": [
        "ConstructorDefinition",
        "ErrorDefinition",
        "EnumDefinition",
        "EventDefinition",
        "FunctionDefinition",
        "FallbackFunctionDefinition",
        "ReceiveFunctionDefinition"
        "ModifierDefinition",
        "StateVariableDeclaration",
        "StructDefinition",
        "UsingForDeclaration",
    ],
    "Expression": [
        "Assignment",
        "BinaryOperation",
        "Conditional",
        "FunctionCall",
        "IndexAccess",
        "MemberAccess",
        "NewExpression",
        "UnaryOperation",
        "VariableDeclaration",
    ],
    "PrimaryExpression": [
        "BooleanLiteral",
        "ElementaryTypeNameExpression",
        "HexLiteral",
        "Identifier",
        "NumberLiteral",
        "StringLiteral",
        "TupleExpression",
    ],
    "Statement": [
        "BreakStatement",
        "ContinueStatement",
        "DoWhileStatement",
        "EmitStatement",
        "ExpressionStatement",
        "ForStatement",
        "IfStatement",
        "InlineAssemblyStatement",
        "PlaceholderStatement",
        "SimpleStatement",
        "TryStatement",
        "Throw",
        "WhileStatement",
        "ReturnStatement",
        "RevertStatement",
        "AssemblyStatement"
    ],
    "TypeName": [
        "ArrayTypeName",
        "ElementaryTypeName",
        "FunctionTypeName",
        "Mapping",
        "UserDefinedTypeName",
        "IdentifierPath",
    ],
    "YulStatement": [
        'YulVariableDeclaration',
        "YulAssignment",
        "YulFunctionCall",
        "YulIfStatement",
        "YulForStatement",
        "YulSwitchStatement",
        "Leave",
        "Break",
        "Continue",
        "YulFunctionDefinition"
    ]
}
