package ast.nodes;

import utils.Debug;

public class DeclarationNodes {

    // Variable declaration node
    public static class VarDeclarationNode extends CoreNodes.ASTNode {

        private String type;
        private String name;
        private ExpressionNodes.ExpressionNode value;

        public VarDeclarationNode(String type, String name, ExpressionNodes.ExpressionNode value) {
            super();
            this.type = type;
            this.name = name;
            this.value = value;
        }

        @Override
        public void validate(CoreNodes.Scope scope) {
            clearErrors();

            // DEBUG: Add this to track validation
            Debug.logln("DEBUG: Validating declaration for variable: " + name);

            // Normalize type for consistent checking
            String normalizedType = CoreNodes.TypeChecker.normalizeType(type);

            // Check if type is valid
            if (!CoreNodes.TypeChecker.isValidType(normalizedType)) {
                addError("Invalid type '" + type + "' in variable declaration");
                return; // Cannot proceed with invalid type
            }

            // Check for valid variable name pattern
            if (!isValidVariableName(name)) {
                addError("Invalid variable name '" + name
                        + "' (must start with letter, contain only letters, digits, and underscores)");
            }

            // FIXED: Check for duplicate declaration in ANY scope (not just current scope)
            if (scope.isDeclared(name)) {
                addError("Variable '" + name + "' already declared in current scope");
                Debug.logln("DEBUG: Duplicate declaration detected for " + name);
            }

            // Validate initial value if provided
            if (value != null) {
                value.validate(scope);
                propagateErrors(value);

                // Check type compatibility between declared type and initial value
                if (!hasErrors()) {
                    String valueType = value.getExpressionType();
                    if (!valueType.equals(CoreNodes.TypeChecker.TYPE_UNKNOWN)) {
                        if (!CoreNodes.TypeChecker.areTypesCompatible(normalizedType, valueType)) {
                            addError("Type mismatch: cannot assign "
                                    + valueType + " to " + normalizedType);
                        }
                    }
                }
            }

            // Declare variable in scope if no errors
            if (!hasErrors()) {
                scope.declareAndInitialize(name, normalizedType);
                if (value != null) {
                    Debug.logln("DEBUG: Successfully declared and initialized: " + name);
                } else {
                    Debug.logln("DEBUG: Successfully declared with default value: " + name);
                }
            } else {
                Debug.logln("DEBUG: Declaration failed for " + name + " due to errors");
            }
        }

        @Override
        public Object execute() {
            if (CoreNodes.GlobalContext.shouldExecute()) {
                String valueStr = (value != null) ? value.execute().toString() : getDefaultValue();
                CoreNodes.GlobalContext.symbolTable.put(name, valueStr);
                Debug.logln("DEBUG: Executed declaration - " + name + " = " + valueStr);
            }
            return null;
        }

        private String getDefaultValue() {
            if (type.toUpperCase().startsWith("NUMBER")) {
                return "0.0";
            } else if (type.toUpperCase().startsWith("LETTER")) {
                return "' '";
            } else if (type.toUpperCase().startsWith("LOGIC")) {
                return "false";
            } else {
                return "\"\"";
            }
        }

        /**
         * Check if variable name is valid (starts with letter, contains only
         * alphanumeric and underscore)
         */
        private boolean isValidVariableName(String name) {
            if (name == null || name.isEmpty()) {
                return false;
            }
            // Must start with letter
            if (!Character.isLetter(name.charAt(0))) {
                return false;
            }
            // Rest must be letters, digits, or underscores
            for (int i = 1; i < name.length(); i++) {
                char c = name.charAt(i);
                if (!Character.isLetterOrDigit(c) && c != '_') {
                    return false;
                }
            }
            return true;
        }



        // Getters for testing
        public String getType() {
            return type;
        }

        public String getName() {
            return name;
        }

        public ExpressionNodes.ExpressionNode getValue() {
            return value;
        }
    }

    // Assignment node
    public static class AssignmentNode extends CoreNodes.ASTNode {

        private String name;
        private String operator;
        private ExpressionNodes.ExpressionNode value;

        public AssignmentNode(String name, String operator, ExpressionNodes.ExpressionNode value) {
            super();
            this.name = name;
            this.operator = operator;
            this.value = value;
        }

        @Override
        public void validate(CoreNodes.Scope scope) {
            clearErrors();

            // DEBUG
            Debug.logln("DEBUG: Validating assignment for variable: " + name);

            // Check if variable exists in scope
            if (!scope.isDeclared(name)) {
                addError("Variable '" + name + "' not declared");
                Debug.logln("DEBUG: Undefined variable: " + name);
                return; // Cannot proceed without variable
            }

            // Get variable type
            String varType = scope.lookup(name);

            // Validate the value expression
            if (value != null) {
                value.validate(scope);
                propagateErrors(value);

                // Check type compatibility for assignments
                if (!hasErrors()) {
                    String valueType = value.getExpressionType();

                    if (operator.equals("=")) {
                        // Simple assignment - check type compatibility
                        if (!valueType.equals(CoreNodes.TypeChecker.TYPE_UNKNOWN)) {
                            if (!CoreNodes.TypeChecker.areTypesCompatible(varType, valueType)) {
                                addError("Type mismatch: cannot assign " + valueType
                                        + " to " + varType);
                            }
                        }
                    } else {
                        // Compound assignment (+=, -=, *=, /=, %=)
                        // Variable must be numeric
                        if (!varType.equals(CoreNodes.TypeChecker.TYPE_NUMBER)) {
                            addError("Cannot use compound assignment operator '" + operator
                                    + "' on non-numeric variable '" + name + "' of type " + varType);
                        }
                        // Value must be numeric
                        if (!valueType.equals(CoreNodes.TypeChecker.TYPE_UNKNOWN)
                                && !valueType.equals(CoreNodes.TypeChecker.TYPE_NUMBER)) {
                            addError("Cannot use " + valueType
                                    + " value with compound assignment operator '" + operator + "'");
                        }
                    }
                }
            } else {
                addError("Assignment requires a value");
            }

            // Mark variable as initialized after assignment
            if (!hasErrors()) {
                scope.markInitialized(name);
                Debug.logln("DEBUG: Assignment validation passed for: " + name);
            } else {
                Debug.logln("DEBUG: Assignment validation failed for: " + name);
            }
        }

        @Override
        public Object execute() {
            if (CoreNodes.GlobalContext.shouldExecute()) {
                if (!CoreNodes.GlobalContext.symbolTable.containsKey(name)) {
                    throw new RuntimeException("Undefined variable: " + name);
                }

                String valueStr = value.execute().toString();
                String varType = CoreNodes.GlobalContext.symbolTable.get(name) != null ? inferTypeFromValue(name)
                        : null;

                if (operator.equals("=")) {
                    // Simple assignment
                    // Check the variable type to determine how to store the value
                    if (varType != null) {
                        // Get the actual type from the symbol table or scope
                        // For now, we need to infer from the variable name
                        // A better approach would be to store type information with variables

                        // For string/sentence types, store as-is (without adding quotes)
                        if (value instanceof ExpressionNodes.LiteralNode) {
                            ExpressionNodes.LiteralNode literal = (ExpressionNodes.LiteralNode) value;
                            String literalValue = literal.getValue();

                            // If it's a quoted string/char literal, store without quotes
                            if ((literalValue.startsWith("\"") && literalValue.endsWith("\""))
                                    || (literalValue.startsWith("'") && literalValue.endsWith("'"))) {
                                CoreNodes.GlobalContext.symbolTable.put(name,
                                        literalValue.substring(1, literalValue.length() - 1));
                            } else {
                                CoreNodes.GlobalContext.symbolTable.put(name, literalValue);
                            }
                        } else {
                            // For expressions, just store the result
                            CoreNodes.GlobalContext.symbolTable.put(name, valueStr);
                        }
                    } else {
                        // Fallback to old behavior
                        if (valueStr.startsWith("'") && valueStr.endsWith("'")
                                || valueStr.startsWith("\"") && valueStr.endsWith("\"")) {
                            CoreNodes.GlobalContext.symbolTable.put(name,
                                    valueStr.substring(1, valueStr.length() - 1));
                        } else {
                            // Otherwise, parse it as a number or boolean
                            try {
                                Double.parseDouble(valueStr);
                                CoreNodes.GlobalContext.symbolTable.put(name, valueStr);
                            } catch (NumberFormatException e) {
                                CoreNodes.GlobalContext.symbolTable.put(name,
                                        Boolean.toString(Boolean.parseBoolean(valueStr)));
                            }
                        }
                    }
                } else {
                    // Compound assignment (+=, -=, *=, /=, %=)
                    String currentValue = CoreNodes.GlobalContext.symbolTable.get(name);
                    double val1 = Double.parseDouble(currentValue);
                    double val2 = Double.parseDouble(valueStr);
                    double result;
                    switch (operator) {
                        case "+=":
                            result = val1 + val2;
                            break;
                        case "-=":
                            result = val1 - val2;
                            break;
                        case "*=":
                            result = val1 * val2;
                            break;
                        case "/=":
                            if (val2 == 0) {
                                throw new RuntimeException("Division by zero");
                            }
                            result = val1 / val2;
                            break;
                        case "%=":
                            if (val2 == 0) {
                                throw new RuntimeException("Modulus by zero");
                            }
                            result = val1 % val2;
                            break;
                        default:
                            throw new RuntimeException("Unknown operator: " + operator);
                    }
                    CoreNodes.GlobalContext.symbolTable.put(name, String.valueOf(result));
                }
                Debug.logln("DEBUG: Executed assignment - " + name + " " + operator + " " + valueStr);
            }
            return null;
        }

        // Helper method to infer type from variable name (temporary solution)
        private String inferTypeFromValue(String varName) {
            // This is a temporary solution - ideally we'd store type info with variables
            Object value = CoreNodes.GlobalContext.symbolTable.get(varName);
            if (value == null) {
                return null;
            }

            String str = value.toString();
            try {
                Double.parseDouble(str);
                return CoreNodes.TypeChecker.TYPE_NUMBER;
            } catch (NumberFormatException e) {
                if (str.equals("true") || str.equals("false")) {
                    return CoreNodes.TypeChecker.TYPE_LOGIC;
                }
                // If it's a single character, might be LETTER
                if (str.length() == 1 && !str.matches("[0-9]")) {
                    return CoreNodes.TypeChecker.TYPE_LETTER;
                }
                // Default to SENTENCE
                return CoreNodes.TypeChecker.TYPE_SENTENCE;
            }
        }



        // Getters for testing
        public String getName() {
            return name;
        }

        public String getOperator() {
            return operator;
        }

        public ExpressionNodes.ExpressionNode getValue() {
            return value;
        }
    }

    public static class IncrementStatementNode extends CoreNodes.ASTNode {

        private String variableName;
        private boolean isPreIncrement;

        public IncrementStatementNode(String variableName, boolean isPreIncrement) {
            super();
            this.variableName = variableName;
            this.isPreIncrement = isPreIncrement;
        }

        @Override
        public void validate(CoreNodes.Scope scope) {
            clearErrors();

            // Check if variable exists in scope
            if (!scope.isDeclared(variableName)) {
                addError("Undefined variable: '" + variableName + "'");
                return;
            }

            // Check if variable is initialized
            if (!scope.isInitialized(variableName)) {
                addError("Variable '" + variableName + "' used before initialization" + " at line " + this.getLineNumber());
            }

            // Check if variable is numeric type
            String varType = scope.lookup(variableName);
            if (!varType.equals(CoreNodes.TypeChecker.TYPE_NUMBER)) {
                addError("Cannot increment non-numeric variable '" + variableName
                        + "' of type " + varType);
            }
        }

        @Override
        public Object execute() {
            if (CoreNodes.GlobalContext.shouldExecute()) {
                if (!CoreNodes.GlobalContext.symbolTable.containsKey(variableName)) {
                    throw new RuntimeException("Undefined variable: " + variableName);
                }

                Object value = CoreNodes.GlobalContext.symbolTable.get(variableName);
                double numValue;
                try {
                    numValue = Double.parseDouble(value.toString());
                } catch (NumberFormatException e) {
                    throw new RuntimeException("Cannot increment non-numeric value: " + value);
                }

                // Increment and update the symbol table
                numValue++;
                CoreNodes.GlobalContext.symbolTable.put(variableName, String.valueOf(numValue));
            }
            return null;
        }

        // Getters for testing
        public String getVariableName() {
            return variableName;
        }

        public boolean isPreIncrement() {
            return isPreIncrement;
        }
    }

    public static class DecrementStatementNode extends CoreNodes.ASTNode {

        private String variableName;
        private boolean isPreDecrement;

        public DecrementStatementNode(String variableName, boolean isPreDecrement) {
            super();
            this.variableName = variableName;
            this.isPreDecrement = isPreDecrement;
        }

        @Override
        public void validate(CoreNodes.Scope scope) {
            clearErrors();

            // Check if variable exists in scope
            if (!scope.isDeclared(variableName)) {
                addError("Undefined variable: '" + variableName + "'");
                return;
            }

            // Check if variable is initialized
            if (!scope.isInitialized(variableName)) {
                addError("Variable '" + variableName + "' used before initialization" + " at line " + this.getLineNumber());
            }

            // Check if variable is numeric type
            String varType = scope.lookup(variableName);
            if (!varType.equals(CoreNodes.TypeChecker.TYPE_NUMBER)) {
                addError("Cannot decrement non-numeric variable '" + variableName
                        + "' of type " + varType);
            }
        }

        @Override
        public Object execute() {
            if (CoreNodes.GlobalContext.shouldExecute()) {
                if (!CoreNodes.GlobalContext.symbolTable.containsKey(variableName)) {
                    throw new RuntimeException("Undefined variable: " + variableName);
                }

                Object value = CoreNodes.GlobalContext.symbolTable.get(variableName);
                double numValue;
                try {
                    numValue = Double.parseDouble(value.toString());
                } catch (NumberFormatException e) {
                    throw new RuntimeException("Cannot decrement non-numeric value: " + value);
                }

                // Decrement and update the symbol table
                numValue--;
                CoreNodes.GlobalContext.symbolTable.put(variableName, String.valueOf(numValue));
            }
            return null;
        }

        // Getters for testing
        public String getVariableName() {
            return variableName;
        }

        public boolean isPreDecrement() {
            return isPreDecrement;
        }
    }

}
