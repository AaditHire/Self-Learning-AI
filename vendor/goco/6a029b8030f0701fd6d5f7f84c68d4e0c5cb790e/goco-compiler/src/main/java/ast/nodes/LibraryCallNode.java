package ast.nodes;

import java.util.ArrayList;
import java.util.List;
import ast.math.MathLibrary;
import ast.strings.StringsLibrary;
import ast.arrays.ArraysLibrary;

/**
 * AST nodes for library-qualified calls and variable access.
 * Handles: math.POW(2, 3), strings.UPPER("hello"), arrays.LENGTH(arr), math.PI
 */
public class LibraryCallNode {

    /**
     * Library function call used as an expression (returns a value).
     * Example: NUMBER x = math.POW(2, 3).
     */
    public static class LibraryCallExpressionNode extends ExpressionNodes.ExpressionNode {

        private String libraryName;
        private String functionName;
        private List<ExpressionNodes.ExpressionNode> arguments;

        public LibraryCallExpressionNode(String libraryName, String functionName,
                List<ExpressionNodes.ExpressionNode> arguments) {
            super();
            this.libraryName = libraryName.toLowerCase();
            this.functionName = functionName.toUpperCase();
            this.arguments = arguments;
        }

        @Override
        public void validate(CoreNodes.Scope scope) {
            clearErrors();

            // Check library is imported
            if (!CoreNodes.GlobalContext.importedLibraries.contains(libraryName)) {
                addError("Library '" + libraryName + "' is not imported. Add 'IMPORT " + libraryName + ".' at the top of your program");
                this.expressionType = CoreNodes.TypeChecker.TYPE_UNKNOWN;
                return;
            }

            // Validate arguments
            for (ExpressionNodes.ExpressionNode arg : arguments) {
                arg.validate(scope);
                propagateErrors(arg);
            }

            // Validate function exists and arg count matches, set return type
            switch (libraryName) {
                case "math":
                    validateMathCall(scope);
                    break;
                case "strings":
                    validateStringsCall(scope);
                    break;
                case "arrays":
                    validateArraysCall(scope);
                    break;
                default:
                    addError("Unknown library: '" + libraryName + "'");
                    this.expressionType = CoreNodes.TypeChecker.TYPE_UNKNOWN;
            }
        }

        private void validateMathCall(CoreNodes.Scope scope) {
            int expectedArgs = MathLibrary.getParamCount(functionName);
            if (expectedArgs < 0) {
                addError("Unknown math function: '" + functionName + "'");
                this.expressionType = CoreNodes.TypeChecker.TYPE_UNKNOWN;
                return;
            }
            if (arguments.size() != expectedArgs) {
                addError("math." + functionName + " expects " + expectedArgs + " argument(s) but got " + arguments.size());
            }
            this.expressionType = MathLibrary.getReturnType(functionName);
        }

        private void validateStringsCall(CoreNodes.Scope scope) {
            int expectedArgs = StringsLibrary.getParamCount(functionName);
            if (expectedArgs < 0) {
                addError("Unknown strings function: '" + functionName + "'");
                this.expressionType = CoreNodes.TypeChecker.TYPE_UNKNOWN;
                return;
            }
            if (arguments.size() != expectedArgs) {
                addError("strings." + functionName + " expects " + expectedArgs + " argument(s) but got " + arguments.size());
            }
            this.expressionType = StringsLibrary.getReturnType(functionName);
        }

        private void validateArraysCall(CoreNodes.Scope scope) {
            int expectedArgs = ArraysLibrary.getParamCount(functionName);
            if (expectedArgs < 0) {
                addError("Unknown arrays function: '" + functionName + "'");
                this.expressionType = CoreNodes.TypeChecker.TYPE_UNKNOWN;
                return;
            }
            if (arguments.size() != expectedArgs) {
                addError("arrays." + functionName + " expects " + expectedArgs + " argument(s) but got " + arguments.size());
            }
            // Attempt to infer specific return types based on arguments
            String inferredType = ArraysLibrary.getReturnType(functionName);
            if (!arguments.isEmpty()) {
                String firstArgType = arguments.get(0).getExpressionType();
                if (firstArgType != null && firstArgType.startsWith("ARRAY:")) {
                    if (functionName.equals("CONCAT") || functionName.equals("SLICE")) {
                        // Return type is the same array type
                        inferredType = firstArgType;
                    } else if (functionName.equals("POP")) {
                        // Return type is the element type
                        inferredType = firstArgType.substring(6); // remove "ARRAY:"
                    }
                }
            }
            this.expressionType = inferredType;
        }

        @Override
        public Object execute() {
            // Evaluate arguments
            List<Object> argValues = new ArrayList<>();
            for (ExpressionNodes.ExpressionNode arg : arguments) {
                argValues.add(arg.execute());
            }

            Object result;
            switch (libraryName) {
                case "math":
                    result = MathLibrary.call(functionName, argValues);
                    break;
                case "strings":
                    result = StringsLibrary.call(functionName, argValues);
                    break;
                case "arrays":
                    result = ArraysLibrary.call(functionName, argValues);
                    break;
                default:
                    throw new RuntimeException("Unknown library: " + libraryName);
            }

            if (result instanceof String && this.expressionType != null && this.expressionType.equals(CoreNodes.TypeChecker.TYPE_NUMBER)) {
                try {
                    return Double.parseDouble((String) result);
                } catch (NumberFormatException e) {
                    // Ignore, return original result
                }
            }

            return result;
        }

        public String getLibraryName() { return libraryName; }
        public String getFunctionName() { return functionName; }
        public List<ExpressionNodes.ExpressionNode> getArguments() { return arguments; }
    }

    /**
     * Library function call used as a statement (void calls).
     * Example: arrays.PUSH(arr, 5).
     */
    public static class LibraryCallStatementNode extends CoreNodes.ASTNode {

        private LibraryCallExpressionNode callNode;

        public LibraryCallStatementNode(LibraryCallExpressionNode callNode) {
            super();
            this.callNode = callNode;
        }

        @Override
        public void validate(CoreNodes.Scope scope) {
            clearErrors();
            callNode.validate(scope);
            propagateErrors(callNode);
        }

        @Override
        public Object execute() {
            callNode.execute(); // discard return value
            return null;
        }

        public LibraryCallExpressionNode getCallNode() { return callNode; }
    }

    /**
     * Library variable/constant access.
     * Example: math.PI, math.E
     */
    public static class LibraryVariableNode extends ExpressionNodes.ExpressionNode {

        private String libraryName;
        private String variableName;

        public LibraryVariableNode(String libraryName, String variableName) {
            super();
            this.libraryName = libraryName.toLowerCase();
            this.variableName = variableName.toUpperCase();
        }

        @Override
        public void validate(CoreNodes.Scope scope) {
            clearErrors();

            // Check library is imported
            if (!CoreNodes.GlobalContext.importedLibraries.contains(libraryName)) {
                addError("Library '" + libraryName + "' is not imported. Add 'IMPORT " + libraryName + ".' at the top of your program");
                this.expressionType = CoreNodes.TypeChecker.TYPE_UNKNOWN;
                return;
            }

            // Validate variable exists
            switch (libraryName) {
                case "math":
                    if (!MathLibrary.hasConstant(variableName)) {
                        addError("Unknown math constant: '" + variableName + "'");
                        this.expressionType = CoreNodes.TypeChecker.TYPE_UNKNOWN;
                    } else {
                        this.expressionType = CoreNodes.TypeChecker.TYPE_NUMBER;
                    }
                    break;
                default:
                    addError("Library '" + libraryName + "' does not have accessible variables");
                    this.expressionType = CoreNodes.TypeChecker.TYPE_UNKNOWN;
            }
        }

        @Override
        public Object execute() {
            switch (libraryName) {
                case "math":
                    return MathLibrary.getConstant(variableName);
                default:
                    throw new RuntimeException("Library '" + libraryName + "' does not have variables");
            }
        }

        public String getLibraryName() { return libraryName; }
        public String getVariableName() { return variableName; }
    }
}
