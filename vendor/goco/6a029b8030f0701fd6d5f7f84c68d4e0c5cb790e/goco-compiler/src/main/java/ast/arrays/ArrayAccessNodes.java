package ast.arrays;

import java.io.*;
import utils.Debug;

public class ArrayAccessNodes {

    /**
     * Node for accessing an array element (arr[index])
     */
    public static class ArrayAccessNode extends ast.nodes.ExpressionNodes.ExpressionNode {

        private String arrayName;
        private ast.nodes.ExpressionNodes.ExpressionNode indexExpr;

        public ArrayAccessNode(String arrayName, ast.nodes.ExpressionNodes.ExpressionNode indexExpr) {
            this.arrayName = arrayName;
            this.indexExpr = indexExpr;
        }

        public ArrayAccessNode(String arrayName, ast.nodes.ExpressionNodes.ExpressionNode indexExpr, int lineNumber) {
            this.arrayName = arrayName;
            this.indexExpr = indexExpr;
            this.setLineNumber(lineNumber);
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

            String elementType = arrayType.substring(6); // Remove "ARRAY:"

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
                addError("Array access missing index expression");
            }

            // Set expression type to array's element type
            this.expressionType = elementType;
        }

        @Override
        public Object execute() {
            if (!ArrayCoreNodes.isArray(arrayName)) {
                throw new RuntimeException("Variable is not an array: " + arrayName
                        + " at line " + this.getLineNumber());
            }

            ArrayCoreNodes.ArrayValue array = ArrayCoreNodes.getArray(arrayName);
            String arrayType = array.getType();

            // Calculate index
            Object indexResult = indexExpr.execute();

            // Check if index is numeric and integer
            try {
                double indexValue = Double.parseDouble(indexResult.toString());
                if (Math.floor(indexValue) != indexValue) {
                    throw new RuntimeException("Array index must be an integer: " + indexValue
                            + " at line " + this.getLineNumber());
                }
                int index = (int) indexValue;

                if (index < 0 || index >= array.length()) {
                    throw new RuntimeException("Array index " + index + " out of bounds for length "
                            + array.length() + " at line " + this.getLineNumber());
                }

                String value = array.getElement(index);

                // Format value based on array type
                switch (arrayType) {
                    case "SENTENCE":
                        return value.startsWith("\"") && value.endsWith("\"")
                                ? value.substring(1, value.length() - 1)
                                : value;
                    case "LETTER":
                        return value.startsWith("'") && value.endsWith("'")
                                ? value.substring(1, value.length() - 1)
                                : value;
                    case "LOGIC":
                        return value.toLowerCase();
                    case "NUMBER":
                    default:
                        return value;
                }
            } catch (NumberFormatException e) {
                throw new RuntimeException("Array index must be numeric, got: " + indexResult
                        + " at line " + this.getLineNumber());
            }
        }

    }

    /**
     * Node for assigning a value to an array element (arr[index] = value)
     */
    public static class ArrayElementAssignmentNode extends ast.nodes.CoreNodes.ASTNode {

        private String arrayName;
        private ast.nodes.ExpressionNodes.ExpressionNode indexExpr;
        private ast.nodes.ExpressionNodes.ExpressionNode valueExpr;

        public ArrayElementAssignmentNode(String arrayName, ast.nodes.ExpressionNodes.ExpressionNode indexExpr,
                ast.nodes.ExpressionNodes.ExpressionNode valueExpr) {
            this.arrayName = arrayName;
            this.indexExpr = indexExpr;
            this.valueExpr = valueExpr;
        }

        // Add this constructor to set line number at creation
        public ArrayElementAssignmentNode(String arrayName, ast.nodes.ExpressionNodes.ExpressionNode indexExpr,
                ast.nodes.ExpressionNodes.ExpressionNode valueExpr, int lineNumber) {
            this.arrayName = arrayName;
            this.indexExpr = indexExpr;
            this.valueExpr = valueExpr;
            this.setLineNumber(lineNumber);
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
                addError("Array element assignment missing index expression");
            }

            // Validate value expression
            if (valueExpr != null) {
                valueExpr.validate(scope);
                propagateErrors(valueExpr);

                // Check type compatibility
                if (!ast.nodes.CoreNodes.TypeChecker.areTypesCompatible(elementType, valueExpr.getExpressionType())) {
                    addError("Cannot assign " + valueExpr.getExpressionType()
                            + " to " + elementType + " array element");
                }
            } else {
                addError("Array element assignment missing value expression");
            }

            // Mark array as modified (stays initialized)
        }

        @Override
        public Object execute() {
            if (ast.nodes.CoreNodes.GlobalContext.shouldExecute()) {
                if (!ArrayCoreNodes.isArray(arrayName)) {
                    throw new RuntimeException("Variable is not an array: " + arrayName);
                }

                ArrayCoreNodes.ArrayValue array = ArrayCoreNodes.getArray(arrayName);

                // Calculate the index
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
                            throw new RuntimeException("Array index must be an integer: " + doubleIndex + " at line "
                                    + this.getLineNumber());
                        }
                    }
                } catch (NumberFormatException e) {
                    throw new RuntimeException("Array index must be a number: " + indexExpr.execute().toString()
                            + " at line " + this.getLineNumber());
                }

                // Get the value to assign
                Object value = valueExpr.execute();

                // Check if the value is a sub-array (e.g., matrix[i] = NEW NUMBER[3])
                if (value instanceof ArrayCoreNodes.ArrayValue) {
                    ArrayCoreNodes.ArrayValue subArray = (ArrayCoreNodes.ArrayValue) value;
                    String subArrayName = ArrayCoreNodes.generateNestedArrayName(arrayName);
                    ArrayCoreNodes.putArray(subArrayName, subArray);
                    ast.nodes.CoreNodes.GlobalContext.symbolTable.put(subArrayName,
                            "ARRAY:" + subArray.getType() + ":" + subArrayName);
                    array.setElement(index, subArrayName);
                } else {
                    String valueStr = value.toString();

                    // Validate the value for the array type
                    if (array.getType().equals("NUMBER") && !ArrayCoreNodes.isNumeric(valueStr)) {
                        throw new RuntimeException("Cannot assign non-numeric value to NUMBER array: " + valueStr);
                    }

                    // Set the element at the specified index
                    array.setElement(index, valueStr);
                }
            }
            return null;
        }
    }

    /**
     * Node for compound assignment to an array element (arr[index] += value)
     */
    public static class ArrayElementCompoundAssignmentNode extends ast.nodes.CoreNodes.ASTNode {

        private String arrayName;
        private ast.nodes.ExpressionNodes.ExpressionNode indexExpr;
        private String operator;
        private ast.nodes.ExpressionNodes.ExpressionNode valueExpr;

        public ArrayElementCompoundAssignmentNode(String arrayName, ast.nodes.ExpressionNodes.ExpressionNode indexExpr,
                String operator, ast.nodes.ExpressionNodes.ExpressionNode valueExpr) {
            this.arrayName = arrayName;
            this.indexExpr = indexExpr;
            this.operator = operator;
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
                addError("Array compound assignment missing index expression");
            }

            // Validate value expression
            if (valueExpr != null) {
                valueExpr.validate(scope);
                propagateErrors(valueExpr);

                // Validate operation compatibility
                validateCompoundOperation(elementType, valueExpr.getExpressionType());
            } else {
                addError("Array compound assignment missing value expression");
            }
        }

        /**
         * Validate compound assignment operation compatibility
         */
        private void validateCompoundOperation(String elementType, String valueType) {
            if (operator.equals("+=")) {
                // += can work for NUMBER and SENTENCE arrays
                if (elementType.equals("SENTENCE")) {
                    // SENTENCE arrays can concatenate with any type
                    return; // All types are convertible to string
                } else if (elementType.equals("NUMBER")) {
                    // NUMBER arrays require numeric operands
                    if (!valueType.equals("NUMBER")) {
                        addError("Cannot use += with " + valueType
                                + " on NUMBER array element");
                    }
                } else {
                    // LETTER and LOGIC arrays don't support +=
                    addError("Compound assignment '" + operator
                            + "' not supported for " + elementType + " arrays");
                }
            } else {
                // -=, *=, /=, %= only work for NUMBER arrays
                if (!elementType.equals("NUMBER")) {
                    addError("Arithmetic compound assignment '" + operator
                            + "' only supported for NUMBER arrays");
                } else if (!valueType.equals("NUMBER")) {
                    addError("Cannot use " + operator + " with " + valueType
                            + " on NUMBER array element");
                }
            }
        }

        @Override
        public Object execute() {
            if (ast.nodes.CoreNodes.GlobalContext.shouldExecute()) {
                if (!ArrayCoreNodes.isArray(arrayName)) {
                    throw new RuntimeException("Variable is not an array: " + arrayName);
                }

                ArrayCoreNodes.ArrayValue array = ArrayCoreNodes.getArray(arrayName);

                // Calculate the index
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
                            throw new RuntimeException("Array index must be an integer: " + doubleIndex + " at line "
                                    + this.getLineNumber());
                        }
                    }
                } catch (NumberFormatException e) {
                    throw new RuntimeException("Array index must be a number: " + indexExpr.execute().toString()
                            + " at line " + this.getLineNumber());
                }

                // Get the current value
                String currentValue = array.getElement(index).toString();
                String newValueStr = valueExpr.execute().toString();

                // Perform the compound operation
                String result;
                if (operator.equals("+=")) {
                    if (array.getType().toUpperCase().startsWith("SENTENCE")) {
                        result = currentValue + newValueStr;
                    } else {
                        double val1 = Double.parseDouble(currentValue);
                        double val2 = Double.parseDouble(newValueStr);
                        result = String.valueOf(val1 + val2);
                    }
                } else {
                    double val1 = Double.parseDouble(currentValue);
                    double val2 = Double.parseDouble(newValueStr);
                    switch (operator) {
                        case "-=":
                            result = String.valueOf(val1 - val2);
                            break;
                        case "*=":
                            result = String.valueOf(val1 * val2);
                            break;
                        case "/=":
                            if (val2 == 0) {
                                throw new RuntimeException("Division by zero");
                            }
                            result = String.valueOf(val1 / val2);
                            break;
                        case "%=":
                            if (val2 == 0) {
                                throw new RuntimeException("Modulus by zero");
                            }
                            result = String.valueOf(val1 % val2);
                            break;
                        default:
                            throw new RuntimeException("Unknown operator: " + operator);
                    }
                }

                array.setElement(index, result);
            }
            return null;
        }
    }

    /**
     * Node for handling input to array elements
     */
    public static class ArrayElementInputNode extends ast.nodes.CoreNodes.ASTNode {

        private String arrayName;
        private ast.nodes.ExpressionNodes.ExpressionNode indexExpr;

        public ArrayElementInputNode(String arrayName, ast.nodes.ExpressionNodes.ExpressionNode indexExpr) {
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
                addError("Array element input missing index expression");
            }

            // Note: Input type validation happens at runtime
            // Mark array as modified (stays initialized)
        }

        @Override
        public Object execute() {
            if (ast.nodes.CoreNodes.GlobalContext.shouldExecute()) {
                if (!ArrayCoreNodes.isArray(arrayName)) {
                    throw new RuntimeException("Variable is not an array: " + arrayName);
                }

                ArrayCoreNodes.ArrayValue array = ArrayCoreNodes.getArray(arrayName);
                int index = (int) Double.parseDouble(indexExpr.execute().toString());
                if (index < 0 || index >= array.length()) {
                    throw new RuntimeException("Array index " + index + " out of bounds for length " + array.length());
                }

                BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
                try {
                    // MUST use System.out directly (not Debug.log) so the IDE can detect the prompt
                    System.out.print("Enter value for " + arrayName + "[" + index + "]: ");
                    System.out.flush(); // Force flush — critical when stdout is piped
                    String userInput = reader.readLine();

                    if (userInput == null) {
                        throw new RuntimeException("No input received for " + arrayName + "[" + index + "]");
                    }

                    if (array.getType().equals("LETTER")) {
                        if (userInput.length() != 1) {
                            throw new RuntimeException("LETTER input must be a single character.");
                        }
                        array.setElement(index, "'" + userInput + "'");
                    } else if (array.getType().equals("NUMBER")) {
                        try {
                            Double.parseDouble(userInput);
                            array.setElement(index, userInput);
                        } catch (NumberFormatException e) {
                            throw new RuntimeException("Numeric input required");
                        }
                    } else {
                        array.setElement(index, userInput);
                    }
                } catch (IOException e) {
                    Debug.errln("Error: Failed to read input.");
                }
            }
            return null;
        }
    }

    /**
     * Node for multi-dimensional array access (arr[i][j]) in expressions.
     * Resolves the outer expression to get a sub-array name, then accesses the
     * element.
     */
    public static class MultiDimArrayAccessNode extends ast.nodes.ExpressionNodes.ExpressionNode {

        private ast.nodes.ExpressionNodes.ExpressionNode outerExpr;
        private ast.nodes.ExpressionNodes.ExpressionNode indexExpr;

        public MultiDimArrayAccessNode(ast.nodes.ExpressionNodes.ExpressionNode outerExpr,
                ast.nodes.ExpressionNodes.ExpressionNode indexExpr) {
            this.outerExpr = outerExpr;
            this.indexExpr = indexExpr;
        }

        @Override
        public void validate(ast.nodes.CoreNodes.Scope scope) {
            clearErrors();

            // Validate outer expression
            if (outerExpr != null) {
                outerExpr.validate(scope);
                propagateErrors(outerExpr);
            }

            // Validate index expression
            if (indexExpr != null) {
                indexExpr.validate(scope);
                propagateErrors(indexExpr);

                if (indexExpr.getExpressionType() != null
                        && !indexExpr.getExpressionType().equals("NUMBER")
                        && !indexExpr.getExpressionType().equals(ast.nodes.CoreNodes.TypeChecker.TYPE_UNKNOWN)) {
                    addError("Array index must be numeric expression, got "
                            + indexExpr.getExpressionType());
                }
            }

            // The result type is the element type of the inner array.
            // Since we can't statically know the sub-array type easily,
            // we set it to NUMBER (most common) or UNKNOWN.
            // At runtime it will resolve correctly.
            this.expressionType = "NUMBER";
        }

        @Override
        public Object execute() {
            // Execute outer expression to get the sub-array name
            Object outerResult = outerExpr.execute();
            String subArrayName = outerResult.toString();

            // Look up the sub-array
            if (!ArrayCoreNodes.isArray(subArrayName)) {
                throw new RuntimeException("Multi-dimensional array access failed: '"
                        + subArrayName + "' is not a sub-array at line " + this.getLineNumber());
            }

            ArrayCoreNodes.ArrayValue subArray = ArrayCoreNodes.getArray(subArrayName);

            // Calculate index
            Object indexResult = indexExpr.execute();
            try {
                double indexValue = Double.parseDouble(indexResult.toString());
                if (Math.floor(indexValue) != indexValue) {
                    throw new RuntimeException("Array index must be an integer: " + indexValue
                            + " at line " + this.getLineNumber());
                }
                int index = (int) indexValue;

                if (index < 0 || index >= subArray.length()) {
                    throw new RuntimeException("Array index " + index + " out of bounds for length "
                            + subArray.length() + " at line " + this.getLineNumber());
                }

                String value = subArray.getElement(index);

                // Format value based on array type
                switch (subArray.getType()) {
                    case "SENTENCE":
                        return value.startsWith("\"") && value.endsWith("\"")
                                ? value.substring(1, value.length() - 1)
                                : value;
                    case "LETTER":
                        return value.startsWith("'") && value.endsWith("'")
                                ? value.substring(1, value.length() - 1)
                                : value;
                    case "LOGIC":
                        return value.toLowerCase();
                    case "NUMBER":
                    default:
                        return value;
                }
            } catch (NumberFormatException e) {
                throw new RuntimeException("Array index must be numeric, got: " + indexResult
                        + " at line " + this.getLineNumber());
            }
        }
    }

    /**
     * Node for multi-dimensional array element assignment (arr[i][j] = value).
     * Resolves the outer index to find the sub-array, then sets the inner element.
     */
    public static class MultiDimArrayElementAssignmentNode extends ast.nodes.CoreNodes.ASTNode {

        private String arrayName;
        private ast.nodes.ExpressionNodes.ExpressionNode outerIndexExpr;
        private ast.nodes.ExpressionNodes.ExpressionNode innerIndexExpr;
        private ast.nodes.ExpressionNodes.ExpressionNode valueExpr;

        public MultiDimArrayElementAssignmentNode(String arrayName,
                ast.nodes.ExpressionNodes.ExpressionNode outerIndexExpr,
                ast.nodes.ExpressionNodes.ExpressionNode innerIndexExpr,
                ast.nodes.ExpressionNodes.ExpressionNode valueExpr) {
            this.arrayName = arrayName;
            this.outerIndexExpr = outerIndexExpr;
            this.innerIndexExpr = innerIndexExpr;
            this.valueExpr = valueExpr;
        }

        @Override
        public void validate(ast.nodes.CoreNodes.Scope scope) {
            clearErrors();

            // Validate array exists
            if (!scope.isDeclared(arrayName)) {
                addError("Undefined array: '" + arrayName + "'");
                return;
            }

            String arrayType = scope.lookup(arrayName);
            if (!arrayType.startsWith("ARRAY:")) {
                addError("Variable '" + arrayName + "' is not an array");
                return;
            }

            // Check array is initialized
            if (!scope.isInitialized(arrayName)) {
                addError("Array '" + arrayName + "' used before initialization at line " + this.getLineNumber());
            }

            // Validate outer index expression
            if (outerIndexExpr != null) {
                outerIndexExpr.validate(scope);
                propagateErrors(outerIndexExpr);
                if (outerIndexExpr.getExpressionType() != null
                        && !outerIndexExpr.getExpressionType().equals("NUMBER")
                        && !outerIndexExpr.getExpressionType().equals(ast.nodes.CoreNodes.TypeChecker.TYPE_UNKNOWN)) {
                    addError("Outer array index must be numeric expression, got "
                            + outerIndexExpr.getExpressionType());
                }
            }

            // Validate inner index expression
            if (innerIndexExpr != null) {
                innerIndexExpr.validate(scope);
                propagateErrors(innerIndexExpr);
                if (innerIndexExpr.getExpressionType() != null
                        && !innerIndexExpr.getExpressionType().equals("NUMBER")
                        && !innerIndexExpr.getExpressionType().equals(ast.nodes.CoreNodes.TypeChecker.TYPE_UNKNOWN)) {
                    addError("Inner array index must be numeric expression, got "
                            + innerIndexExpr.getExpressionType());
                }
            }

            // Validate value expression
            if (valueExpr != null) {
                valueExpr.validate(scope);
                propagateErrors(valueExpr);

                String baseType = arrayType;
                while (baseType.startsWith("ARRAY:")) {
                    baseType = baseType.substring(6);
                }

                String valueType = valueExpr.getExpressionType();
                if (valueType != null && !ast.nodes.CoreNodes.TypeChecker.areTypesCompatible(baseType, valueType)) {
                    addError("Type mismatch: cannot assign " + valueType + " to " + baseType);
                }
            }
        }

        @Override
        public Object execute() {
            if (ast.nodes.CoreNodes.GlobalContext.shouldExecute()) {
                if (!ArrayCoreNodes.isArray(arrayName)) {
                    throw new RuntimeException("Variable is not an array: " + arrayName);
                }

                ArrayCoreNodes.ArrayValue outerArray = ArrayCoreNodes.getArray(arrayName);

                // Calculate outer index
                int outerIndex;
                try {
                    Object indexObj = outerIndexExpr.execute();
                    double doubleIndex = Double.parseDouble(indexObj.toString());
                    outerIndex = (int) doubleIndex;
                    if (doubleIndex != outerIndex) {
                        throw new RuntimeException("Array index must be an integer: " + doubleIndex
                                + " at line " + this.getLineNumber());
                    }
                } catch (NumberFormatException e) {
                    throw new RuntimeException("Array index must be a number at line " + this.getLineNumber());
                }

                // Get sub-array name from outer array
                String subArrayName = outerArray.getElement(outerIndex);
                if (!ArrayCoreNodes.isArray(subArrayName)) {
                    throw new RuntimeException("Element at index " + outerIndex
                            + " is not a sub-array (value: " + subArrayName
                            + ") at line " + this.getLineNumber());
                }

                ArrayCoreNodes.ArrayValue subArray = ArrayCoreNodes.getArray(subArrayName);

                // Calculate inner index
                int innerIndex;
                try {
                    Object indexObj = innerIndexExpr.execute();
                    double doubleIndex = Double.parseDouble(indexObj.toString());
                    innerIndex = (int) doubleIndex;
                    if (doubleIndex != innerIndex) {
                        throw new RuntimeException("Array index must be an integer: " + doubleIndex
                                + " at line " + this.getLineNumber());
                    }
                } catch (NumberFormatException e) {
                    throw new RuntimeException("Array index must be a number at line " + this.getLineNumber());
                }

                // Get and set the value
                Object value = valueExpr.execute();
                String valueStr = value.toString();

                if (subArray.getType().equals("NUMBER") && !ArrayCoreNodes.isNumeric(valueStr)) {
                    throw new RuntimeException("Cannot assign non-numeric value to NUMBER array: " + valueStr);
                }

                subArray.setElement(innerIndex, valueStr);
            }
            return null;
        }
    }

    /**
     * Node for triple-dimensional array element assignment (arr[i][j][k] = value)
     */
    public static class TripleDimArrayElementAssignmentNode extends ast.nodes.CoreNodes.ASTNode {

        private String arrayName;
        private ast.nodes.ExpressionNodes.ExpressionNode firstIndexExpr;
        private ast.nodes.ExpressionNodes.ExpressionNode secondIndexExpr;
        private ast.nodes.ExpressionNodes.ExpressionNode thirdIndexExpr;
        private ast.nodes.ExpressionNodes.ExpressionNode valueExpr;

        public TripleDimArrayElementAssignmentNode(String arrayName,
                ast.nodes.ExpressionNodes.ExpressionNode firstIndexExpr,
                ast.nodes.ExpressionNodes.ExpressionNode secondIndexExpr,
                ast.nodes.ExpressionNodes.ExpressionNode thirdIndexExpr,
                ast.nodes.ExpressionNodes.ExpressionNode valueExpr) {
            this.arrayName = arrayName;
            this.firstIndexExpr = firstIndexExpr;
            this.secondIndexExpr = secondIndexExpr;
            this.thirdIndexExpr = thirdIndexExpr;
            this.valueExpr = valueExpr;
        }

        @Override
        public void validate(ast.nodes.CoreNodes.Scope scope) {
            clearErrors();

            // Validate array exists
            if (!scope.isDeclared(arrayName)) {
                addError("Undefined array: '" + arrayName + "'");
                return;
            }

            String arrayType = scope.lookup(arrayName);
            if (!arrayType.startsWith("ARRAY:")) {
                addError("Variable '" + arrayName + "' is not an array");
                return;
            }

            // Check array is initialized
            if (!scope.isInitialized(arrayName)) {
                addError("Array '" + arrayName + "' used before initialization at line " + this.getLineNumber());
            }

            // Validate first index
            validateIndex(firstIndexExpr, "first", scope);
            // Validate second index
            validateIndex(secondIndexExpr, "second", scope);
            // Validate third index
            validateIndex(thirdIndexExpr, "third", scope);

            // Validate value expression
            if (valueExpr != null) {
                valueExpr.validate(scope);
                propagateErrors(valueExpr);

                // Determine base element type (strip all array dimensions)
                String baseType = arrayType;
                while (baseType.startsWith("ARRAY:")) {
                    baseType = baseType.substring(6);
                }

                String valueType = valueExpr.getExpressionType();
                if (valueType != null && !ast.nodes.CoreNodes.TypeChecker.areTypesCompatible(baseType, valueType)) {
                    addError("Type mismatch: cannot assign " + valueType + " to " + baseType);
                }
            } else {
                addError("Triple-dim array assignment missing value expression");
            }
        }

        private void validateIndex(ast.nodes.ExpressionNodes.ExpressionNode idxExpr, String position,
                ast.nodes.CoreNodes.Scope scope) {
            if (idxExpr != null) {
                idxExpr.validate(scope);
                propagateErrors(idxExpr);
                if (idxExpr.getExpressionType() != null
                        && !idxExpr.getExpressionType().equals("NUMBER")
                        && !idxExpr.getExpressionType().equals(ast.nodes.CoreNodes.TypeChecker.TYPE_UNKNOWN)) {
                    addError(position + " array index must be numeric expression, got " + idxExpr.getExpressionType());
                }
            } else {
                addError("Triple-dim array assignment missing " + position + " index expression");
            }
        }

        @Override
        public Object execute() {
            if (ast.nodes.CoreNodes.GlobalContext.shouldExecute()) {
                if (!ArrayCoreNodes.isArray(arrayName)) {
                    throw new RuntimeException("Variable is not an array: " + arrayName);
                }

                ArrayCoreNodes.ArrayValue firstLevelArray = ArrayCoreNodes.getArray(arrayName);

                // First index
                int firstIdx = evaluateIndex(firstIndexExpr);
                // Get sub-array name from first level
                String secondLevelName = firstLevelArray.getElement(firstIdx);
                if (!ArrayCoreNodes.isArray(secondLevelName)) {
                    throw new RuntimeException("Element at index " + firstIdx + " is not a sub-array (value: "
                            + secondLevelName + ") at line " + this.getLineNumber());
                }
                ArrayCoreNodes.ArrayValue secondLevelArray = ArrayCoreNodes.getArray(secondLevelName);

                // Second index
                int secondIdx = evaluateIndex(secondIndexExpr);
                // Get third level array name
                String thirdLevelName = secondLevelArray.getElement(secondIdx);
                if (!ArrayCoreNodes.isArray(thirdLevelName)) {
                    throw new RuntimeException("Element at indices [" + firstIdx + "][" + secondIdx
                            + "] is not a sub-array (value: " + thirdLevelName + ") at line " + this.getLineNumber());
                }
                ArrayCoreNodes.ArrayValue thirdLevelArray = ArrayCoreNodes.getArray(thirdLevelName);

                // Third index
                int thirdIdx = evaluateIndex(thirdIndexExpr);

                // Assign value
                Object value = valueExpr.execute();
                String valueStr = value.toString();

                if (thirdLevelArray.getType().equals("NUMBER") && !ArrayCoreNodes.isNumeric(valueStr)) {
                    throw new RuntimeException("Cannot assign non-numeric value to NUMBER array: " + valueStr);
                }

                thirdLevelArray.setElement(thirdIdx, valueStr);
            }
            return null;
        }

        private int evaluateIndex(ast.nodes.ExpressionNodes.ExpressionNode idxExpr) {
            try {
                Object idxObj = idxExpr.execute();
                double doubleIdx = Double.parseDouble(idxObj.toString());
                int idx = (int) doubleIdx;
                if (doubleIdx != idx) {
                    throw new RuntimeException(
                            "Array index must be an integer: " + doubleIdx + " at line " + this.getLineNumber());
                }
                return idx;
            } catch (NumberFormatException e) {
                throw new RuntimeException("Array index must be a number at line " + this.getLineNumber());
            }
        }
    }
}
