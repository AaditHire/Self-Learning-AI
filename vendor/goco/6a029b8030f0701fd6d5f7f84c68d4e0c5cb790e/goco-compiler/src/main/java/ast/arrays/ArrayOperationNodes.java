package ast.arrays;

public class ArrayOperationNodes {

    /**
     * Node for the LENGTH function
     */
    public static class ArrayLengthNode extends ast.nodes.ExpressionNodes.ExpressionNode {

        private String arrayName;

        public ArrayLengthNode(String arrayName) {
            this.arrayName = arrayName;
        }

        @Override
        public void validate(ast.nodes.CoreNodes.Scope scope) {
            clearErrors();

            // Validate array exists and is array type
            if (!scope.isDeclared(arrayName)) {
                addError("Undefined array: '" + arrayName + "'");
                return;
            }

            String arrayType = scope.lookup(arrayName);
            if (!arrayType.startsWith("ARRAY:") && !arrayType.equals("SENTENCE") && !arrayType.equals("LETTER")) {
                addError("Array '" + arrayName + "' is not an array or string");
                return;
            }

            // Check array is initialized
            if (!scope.isInitialized(arrayName)) {
                addError("Array '" + arrayName + "' used before initialization at line " + this.getLineNumber());
            }

            // Set expression type to NUMBER
            this.expressionType = "NUMBER";
        }

        public Object execute() {
            if (ast.arrays.ArrayCoreNodes.isArray(arrayName)) {
                return ast.arrays.ArrayCoreNodes.getArray(arrayName).length();
            } else {
                String val = ast.nodes.CoreNodes.GlobalContext.symbolTable.get(arrayName);
                if (val != null) {
                    return val.length();
                }
                return 0;
            }
        }
    }

    /**
     * Node for the PUSH function
     */
    public static class ArrayPushNode extends ast.nodes.CoreNodes.ASTNode {

        private String arrayName;
        private ast.nodes.ExpressionNodes.ExpressionNode valueExpr;

        public ArrayPushNode(String arrayName, ast.nodes.ExpressionNodes.ExpressionNode valueExpr) {
            this.arrayName = arrayName;
            this.valueExpr = valueExpr;
        }

        @Override
        public void validate(ast.nodes.CoreNodes.Scope scope) {
            clearErrors();

            // Validate array exists and is array type
            if (!scope.isDeclared(arrayName)) {
                addError("Undefined array: '" + arrayName + "'");
                return;
            }

            String arrayType = scope.lookup(arrayName);
            if (!arrayType.startsWith("ARRAY:")) {
                addError("Array '" + arrayName + "' is not an array");
                return;
            }

            String elementType = arrayType.substring(6);

            // Check array is initialized
            if (!scope.isInitialized(arrayName)) {
                addError("Array '" + arrayName + "' used before initialization at line " + this.getLineNumber());
            }

            // Validate value expression
            if (valueExpr != null) {
                valueExpr.validate(scope);
                propagateErrors(valueExpr);

                // Check type compatibility
                if (!ast.nodes.CoreNodes.TypeChecker.areTypesCompatible(elementType, valueExpr.getExpressionType())) {
                    addError("Cannot push " + valueExpr.getExpressionType()
                            + " to " + elementType + " array");
                }
            } else {
                addError("Array push missing value expression");
            }

            // Note: Array bounds for push are dynamic, no validation needed
        }

        @Override
        public Object execute() {
            if (ast.nodes.CoreNodes.GlobalContext.shouldExecute()) {
                if (!ArrayCoreNodes.isArray(arrayName)) {
                    throw new RuntimeException("Variable is not an array: " + arrayName);
                }

                ArrayCoreNodes.ArrayValue array = ArrayCoreNodes.getArray(arrayName);
                Object value = valueExpr.execute();
                String valueStr = value.toString();

                if (array.getType().equals("NUMBER") && !ArrayCoreNodes.isNumeric(valueStr)) {
                    throw new RuntimeException("Cannot push non-numeric value to NUMBER array: " + valueStr);
                }

                array.push(valueStr);
            }
            return null;
        }
    }

    /**
     * Node for the POP function
     */
    public static class ArrayPopNode extends ast.nodes.ExpressionNodes.ExpressionNode {

        private String arrayName;

        public ArrayPopNode(String arrayName) {
            this.arrayName = arrayName;
        }

        @Override
        public void validate(ast.nodes.CoreNodes.Scope scope) {
            clearErrors();

            // Validate array exists and is array type
            if (!scope.isDeclared(arrayName)) {
                addError("Undefined array: '" + arrayName + "'");
                return;
            }

            String arrayType = scope.lookup(arrayName);
            if (!arrayType.startsWith("ARRAY:")) {
                addError("Array '" + arrayName + "' is not an array");
                return;
            }

            String elementType = arrayType.substring(6);

            // Check array is initialized
            if (!scope.isInitialized(arrayName)) {
                addError("Array '" + arrayName + "' used before initialization at line " + this.getLineNumber());
            }

            // Note: Empty array check happens at runtime
            // Set expression type to array's element type
            this.expressionType = elementType;
        }

        @Override
        public Object execute() {
            if (!ArrayCoreNodes.isArray(arrayName)) {
                throw new RuntimeException("Variable is not an array: " + arrayName);
            }

            ArrayCoreNodes.ArrayValue array = ArrayCoreNodes.getArray(arrayName);
            return array.pop();
        }
    }

    /**
     * Node for the SET function
     */
    public static class ArraySetNode extends ast.nodes.CoreNodes.ASTNode {

        private String arrayName;
        private ast.nodes.ExpressionNodes.ExpressionNode indexExpr;
        private ast.nodes.ExpressionNodes.ExpressionNode valueExpr;

        public ArraySetNode(String arrayName, ast.nodes.ExpressionNodes.ExpressionNode indexExpr,
                ast.nodes.ExpressionNodes.ExpressionNode valueExpr) {
            this.arrayName = arrayName;
            this.indexExpr = indexExpr;
            this.valueExpr = valueExpr;
        }

        @Override
        public void validate(ast.nodes.CoreNodes.Scope scope) {
            clearErrors();

            // Validate array exists and is array type
            if (!scope.isDeclared(arrayName)) {
                addError("Undefined array: '" + arrayName + "'");
                return;
            }

            String arrayType = scope.lookup(arrayName);
            if (!arrayType.startsWith("ARRAY:")) {
                addError("Array '" + arrayName + "' is not an array");
                return;
            }

            String elementType = arrayType.substring(6);

            // Check array is initialized
            if (!scope.isInitialized(arrayName)) {
                addError("Array '" + arrayName + "' used before initialization at line " + this.getLineNumber());
            }

            // Validate index expression
            if (indexExpr != null) {
                indexExpr.validate(scope);
                propagateErrors(indexExpr);

                if (!indexExpr.getExpressionType().equals("NUMBER")) {
                    addError("Array index must be numeric expression, got "
                            + indexExpr.getExpressionType());
                }
            } else {
                addError("Array set missing index expression");
            }

            // Validate value expression
            if (valueExpr != null) {
                valueExpr.validate(scope);
                propagateErrors(valueExpr);

                // Check type compatibility
                if (!ast.nodes.CoreNodes.TypeChecker.areTypesCompatible(elementType, valueExpr.getExpressionType())) {
                    addError("Cannot set " + valueExpr.getExpressionType()
                            + " to " + elementType + " array element");
                }
            } else {
                addError("Array set missing value expression");
            }

            // Note: Array bounds checking happens at runtime
        }

        @Override
        public Object execute() {
            if (ast.nodes.CoreNodes.GlobalContext.shouldExecute()) {
                if (!ArrayCoreNodes.isArray(arrayName)) {
                    throw new RuntimeException("Variable is not an array: " + arrayName);
                }

                ArrayCoreNodes.ArrayValue array = ArrayCoreNodes.getArray(arrayName);
                int index;

                try {
                    Object indexObj = indexExpr.execute();
                    if (indexObj instanceof Number) {
                        index = ((Number) indexObj).intValue();
                    } else {
                        String indexStr = indexObj.toString().trim();
                        if (indexStr.startsWith("\"") && indexStr.endsWith("\"")) {
                            indexStr = indexStr.substring(1, indexStr.length() - 1);
                        }
                        double doubleIndex = Double.parseDouble(indexStr);
                        index = (int) doubleIndex;
                        if (doubleIndex != index) {
                            throw new RuntimeException("Array index must be an integer: " + doubleIndex + " at line " + this.getLineNumber());
                        }
                    }
                } catch (NumberFormatException e) {
                    throw new RuntimeException("Array index must be a number: " + indexExpr.execute().toString() + " at line " + this.getLineNumber());
                }

                Object value = valueExpr.execute();
                String valueStr = value.toString();

                if (array.getType().equals("NUMBER") && !ArrayCoreNodes.isNumeric(valueStr)) {
                    throw new RuntimeException("Cannot set non-numeric value to NUMBER array: " + valueStr);
                }

                array.setElement(index, valueStr);
            }
            return null;
        }
    }

    /**
     * Node for the GET function
     */
    public static class ArrayGetNode extends ast.nodes.ExpressionNodes.ExpressionNode {

        private String arrayName;
        private ast.nodes.ExpressionNodes.ExpressionNode indexExpr;

        public ArrayGetNode(String arrayName, ast.nodes.ExpressionNodes.ExpressionNode indexExpr) {
            this.arrayName = arrayName;
            this.indexExpr = indexExpr;
        }

        @Override
        public void validate(ast.nodes.CoreNodes.Scope scope) {
            clearErrors();

            // Validate array exists and is array type
            if (!scope.isDeclared(arrayName)) {
                addError("Undefined array: '" + arrayName + "'");
                return;
            }

            String arrayType = scope.lookup(arrayName);
            if (!arrayType.startsWith("ARRAY:")) {
                addError("Array '" + arrayName + "' is not an array");
                return;
            }

            String elementType = arrayType.substring(6);

            // Check array is initialized
            if (!scope.isInitialized(arrayName)) {
                addError("Array '" + arrayName + "' used before initialization at line " + this.getLineNumber());
            }

            // Validate index expression
            if (indexExpr != null) {
                indexExpr.validate(scope);
                propagateErrors(indexExpr);

                if (!indexExpr.getExpressionType().equals("NUMBER")) {
                    addError("Array index must be numeric expression, got "
                            + indexExpr.getExpressionType());
                }
            } else {
                addError("Array get missing index expression");
            }

            // Set expression type to array's element type
            this.expressionType = elementType;

            // Note: Array bounds checking happens at runtime
        }

        @Override
        public Object execute() {
            if (!ArrayCoreNodes.isArray(arrayName)) {
                throw new RuntimeException("Variable is not an array: " + arrayName);
            }

            ArrayCoreNodes.ArrayValue array = ArrayCoreNodes.getArray(arrayName);
            int index;

            try {
                Object indexObj = indexExpr.execute();
                if (indexObj instanceof Number) {
                    index = ((Number) indexObj).intValue();
                } else {
                    String indexStr = indexObj.toString().trim();
                    if (indexStr.startsWith("\"") && indexStr.endsWith("\"")) {
                        indexStr = indexStr.substring(1, indexStr.length() - 1);
                    }
                    double doubleIndex = Double.parseDouble(indexStr);
                    index = (int) doubleIndex;
                    if (doubleIndex != index) {
                        throw new RuntimeException("Array index must be an integer: " + doubleIndex + " at line " + this.getLineNumber());
                    }
                }
            } catch (NumberFormatException e) {
                throw new RuntimeException("Array index must be a number: " + indexExpr.execute().toString() + " at line " + this.getLineNumber());
            }

            return array.getElement(index);
        }
    }

    /**
     * Node for POP as an expression (for use in DISPLAYNL(POP(arr)))
     */
    public static class ArrayPopExpressionNode extends ast.nodes.ExpressionNodes.ExpressionNode {

        private String arrayName;

        public ArrayPopExpressionNode(String arrayName) {
            this.arrayName = arrayName;
        }

        @Override
        public void validate(ast.nodes.CoreNodes.Scope scope) {
            clearErrors();

            // Check if array exists
            if (!scope.isDeclared(arrayName)) {
                addError("Undefined array: '" + arrayName + "'");
                return;
            }

            // Check that it's actually an array
            String type = scope.lookup(arrayName);
            if (!type.startsWith("ARRAY:")) {
                addError("Array '" + arrayName + "' is not an array");
                return;
            }

            // Check if array is initialized
            if (!scope.isInitialized(arrayName)) {
                addError("Array '" + arrayName + "' used before initialization at line " + this.getLineNumber());
            }

            // POP returns the element type from the array
            String elementType = type.substring(6); // Remove "ARRAY:"
            this.expressionType = elementType;
        }

        @Override
        public Object execute() {
            if (!ArrayCoreNodes.isArray(arrayName)) {
                throw new RuntimeException("Variable is not an array: " + arrayName);
            }

            ArrayCoreNodes.ArrayValue array = ArrayCoreNodes.getArray(arrayName);
            String popped = array.pop();

            // Return the popped value (without quotes for display)
            if (popped.startsWith("\"") && popped.endsWith("\"")
                    || popped.startsWith("'") && popped.endsWith("'")) {
                return popped.substring(1, popped.length() - 1);
            }
            return popped;
        }
    }

}
