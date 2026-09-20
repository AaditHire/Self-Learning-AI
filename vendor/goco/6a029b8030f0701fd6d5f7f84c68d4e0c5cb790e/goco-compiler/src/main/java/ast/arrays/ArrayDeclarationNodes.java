package ast.arrays;

import java.util.*;

public class ArrayDeclarationNodes {

    /**
     * Node for declaring and initializing arrays
     */
    public static class ArrayDeclarationNode extends ast.nodes.CoreNodes.ASTNode {

        private String type;
        private String name;
        private ast.nodes.ExpressionNodes.ExpressionNode value;
        private int dimensions;

        public ArrayDeclarationNode(String type, String name, ast.nodes.ExpressionNodes.ExpressionNode value) {
            this(type, name, value, 1);
        }

        public ArrayDeclarationNode(String type, String name, ast.nodes.ExpressionNodes.ExpressionNode value, int dimensions) {
            this.type = type.toUpperCase();
            this.name = name;
            this.value = value;
            this.dimensions = dimensions;
        }

        @Override
        public void validate(ast.nodes.CoreNodes.Scope scope) {
            clearErrors();

            // Normalize and validate array type
            String normalizedType = ast.nodes.CoreNodes.TypeChecker.normalizeType(type);
            if (!ast.nodes.CoreNodes.TypeChecker.isValidType(normalizedType)) {
                addError("Invalid array type '" + type + "'");
                return;
            }

            // Check for duplicate declaration
            if (scope.isDeclaredInCurrentScopeOnly(name)) {
                addError("Duplicate array declaration: '" + name + "'");
            }

            // Validate variable name pattern
            if (!isValidVariableName(name)) {
                addError("Invalid array name '" + name + "'");
            }

            // Register array in scope FIRST (before validating value)
            // This ensures the array exists when validating its initializer
            if (!hasErrors() && !scope.isDeclaredInCurrentScopeOnly(name)) {
                StringBuilder arrayTypeStr = new StringBuilder();
                for (int i = 0; i < dimensions; i++) {
                    arrayTypeStr.append("ARRAY:");
                }
                arrayTypeStr.append(normalizedType);
                scope.declare(name, arrayTypeStr.toString());
            }

            // Validate initializer expression if present
            if (value != null) {
                // If value is an ArrayLiteralNode, pass the expected type to it
                if (value instanceof ArrayLiteralNode) {
                    if (dimensions > 1) {
                        StringBuilder expType = new StringBuilder();
                        for (int i = 1; i < dimensions; i++) {
                            expType.append("ARRAY:");
                        }
                        expType.append(normalizedType);
                        ((ArrayLiteralNode) value).setExpectedType(expType.toString());
                    } else {
                        ((ArrayLiteralNode) value).setExpectedType(normalizedType);
                    }
                }

                value.validate(scope);
                propagateErrors(value);

                // Compute full array type to check compatibility
                StringBuilder arrayTypeStrBuilder = new StringBuilder();
                for (int i = 0; i < dimensions; i++) {
                    arrayTypeStrBuilder.append("ARRAY:");
                }
                arrayTypeStrBuilder.append(normalizedType);
                String fullArrayType = arrayTypeStrBuilder.toString();

                // Check initializer is array type
                String valueType = value.getExpressionType();
                if (valueType == null || !valueType.startsWith("ARRAY")) {
                    addError("Array initializer must be array expression, got "
                            + (valueType != null ? valueType : "null"));
                } else {
                    // Check type compatibility
                    if (!valueType.equals(fullArrayType)) {
                        addError("Array element type mismatch: expected " + fullArrayType
                                + ", got " + valueType + " at line " + value.getLineNumber());
                    }
                }

                // Mark array as initialized if value is valid
                if (!hasErrors()) {
                    scope.markInitialized(name);
                }
            } else {
                // No initializer - array is declared but not initialized
                // Still mark as declared but not initialized
                // This is valid for arrays that will be assigned later
            }
        }

        @Override
        public Object execute() {
            // Handle array declaration without initializer
            if (value == null) {
                // Create an empty array of the specified type
                ArrayCoreNodes.ArrayValue array = new ArrayCoreNodes.ArrayValue(type);
                ArrayCoreNodes.putArray(name, array);
                ast.nodes.CoreNodes.GlobalContext.symbolTable.put(name, "ARRAY:" + type + ":" + name);
                return null;
            }

            // If the value is an ArrayLiteralNode, pass the type to it
            if (value instanceof ArrayLiteralNode) {
                ((ArrayLiteralNode) value).setType(type);
            }

            // Execute the value (static or dynamic array)
            Object executedValue = value.execute();
            ArrayCoreNodes.ArrayValue array;
            if (executedValue instanceof ArrayCoreNodes.ArrayValue) {
                array = (ArrayCoreNodes.ArrayValue) executedValue;
            } else if (executedValue instanceof String) {
                String potentialArrayName = (String) executedValue;
                if (ArrayCoreNodes.isArray(potentialArrayName)) {
                    array = ArrayCoreNodes.getArray(potentialArrayName);
                } else {
                    throw new RuntimeException("Expression did not return a valid array: " + potentialArrayName);
                }
            } else {
                 throw new RuntimeException("Cannot initialize array with " + executedValue);
            }
            
            ArrayCoreNodes.putArray(name, array);
            ast.nodes.CoreNodes.GlobalContext.symbolTable.put(name, "ARRAY:" + type + ":" + name);
            return null;
        }

        /**
         * Check if variable name is valid
         */
        private boolean isValidVariableName(String name) {
            if (name == null || name.isEmpty()) {
                return false;
            }
            if (!Character.isLetter(name.charAt(0))) {
                return false;
            }
            for (char c : name.toCharArray()) {
                if (!Character.isLetterOrDigit(c) && c != '_') {
                    return false;
                }
            }
            return true;
        }
    }

    /**
     * Node for array literals [1, 2, 3]
     */
    public static class ArrayLiteralNode extends ast.nodes.ExpressionNodes.ExpressionNode {

        private String type;
        private String expectedType; // Type expected by the declaration context
        private List<ast.nodes.ExpressionNodes.ExpressionNode> elements;

        public ArrayLiteralNode(List<ast.nodes.ExpressionNodes.ExpressionNode> elements) {
            this.elements = elements;
            this.type = null; // Will be set during validation or execution
            this.expectedType = null;
        }

        public void setType(String type) {
            this.type = type.toUpperCase();
        }

        public void setExpectedType(String expectedType) {
            this.expectedType = expectedType.toUpperCase();
        }

        @Override
        public void validate(ast.nodes.CoreNodes.Scope scope) {
            clearErrors();

            // Validate all element expressions and collect their types
            String inferredType = null;
            boolean hasInconsistentTypes = false;

            for (ast.nodes.ExpressionNodes.ExpressionNode element : elements) {
                element.validate(scope);
                propagateErrors(element);

                // Get element type
                String elementType = element.getExpressionType();

                // Handle literal nodes that might not have proper type yet
                if (element instanceof ast.nodes.ExpressionNodes.LiteralNode) {
                    ast.nodes.ExpressionNodes.LiteralNode lit = (ast.nodes.ExpressionNodes.LiteralNode) element;
                    // Force type inference if needed
                    if (elementType == null || elementType.equals(ast.nodes.CoreNodes.TypeChecker.TYPE_UNKNOWN)) {
                        elementType = ast.nodes.CoreNodes.TypeChecker.inferTypeFromLiteral(lit.getValue());
                    }
                }

                // Infer array element type from first element
                if (inferredType == null && elementType != null
                        && !elementType.equals(ast.nodes.CoreNodes.TypeChecker.TYPE_UNKNOWN)) {
                    inferredType = elementType;
                } // Check consistency with subsequent elements
                else if (inferredType != null && elementType != null
                        && !elementType.equals(ast.nodes.CoreNodes.TypeChecker.TYPE_UNKNOWN)) {
                    if (!elementType.equals(inferredType)) {
                        hasInconsistentTypes = true;
                        addError("Inconsistent element types in array literal: "
                                + inferredType + " and " + elementType + " at index " + elements.indexOf(element));
                    }
                }
            }

            // Determine final type
            String finalType;
            if (expectedType != null) {
                // Expected type from declaration context
                finalType = expectedType;

                // Check compatibility with inferred type if available
                if (inferredType != null && !inferredType.equals(ast.nodes.CoreNodes.TypeChecker.TYPE_UNKNOWN)) {
                    if (!ast.nodes.CoreNodes.TypeChecker.areTypesCompatible(finalType, inferredType)) {
                        addError("Array element type mismatch: declared " + finalType
                                + ", initializer " + inferredType + " at line " + this.getLineNumber());
                    }
                }
            } else if (type != null) {
                // Type explicitly set (from setType)
                finalType = type;
            } else if (inferredType != null && !hasInconsistentTypes) {
                // No parent type but all elements consistent - infer from elements
                finalType = inferredType;
            } else if (elements.isEmpty()) {
                // Empty array literal - type will be determined by context
                finalType = ast.nodes.CoreNodes.TypeChecker.TYPE_UNKNOWN;
            } else {
                // Inconsistent types or no type info
                finalType = ast.nodes.CoreNodes.TypeChecker.TYPE_UNKNOWN;
            }

            // Set expression type
            this.expressionType = "ARRAY:" + finalType;
        }

        @Override
        public Object execute() {
            // If type hasn't been set during validation, we need to infer it now
            if (type == null && expressionType != null && expressionType.startsWith("ARRAY:")) {
                type = expressionType.substring(6); // Remove "ARRAY:"
            }

            // If still no type and we have elements, infer from first element
            if (type == null || type.equals(ast.nodes.CoreNodes.TypeChecker.TYPE_UNKNOWN)) {
                if (!elements.isEmpty()) {
                    // Try to infer type from first element
                    ast.nodes.ExpressionNodes.ExpressionNode firstElement = elements.get(0);
                    if (firstElement instanceof ast.nodes.ExpressionNodes.LiteralNode) {
                        ast.nodes.ExpressionNodes.LiteralNode lit = (ast.nodes.ExpressionNodes.LiteralNode) firstElement;
                        type = ast.nodes.CoreNodes.TypeChecker.inferTypeFromLiteral(lit.getValue());
                    } else {
                        type = ast.nodes.CoreNodes.TypeChecker.TYPE_UNKNOWN;
                    }
                } else {
                    // Empty array - use the expected type or default to UNKNOWN
                    if (expectedType != null) {
                        type = expectedType;
                    } else {
                        type = ast.nodes.CoreNodes.TypeChecker.TYPE_UNKNOWN;
                    }
                }
            }

            ArrayCoreNodes.ArrayValue array = new ArrayCoreNodes.ArrayValue(type);

            for (ast.nodes.ExpressionNodes.ExpressionNode elementExpr : elements) {
                Object rawValue = elementExpr.execute();
                String valueStr = rawValue.toString();

                // Validate and add elements
                array.validateArrayElement(valueStr);
                array.addElement(valueStr);
            }

            return array;
        }
    }

    /**
     * Node for dynamic array creation with size
     */
    public static class DynamicArrayNode extends ast.nodes.ExpressionNodes.ExpressionNode {

        private String type;
        private ast.nodes.ExpressionNodes.ExpressionNode sizeExpr;
        private int dimensions;
        private String expectedType; // For type checking

        public DynamicArrayNode(String type, ast.nodes.ExpressionNodes.ExpressionNode sizeExpr) {
            this(type, sizeExpr, 1); // Default to 1 dimension
        }

        public DynamicArrayNode(String type, ast.nodes.ExpressionNodes.ExpressionNode sizeExpr, int dimensions) {
            this.type = type.toUpperCase();
            this.sizeExpr = sizeExpr;
            this.dimensions = dimensions;
            this.expectedType = null;
        }

        public void setExpectedType(String expectedType) {
            this.expectedType = expectedType.toUpperCase();
        }

        @Override
        public void validate(ast.nodes.CoreNodes.Scope scope) {
            clearErrors();

            // Validate size expression
            if (sizeExpr != null) {
                sizeExpr.validate(scope);
                propagateErrors(sizeExpr);

                if (!sizeExpr.getExpressionType().equals("NUMBER")) {
                    addError("Array size must be a number, got " + sizeExpr.getExpressionType());
                }
            }

            // Build array type string with dimensions
            StringBuilder arrayTypeStr = new StringBuilder();
            for (int i = 0; i < dimensions; i++) {
                arrayTypeStr.append("ARRAY:");
            }
            arrayTypeStr.append(type);

            // Check against expected type if provided
            if (expectedType != null) {
                String expectedArrayType = expectedType.startsWith("ARRAY:") ? expectedType : "ARRAY:" + expectedType;
                if (!arrayTypeStr.toString().equals(expectedArrayType)) {
                    addError("Type mismatch: expected " + expectedArrayType
                            + ", got " + arrayTypeStr.toString());
                }
            }

            this.expressionType = arrayTypeStr.toString();
        }

        @Override
        public Object execute() {
            // Calculate size
            int size;
            try {
                Object sizeObj = sizeExpr.execute();
                double doubleSize = Double.parseDouble(sizeObj.toString());
                size = (int) doubleSize;
                if (doubleSize != size || size < 0) {
                    throw new RuntimeException("Array size must be a positive integer, got " + doubleSize
                            + " at line " + this.getLineNumber());
                }
            } catch (NumberFormatException e) {
                throw new RuntimeException("Array size must be a number at line " + this.getLineNumber());
            }

            // Create the array based on dimensions
            ArrayCoreNodes.ArrayValue array;

            if (dimensions == 1) {
                // Single dimension array
                array = new ArrayCoreNodes.ArrayValue(type);

                // Initialize with default values based on type
                String defaultValue;
                switch (type) {
                    case "NUMBER":
                        defaultValue = "0";
                        break;
                    case "LETTER":
                        defaultValue = "'\\0'";
                        break;
                    case "SENTENCE":
                        defaultValue = "\"\"";
                        break;
                    case "LOGIC":
                        defaultValue = "false";
                        break;
                    default:
                        defaultValue = "null";
                }

                for (int i = 0; i < size; i++) {
                    array.addElement(defaultValue);
                }
            } else {
                // Multi-dimensional array - create a nested structure
                // You'll need to implement this based on your ArrayValue design
                // For now, create a 1D array and store dimension info separately
                array = new ArrayCoreNodes.ArrayValue(type);
                array.setDimensions(dimensions); // You'll need to add this method

                // For jagged arrays, you might need to store the first dimension size
                // and handle nested arrays later
                String defaultValue;
                switch (type) {
                    case "NUMBER":
                        defaultValue = "0";
                        break;
                    case "LETTER":
                        defaultValue = "'\\0'";
                        break;
                    case "SENTENCE":
                        defaultValue = "\"\"";
                        break;
                    case "LOGIC":
                        defaultValue = "false";
                        break;
                    default:
                        defaultValue = "null";
                }

                for (int i = 0; i < size; i++) {
                    array.addElement(defaultValue);
                }
            }

            return array;
        }

        public String getType() {
            return type;
        }

        public int getDimensions() {
            return dimensions;
        }

    }

    /**
     * Node for array assignment (arr = [1,2,3])
     */
    public static class ArrayAssignmentNode extends ast.nodes.CoreNodes.ASTNode {

        private String arrayName;
        private ast.nodes.ExpressionNodes.ExpressionNode valueExpr;

        public ArrayAssignmentNode(String arrayName, ast.nodes.ExpressionNodes.ExpressionNode valueExpr) {
            this.arrayName = arrayName;
            this.valueExpr = valueExpr;
        }

        @Override
        public void validate(ast.nodes.CoreNodes.Scope scope) {
            clearErrors();

            // Check target array exists
            if (!scope.isDeclared(arrayName)) {
                addError("Undefined array: '" + arrayName + "'");
                return;
            }

            // Check target is array type
            String targetType = scope.lookup(arrayName);
            if (!targetType.startsWith("ARRAY:")) {
                addError("Array '" + arrayName + "' is not an array");
                return;
            }

            String targetElementType = targetType.substring(6); // Remove "ARRAY:"

            // Validate source expression
            if (valueExpr != null) {
                valueExpr.validate(scope);
                propagateErrors(valueExpr);

                // Check source is array type
                if (!valueExpr.getExpressionType().startsWith("ARRAY")) {
                    addError("Cannot assign non-array value to array variable");
                } else {
                    // Check type compatibility
                    String sourceElementType = valueExpr.getExpressionType().substring(6);
                    if (!sourceElementType.equals(targetElementType)) {
                        addError("Array type mismatch: target " + targetElementType
                                + ", source " + sourceElementType);
                    }
                }
            } else {
                addError("Array assignment missing value expression");
            }

            // Mark array as initialized
            if (!hasErrors()) {
                scope.markInitialized(arrayName);
            }
        }

        @Override
        public Object execute() {
            Object value = valueExpr.execute();
            ArrayCoreNodes.ArrayValue array = null;

            if (value instanceof ArrayCoreNodes.ArrayValue) {
                array = (ArrayCoreNodes.ArrayValue) value;
            } else if (value instanceof String) {
                String potentialArrayName = (String) value;
                if (ArrayCoreNodes.isArray(potentialArrayName)) {
                    array = ArrayCoreNodes.getArray(potentialArrayName);
                }
            }

            if (array != null) {
                ArrayCoreNodes.putArray(arrayName, array);
                ast.nodes.CoreNodes.GlobalContext.symbolTable.put(arrayName,
                        "ARRAY:" + array.getType() + ":" + arrayName);
            } else {
                throw new RuntimeException("Cannot assign non-array value to array variable: " + arrayName);
            }
            return null;
        }
    }

    /**
     * Node for multi-dimensional dynamic array creation with sizes Example: NEW
     * NUMBER[3][4] or NEW NUMBER[3][]
     */
    public static class MultiDimensionalArrayNode extends ast.nodes.ExpressionNodes.ExpressionNode {

        private String type;
        private List<ast.nodes.ExpressionNodes.ExpressionNode> sizeExpressions;
        private int dimensions;
        private String expectedType;

        public MultiDimensionalArrayNode(String type, List<ast.nodes.ExpressionNodes.ExpressionNode> sizeExpressions, int dimensions) {
            this.type = type.toUpperCase();
            this.sizeExpressions = sizeExpressions;
            this.dimensions = dimensions;
            this.expectedType = null;
        }

        public void setExpectedType(String expectedType) {
            this.expectedType = expectedType.toUpperCase();
        }

        @Override
        public void validate(ast.nodes.CoreNodes.Scope scope) {
            clearErrors();

            // Validate each size expression that exists
            for (int i = 0; i < sizeExpressions.size(); i++) {
                ast.nodes.ExpressionNodes.ExpressionNode sizeExpr = sizeExpressions.get(i);
                if (sizeExpr != null) {
                    sizeExpr.validate(scope);
                    propagateErrors(sizeExpr);

                    if (!sizeExpr.getExpressionType().equals("NUMBER")) {
                        addError("Array size for dimension " + (i + 1) + " must be a number, got " + sizeExpr.getExpressionType());
                    }
                }
                // null size expression means jagged dimension ([]) - this is valid
            }

            // Build array type string with dimensions
            StringBuilder arrayTypeStr = new StringBuilder();
            for (int i = 0; i < dimensions; i++) {
                arrayTypeStr.append("ARRAY:");
            }
            arrayTypeStr.append(type);

            // Check against expected type if provided
            if (expectedType != null) {
                String expectedArrayType = expectedType.startsWith("ARRAY:") ? expectedType : "ARRAY:" + expectedType;
                if (!arrayTypeStr.toString().equals(expectedArrayType)) {
                    addError("Type mismatch: expected " + expectedArrayType
                            + ", got " + arrayTypeStr.toString());
                }
            }

            this.expressionType = arrayTypeStr.toString();
        }

        @Override
        public Object execute() {
            List<Integer> evaluatedSizes = new ArrayList<>();
            for (ast.nodes.ExpressionNodes.ExpressionNode expr : sizeExpressions) {
                if (expr == null) break;
                Object sizeObj = expr.execute();
                double doubleSize = Double.parseDouble(sizeObj.toString());
                int size = (int) doubleSize;
                if (doubleSize != size || size < 0) {
                    throw new RuntimeException("Array size must be a positive integer, got " + doubleSize);
                }
                evaluatedSizes.add(size);
            }

            if (evaluatedSizes.isEmpty()) {
                throw new RuntimeException("First dimension size is required for multi-dimensional array");
            }

            return createArrayRecursive(0, evaluatedSizes);
        }

        private ArrayCoreNodes.ArrayValue createArrayRecursive(int level, List<Integer> sizes) {
            ArrayCoreNodes.ArrayValue array = new ArrayCoreNodes.ArrayValue(type);
            if (level == 0) array.setDimensions(dimensions);

            if (level >= sizes.size()) {
                 return array;
            }

            int currentSize = sizes.get(level);
            boolean isLastEvaluatedLevel = (level == sizes.size() - 1);

            if (isLastEvaluatedLevel) {
                String defaultValue;
                switch (type) {
                    case "NUMBER": defaultValue = "0"; break;
                    case "LETTER": defaultValue = "'\\0'"; break;
                    case "SENTENCE": defaultValue = "\"\""; break;
                    case "LOGIC": defaultValue = "false"; break;
                    default: defaultValue = "null";
                }
                for (int i = 0; i < currentSize; i++) {
                    array.addElement(defaultValue);
                }
            } else {
                for (int i = 0; i < currentSize; i++) {
                    ArrayCoreNodes.ArrayValue subArray = createArrayRecursive(level + 1, sizes);
                    String subArrayName = ArrayCoreNodes.generateNestedArrayName("dynamic");
                    ArrayCoreNodes.putArray(subArrayName, subArray);
                    ast.nodes.CoreNodes.GlobalContext.symbolTable.put(subArrayName,
                            "ARRAY:" + subArray.getType() + ":" + subArrayName);
                    
                    array.addElement(subArrayName);
                }
            }

            return array;
        }

        public String getType() {
            return type;
        }

        public int getDimensions() {
            return dimensions;
        }
    }

}
