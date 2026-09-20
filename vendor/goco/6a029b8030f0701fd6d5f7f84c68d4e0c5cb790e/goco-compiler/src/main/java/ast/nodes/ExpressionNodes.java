package ast.nodes;

public class ExpressionNodes {

    // Base expression node with type tracking
    public static abstract class ExpressionNode extends CoreNodes.ASTNode {

        protected String expressionType;

        public ExpressionNode() {
            super();
            this.expressionType = CoreNodes.TypeChecker.TYPE_UNKNOWN;
        }

        @Override
        public abstract Object execute();

        /**
         * Get the inferred type of this expression
         */
        public String getExpressionType() {
            return expressionType;
        }

        /**
         * Set the expression type (for type inference)
         */
        protected void setExpressionType(String type) {
            this.expressionType = type;
        }
    }

    // Literal expression node
    public static class LiteralNode extends ExpressionNode {

        private String value;
        private boolean isProcessed; // Track if escape sequences are already processed

        public LiteralNode(String value) {
            this(value, false);
        }

        public LiteralNode(String value, boolean isProcessed) {
            super();
            this.value = value;
            this.isProcessed = isProcessed;
        }

        @Override
        public void validate(CoreNodes.Scope scope) {
            clearErrors();

            // For processed literals (escape sequences already converted),
            // treat them as SENTENCE type (string)
            if (isProcessed) {
                // Still infer type from the raw literal
                this.expressionType = CoreNodes.TypeChecker.inferTypeFromLiteral(value);
                return;
            }

            // Infer type from literal value (for unprocessed literals)
            this.expressionType = CoreNodes.TypeChecker.inferTypeFromLiteral(value);

            if (this.expressionType.equals(CoreNodes.TypeChecker.TYPE_UNKNOWN)) {
                addError("Invalid literal format: '" + value + "'");
                return;
            }

            // Validate literal format
            if (value != null) {
                // Check for mismatched quotes
                if (value.startsWith("'") && !value.endsWith("'")) {
                    addError("Mismatched single quotes in literal: '" + value + "'");
                } else if (value.startsWith("\"") && !value.endsWith("\"")) {
                    addError("Mismatched double quotes in literal: '" + value + "'");
                }

                // Validate character literals (should be single character)
                if (value.startsWith("'") && value.endsWith("'") && value.length() > 3) {
                    addError("Character literal can only contain one character: '" + value + "'");
                }

                // Validate empty character literal
                if (value.equals("''")) {
                    addError("Empty character literal is not allowed");
                }
            }
        }

        @Override
        public Object execute() {
            // If already processed, return as-is
            if (isProcessed) {
                // For character literals that have been processed, they might not have quotes
                // For string literals, we need to handle them differently
                if (value != null && value.length() >= 2) {
                    // Check if it's a quoted string
                    if ((value.startsWith("\"") && value.endsWith("\""))
                            || (value.startsWith("'") && value.endsWith("'"))) {
                        // Return the content without quotes
                        return value.substring(1, value.length() - 1);
                    }
                }
                return value != null ? value : "";
            }

            // For unprocessed literals, format them
            String formatted = CoreNodes.GlobalContext.formatLiteral(value);

            // For character literals, we want to return just the character without quotes
            if (value != null && value.length() >= 2 && value.startsWith("'") && value.endsWith("'")) {
                // It's a character literal
                String content = value.substring(1, value.length() - 1);
                // Process escape sequences in the content
                StringBuilder processed = new StringBuilder();
                for (int i = 0; i < content.length(); i++) {
                    char c = content.charAt(i);
                    if (c == '\\' && i + 1 < content.length()) {
                        char next = content.charAt(i + 1);
                        switch (next) {
                            case 'n':
                                processed.append('\n');
                                i++;
                                break;
                            case 't':
                                processed.append('\t');
                                i++;
                                break;
                            case '\\':
                                processed.append('\\');
                                i++;
                                break;
                            case '\'':
                                processed.append('\'');
                                i++;
                                break;
                            case '"':
                                processed.append('"');
                                i++;
                                break;
                            default:
                                processed.append(c);
                                break;
                        }
                    } else {
                        processed.append(c);
                    }
                }
                return processed.toString();
            }

            // For string literals, remove quotes if present
            if (value != null && value.length() >= 2) {
                if ((value.startsWith("\"") && value.endsWith("\""))
                        || (value.startsWith("'") && value.endsWith("'"))) {
                    return value.substring(1, value.length() - 1);
                }
            }

            return formatted != null ? formatted : "";
        }

        // Getter for testing
        public String getValue() {
            return value;
        }
    }

    // Variable reference node
    public static class VariableNode extends ExpressionNode {

        private String name;

        public VariableNode(String name) {
            super();
            this.name = name;
        }

        @Override
        public void validate(CoreNodes.Scope scope) {
            clearErrors();

            // Check variable exists
            if (!scope.isDeclared(name)) {
                addError("Undefined variable: '" + name + "'");
                this.expressionType = CoreNodes.TypeChecker.TYPE_UNKNOWN;
                return;
            }

            // Get variable type
            this.expressionType = scope.lookup(name);

            // Check variable is initialized
            if (!scope.isInitialized(name)) {
                addError("Variable '" + name + "' used before initialization" + " at line " + this.getLineNumber());
            }
        }

        @Override
        public Object execute() {
            if (!CoreNodes.GlobalContext.symbolTable.containsKey(name)) {
                throw new RuntimeException("Undefined variable: " + name);
            }
            return CoreNodes.GlobalContext.symbolTable.get(name);
        }

        // Getter for testing
        public String getName() {
            return name;
        }
    }

    public static class BinaryOperationNode extends ExpressionNode {

        private String operator;
        private ExpressionNode left;
        private ExpressionNode right;

        public BinaryOperationNode(String operator, ExpressionNode left, ExpressionNode right) {
            super();
            this.operator = operator;
            this.left = left;
            this.right = right;
        }

        @Override
        public void validate(CoreNodes.Scope scope) {
            clearErrors();

            // Validate left operand
            if (left != null) {
                left.validate(scope);
                propagateErrors(left);
            } else {
                addError("Binary operation missing left operand");
            }

            // Validate right operand
            if (right != null) {
                right.validate(scope);
                propagateErrors(right);
            } else {
                addError("Binary operation missing right operand");
            }

            // Proceed with type checking if both operands are valid
            if (left != null && right != null && !hasErrors()) {
                String leftType = left.getExpressionType();
                String rightType = right.getExpressionType();

                // Skip type checking if either type is unknown (already has errors)
                if (!leftType.equals(CoreNodes.TypeChecker.TYPE_UNKNOWN)
                        && !rightType.equals(CoreNodes.TypeChecker.TYPE_UNKNOWN)) {
                    validateBinaryOperation(leftType, rightType);
                }
            }
        }

        /**
         * Validate type compatibility for binary operations
         */
        private void validateBinaryOperation(String leftType, String rightType) {
            switch (operator) {
                case "+":
                    // Special case: + can be arithmetic OR string concatenation
                    if (leftType.equals(CoreNodes.TypeChecker.TYPE_NUMBER)
                            && rightType.equals(CoreNodes.TypeChecker.TYPE_NUMBER)) {
                        // Both numbers -> arithmetic
                        this.expressionType = CoreNodes.TypeChecker.TYPE_NUMBER;
                    } else if (leftType.equals(CoreNodes.TypeChecker.TYPE_SENTENCE)
                            || leftType.equals(CoreNodes.TypeChecker.TYPE_LETTER)
                            || rightType.equals(CoreNodes.TypeChecker.TYPE_SENTENCE)
                            || rightType.equals(CoreNodes.TypeChecker.TYPE_LETTER)) {
                        // If either operand is string/char type, it's concatenation -> result is
                        // SENTENCE
                        this.expressionType = CoreNodes.TypeChecker.TYPE_SENTENCE;
                    } else if ((leftType.equals(CoreNodes.TypeChecker.TYPE_NUMBER) || leftType.equals(CoreNodes.TypeChecker.TYPE_LOGIC))
                            && (rightType.equals(CoreNodes.TypeChecker.TYPE_NUMBER) || rightType.equals(CoreNodes.TypeChecker.TYPE_LOGIC))) {
                        // Number + Logic -> Number
                        this.expressionType = CoreNodes.TypeChecker.TYPE_NUMBER;
                    } else if (leftType.equals(CoreNodes.TypeChecker.TYPE_LOGIC)
                            || rightType.equals(CoreNodes.TypeChecker.TYPE_LOGIC)) {
                        // If either is boolean and the other is NOT numeric, treat as concatenation (converted to string)
                        this.expressionType = CoreNodes.TypeChecker.TYPE_SENTENCE;
                    } else {
                        // Incompatible types for +
                        addError("Operator '+' cannot be applied to " + leftType + " and " + rightType);
                        this.expressionType = CoreNodes.TypeChecker.TYPE_UNKNOWN;
                    }
                    break;

                case "-":
                case "*":
                case "/":
                case "%":
                    // Arithmetic operators require numeric operands
                    if (!leftType.equals(CoreNodes.TypeChecker.TYPE_NUMBER)
                            || !rightType.equals(CoreNodes.TypeChecker.TYPE_NUMBER)) {
                        addError("Arithmetic operator '" + operator
                                + "' requires numeric operands, got " + leftType + " and " + rightType);
                    }
                    this.expressionType = CoreNodes.TypeChecker.TYPE_NUMBER;
                    break;

                case "&&":
                case "||":
                    // Logical operators require boolean operands
                    if (!leftType.equals(CoreNodes.TypeChecker.TYPE_LOGIC)
                            || !rightType.equals(CoreNodes.TypeChecker.TYPE_LOGIC)) {
                        addError("Logical operator '" + operator
                                + "' requires boolean operands, got " + leftType + " and " + rightType);
                    }
                    this.expressionType = CoreNodes.TypeChecker.TYPE_LOGIC;
                    break;

                case ">":
                case "<":
                case ">=":
                case "<=":
                    // Relational operators require numeric operands
                    if (!leftType.equals(CoreNodes.TypeChecker.TYPE_NUMBER)
                            || !rightType.equals(CoreNodes.TypeChecker.TYPE_NUMBER)) {
                        addError("Relational operator '" + operator
                                + "' requires numeric operands, got " + leftType + " and " + rightType);
                    }
                    this.expressionType = CoreNodes.TypeChecker.TYPE_LOGIC;
                    break;

                case "==":
                case "!=":
                    // Equality operators require compatible types
                    if (!CoreNodes.TypeChecker.areTypesCompatible(leftType, rightType)
                            && !CoreNodes.TypeChecker.areTypesCompatible(rightType, leftType)) {
                        addError("Equality operator '" + operator
                                + "' requires compatible types, got " + leftType + " and " + rightType);
                    }
                    this.expressionType = CoreNodes.TypeChecker.TYPE_LOGIC;
                    break;

                default:
                    addError("Unknown binary operator: '" + operator + "'");
                    this.expressionType = CoreNodes.TypeChecker.TYPE_UNKNOWN;
                    break;
            }
        }

        @Override
        public Object execute() {
            // Always execute both sides to ensure proper evaluation
            Object leftResult = left.execute();
            Object rightResult = right.execute();

            // Handle string concatenation with + operator
            if (operator.equals("+")) {
                // Get the raw values without any processing
                String leftStr = leftResult != null ? leftResult.toString() : "";
                String rightStr = rightResult != null ? rightResult.toString() : "";

                // Check if this is string concatenation
                // Get the expression types from validation
                String leftType = left.getExpressionType();
                String rightType = right.getExpressionType();

                boolean leftIsStringType = leftType != null
                        && (leftType.equals(CoreNodes.TypeChecker.TYPE_SENTENCE)
                        || leftType.equals(CoreNodes.TypeChecker.TYPE_LETTER));
                boolean rightIsStringType = rightType != null
                        && (rightType.equals(CoreNodes.TypeChecker.TYPE_SENTENCE)
                        || rightType.equals(CoreNodes.TypeChecker.TYPE_LETTER));

                // Also check the actual values (only if they're long enough to have quotes)
                boolean leftLooksLikeString = leftStr.length() >= 2
                        && (leftStr.startsWith("\"") || leftStr.startsWith("'"));
                boolean rightLooksLikeString = rightStr.length() >= 2
                        && (rightStr.startsWith("\"") || rightStr.startsWith("'"));

                // If either operand is a string type or looks like a string literal, do
                // concatenation
                if (leftIsStringType || rightIsStringType || leftLooksLikeString || rightLooksLikeString) {
                    // Remove quotes if present and string is long enough
                    if (leftStr.length() >= 2 && (leftStr.startsWith("\"") || leftStr.startsWith("'"))) {
                        leftStr = leftStr.substring(1, leftStr.length() - 1);
                    } else if (isNumeric(leftStr)) {
                        try {
                            leftStr = String.valueOf(Double.parseDouble(leftStr));
                        } catch (Exception e) {
                        }
                    }
                    if (rightStr.length() >= 2 && (rightStr.startsWith("\"") || rightStr.startsWith("'"))) {
                        rightStr = rightStr.substring(1, rightStr.length() - 1);
                    } else if (isNumeric(rightStr)) {
                        try {
                            rightStr = String.valueOf(Double.parseDouble(rightStr));
                        } catch (Exception e) {
                        }
                    }

                    // For string concatenation, return WITHOUT quotes
                    return leftStr + rightStr;
                }

                // Otherwise, try numeric addition
                try {
                    double val1 = leftStr.equals("true") ? 1.0 : leftStr.equals("false") ? 0.0 : Double.parseDouble(leftStr);
                    double val2 = rightStr.equals("true") ? 1.0 : rightStr.equals("false") ? 0.0 : Double.parseDouble(rightStr);
                    return String.valueOf(val1 + val2);
                } catch (NumberFormatException e) {
                    // If not numeric, treat as string concatenation
                    if (leftStr.length() >= 2 && (leftStr.startsWith("\"") || leftStr.startsWith("'"))) {
                        leftStr = leftStr.substring(1, leftStr.length() - 1);
                    } else if (isNumeric(leftStr)) {
                        try {
                            leftStr = String.valueOf(Double.parseDouble(leftStr));
                        } catch (Exception ex) {
                        }
                    }
                    if (rightStr.length() >= 2 && (rightStr.startsWith("\"") || rightStr.startsWith("'"))) {
                        rightStr = rightStr.substring(1, rightStr.length() - 1);
                    } else if (isNumeric(rightStr)) {
                        try {
                            rightStr = String.valueOf(Double.parseDouble(rightStr));
                        } catch (Exception ex) {
                        }
                    }
                    return leftStr + rightStr;
                }
            }

            // Handle arithmetic operations (non-plus)
            if (operator.equals("-") || operator.equals("*")
                    || operator.equals("/") || operator.equals("%")) {
                double val1 = Double.parseDouble(leftResult.toString());
                double val2 = Double.parseDouble(rightResult.toString());
                switch (operator) {
                    case "-":
                        return String.valueOf(val1 - val2);
                    case "*":
                        return String.valueOf(val1 * val2);
                    case "/":
                        if (val2 == 0) {
                            throw new RuntimeException("Division by zero");
                        }
                        return String.valueOf(val1 / val2);
                    case "%":
                        if (val2 == 0) {
                            throw new RuntimeException("Modulus by zero");
                        }
                        return String.valueOf(val1 % val2);
                }
            }

            // Handle comparison operations
            if (operator.equals(">") || operator.equals("<")
                    || operator.equals(">=") || operator.equals("<=")
                    || operator.equals("==") || operator.equals("!=")) {

                // Check if both are quoted strings or characters
                if (isQuotedString(leftResult.toString()) && isQuotedString(rightResult.toString())) {
                    // Safely remove quotes for comparison
                    String l = safeRemoveQuotes(leftResult.toString());
                    String r = safeRemoveQuotes(rightResult.toString());
                    switch (operator) {
                        case "==":
                            return String.valueOf(l.equals(r));
                        case "!=":
                            return String.valueOf(!l.equals(r));
                        default:
                            throw new RuntimeException("Invalid operator for string/char comparison");
                    }
                }

                // Try numeric comparison
                try {
                    double val1 = Double.parseDouble(leftResult.toString());
                    double val2 = Double.parseDouble(rightResult.toString());
                    switch (operator) {
                        case ">":
                            return String.valueOf(val1 > val2);
                        case "<":
                            return String.valueOf(val1 < val2);
                        case ">=":
                            return String.valueOf(val1 >= val2);
                        case "<=":
                            return String.valueOf(val1 <= val2);
                        case "==":
                            return String.valueOf(Math.abs(val1 - val2) < 0.000001);
                        case "!=":
                            return String.valueOf(Math.abs(val1 - val2) >= 0.000001);
                    }
                } catch (NumberFormatException e) {
                    // If not numbers and not strings/chars, treat as boolean comparison
                    if (leftResult.toString().equals("true") || leftResult.toString().equals("false")
                            || rightResult.toString().equals("true") || rightResult.toString().equals("false")) {
                        boolean val1 = Boolean.parseBoolean(leftResult.toString());
                        boolean val2 = Boolean.parseBoolean(rightResult.toString());
                        switch (operator) {
                            case "==":
                                return String.valueOf(val1 == val2);
                            case "!=":
                                return String.valueOf(val1 != val2);
                            default:
                                throw new RuntimeException("Invalid operator for boolean values");
                        }
                    }
                }
            }

            // Handle logical operations
            if (operator.equals("&&") || operator.equals("||")) {
                boolean val1 = Boolean.parseBoolean(leftResult.toString());
                boolean val2 = Boolean.parseBoolean(rightResult.toString());
                switch (operator) {
                    case "&&":
                        return String.valueOf(val1 && val2);
                    case "||":
                        return String.valueOf(val1 || val2);
                }
            }

            // If we get here, operator is not supported
            throw new RuntimeException("Unsupported operator: " + operator);
        }

        // Helper method to safely remove quotes from a string
        private String safeRemoveQuotes(String str) {
            if (str == null) {
                return "";
            }

            // Check if the string has at least 2 characters and starts and ends with quotes
            if (str.length() >= 2) {
                if ((str.startsWith("\"") && str.endsWith("\""))
                        || (str.startsWith("'") && str.endsWith("'"))) {
                    return str.substring(1, str.length() - 1);
                }
            }
            return str;
        }

        // Update the existing removeQuotes method to use the safe version
        private String removeQuotes(String str) {
            return safeRemoveQuotes(str);
        }

        // Helper method to check if a string is quoted
        private boolean isQuotedString(String str) {
            return (str.startsWith("\"") && str.endsWith("\""))
                    || (str.startsWith("'") && str.endsWith("'"));
        }

        // Helper method to check if a string represents a number
        private boolean isNumeric(String str) {
            if (isQuotedString(str)) {
                return false;
            }
            try {
                Double.parseDouble(str);
                return true;
            } catch (NumberFormatException e) {
                return false;
            }
        }

        // Getters for testing
        public String getOperator() {
            return operator;
        }

        public ExpressionNode getLeft() {
            return left;
        }

        public ExpressionNode getRight() {
            return right;
        }
    }

    public static class UnaryOperationNode extends ExpressionNode {

        private String operator;
        private ExpressionNode operand;

        public UnaryOperationNode(String operator, ExpressionNode operand) {
            super();
            this.operator = operator;
            this.operand = operand;
        }

        @Override
        public void validate(CoreNodes.Scope scope) {
            clearErrors();

            // Validate operand
            if (operand != null) {
                operand.validate(scope);
                propagateErrors(operand);
            } else {
                addError("Unary operation missing operand");
                return;
            }

            // Proceed with type checking if operand is valid
            if (!hasErrors()) {
                String operandType = operand.getExpressionType();

                // Skip type checking if operand type is unknown (already has errors)
                if (!operandType.equals(CoreNodes.TypeChecker.TYPE_UNKNOWN)) {
                    validateUnaryOperation(operandType);
                }
            }
        }

        /**
         * Validate type compatibility for unary operations
         */
        private void validateUnaryOperation(String operandType) {
            switch (operator) {
                case "!":
                    // Logical NOT requires boolean operand
                    if (!operandType.equals(CoreNodes.TypeChecker.TYPE_LOGIC)) {
                        addError("Logical NOT operator '!' requires boolean operand, got " + operandType);
                    }
                    this.expressionType = CoreNodes.TypeChecker.TYPE_LOGIC;
                    break;

                case "-":
                case "+":
                    // Unary plus/minus requires numeric operand
                    if (!operandType.equals(CoreNodes.TypeChecker.TYPE_NUMBER)) {
                        addError("Unary operator '" + operator
                                + "' requires numeric operand, got " + operandType);
                    }
                    this.expressionType = CoreNodes.TypeChecker.TYPE_NUMBER;
                    break;

                default:
                    addError("Unknown unary operator: '" + operator + "'");
                    this.expressionType = CoreNodes.TypeChecker.TYPE_UNKNOWN;
                    break;
            }
        }

        @Override
        public Object execute() {
            // Always execute operand to ensure proper evaluation
            Object result = operand.execute();
            String value = result != null ? result.toString() : "null";

            if (operator.equals("!")) {
                return String.valueOf(!Boolean.parseBoolean(value));
            } else if (operator.equals("-")) {
                try {
                    double val = Double.parseDouble(value);
                    return String.valueOf(-val);
                } catch (NumberFormatException e) {
                    throw new RuntimeException("Unary minus requires a numeric operand");
                }
            } else if (operator.equals("+")) {
                try {
                    double val = Double.parseDouble(value);
                    return String.valueOf(val);
                } catch (NumberFormatException e) {
                    throw new RuntimeException("Unary plus requires a numeric operand");
                }
            }

            // If we get here, operator is not supported
            throw new RuntimeException("Unsupported unary operator: " + operator);
        }

        // Getters for testing
        public String getOperator() {
            return operator;
        }

        public ExpressionNode getOperand() {
            return operand;
        }
    }

    public static class PreIncrementNode extends ExpressionNode {

        private String variableName;

        public PreIncrementNode(String variableName) {
            super();
            this.variableName = variableName;
        }

        @Override
        public void validate(CoreNodes.Scope scope) {
            clearErrors();

            // Check if variable exists in scope
            if (!scope.isDeclared(variableName)) {
                addError("Undefined variable: '" + variableName + "'");
                this.expressionType = CoreNodes.TypeChecker.TYPE_UNKNOWN;
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

            // Pre-increment returns NUMBER
            this.expressionType = CoreNodes.TypeChecker.TYPE_NUMBER;
        }

        @Override
        public Object execute() {
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

            // Increment first, then return
            numValue++;
            String result = String.valueOf(numValue);
            CoreNodes.GlobalContext.symbolTable.put(variableName, result);
            return result;
        }

        // Getter for testing
        public String getVariableName() {
            return variableName;
        }
    }

    public static class PostIncrementNode extends ExpressionNode {

        private String variableName;

        public PostIncrementNode(String variableName) {
            super();
            this.variableName = variableName;
        }

        @Override
        public void validate(CoreNodes.Scope scope) {
            clearErrors();

            // Check if variable exists in scope
            if (!scope.isDeclared(variableName)) {
                addError("Undefined variable: '" + variableName + "'");
                this.expressionType = CoreNodes.TypeChecker.TYPE_UNKNOWN;
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

            // Post-increment returns NUMBER
            this.expressionType = CoreNodes.TypeChecker.TYPE_NUMBER;
        }

        @Override
        public Object execute() {
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

            // Save the original value to return
            String originalValue = String.valueOf(numValue);
            // Increment and update the symbol table
            numValue++;
            CoreNodes.GlobalContext.symbolTable.put(variableName, String.valueOf(numValue));
            // Return the original value
            return originalValue;
        }

        // Getter for testing
        public String getVariableName() {
            return variableName;
        }
    }

    public static class PreDecrementNode extends ExpressionNode {

        private String variableName;

        public PreDecrementNode(String variableName) {
            super();
            this.variableName = variableName;
        }

        @Override
        public void validate(CoreNodes.Scope scope) {
            clearErrors();

            // Check if variable exists in scope
            if (!scope.isDeclared(variableName)) {
                addError("Undefined variable: '" + variableName + "'");
                this.expressionType = CoreNodes.TypeChecker.TYPE_UNKNOWN;
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

            // Pre-decrement returns NUMBER
            this.expressionType = CoreNodes.TypeChecker.TYPE_NUMBER;
        }

        @Override
        public Object execute() {
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

            // Decrement first, then return
            numValue--;
            String result = String.valueOf(numValue);
            CoreNodes.GlobalContext.symbolTable.put(variableName, result);
            return result;
        }

        // Getter for testing
        public String getVariableName() {
            return variableName;
        }
    }

    public static class PostDecrementNode extends ExpressionNode {

        private String variableName;

        public PostDecrementNode(String variableName) {
            super();
            this.variableName = variableName;
        }

        @Override
        public void validate(CoreNodes.Scope scope) {
            clearErrors();

            // Check if variable exists in scope
            if (!scope.isDeclared(variableName)) {
                addError("Undefined variable: '" + variableName + "'");
                this.expressionType = CoreNodes.TypeChecker.TYPE_UNKNOWN;
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

            // Post-decrement returns NUMBER
            this.expressionType = CoreNodes.TypeChecker.TYPE_NUMBER;
        }

        @Override
        public Object execute() {
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

            // Save the original value to return
            String originalValue = String.valueOf(numValue);
            // Decrement and update the symbol table
            numValue--;
            CoreNodes.GlobalContext.symbolTable.put(variableName, String.valueOf(numValue));
            // Return the original value
            return originalValue;
        }

        // Getter for testing
        public String getVariableName() {
            return variableName;
        }
    }

    public static class StringConcatNode extends ExpressionNode {

        private ExpressionNode left;
        private ExpressionNode right;

        public StringConcatNode(ExpressionNode left, ExpressionNode right) {
            super();
            this.left = left;
            this.right = right;
        }

        @Override
        public void validate(CoreNodes.Scope scope) {
            clearErrors();

            // Validate left operand
            if (left != null) {
                left.validate(scope);
                propagateErrors(left);
            } else {
                addError("String concatenation missing left operand");
            }

            // Validate right operand
            if (right != null) {
                right.validate(scope);
                propagateErrors(right);
            } else {
                addError("String concatenation missing right operand");
            }

            // String concatenation always results in SENTENCE type
            this.expressionType = CoreNodes.TypeChecker.TYPE_SENTENCE;
        }

        @Override
        public Object execute() {
            Object leftResult = left.execute();
            Object rightResult = right.execute();

            String leftStr = leftResult != null ? leftResult.toString() : "";
            String rightStr = rightResult != null ? rightResult.toString() : "";

            // Remove quotes if present and string is long enough
            if (leftStr.length() >= 2) {
                if ((leftStr.startsWith("\"") && leftStr.endsWith("\""))
                        || (leftStr.startsWith("'") && leftStr.endsWith("'"))) {
                    leftStr = leftStr.substring(1, leftStr.length() - 1);
                }
            }

            if (rightStr.length() >= 2) {
                if ((rightStr.startsWith("\"") && rightStr.endsWith("\""))
                        || (rightStr.startsWith("'") && rightStr.endsWith("'"))) {
                    rightStr = rightStr.substring(1, rightStr.length() - 1);
                }
            }

            // Return WITHOUT quotes
            return leftStr + rightStr;
        }

        // Helper method to remove quotes from a string
        private String removeQuotes(String str) {
            if (str == null) {
                return "";
            }

            // Check if the string has at least 2 characters and starts and ends with quotes
            if (str.length() >= 2) {
                if ((str.startsWith("\"") && str.endsWith("\""))
                        || (str.startsWith("'") && str.endsWith("'"))) {
                    return str.substring(1, str.length() - 1);
                }
            }
            return str;
        }

        @Override
        public String toString() {
            return left.toString() + " + " + right.toString();
        }
    }

}
