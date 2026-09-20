package ast.nodes;

import ast.nodes.CoreNodes.Scope;
import java.io.*;
import java.util.*;
import utils.Debug;

public class IONodes {

    public abstract static class BaseDisplayNode extends CoreNodes.ASTNode {

        protected Object value;
        protected boolean isProcessed;

        public BaseDisplayNode(ExpressionNodes.ExpressionNode expr) {
            this.value = expr;
            this.isProcessed = false;
        }

        public BaseDisplayNode(String value, boolean isProcessed) {
            this.value = value;
            this.isProcessed = isProcessed;
        }

        protected String displayResult(Object result) {
            if (result == null) {
                return "";
            }

            String str = result.toString();

            // Format plain integer numbers as doubles (e.g. "10" -> "10.0")
            if (str.matches("-?\\d+")) {
                try {
                    str = Double.toString(Double.parseDouble(str));
                } catch (NumberFormatException e) {
                    // leave str unchanged
                }
            }

            // Handle character literals - they should be displayed without quotes
            if (str.length() == 1) {
                return str;
            }

            // Remove outer quotes if present and if the string is long enough
            if (str.length() >= 2) {
                if ((str.startsWith("\"") && str.endsWith("\""))
                        || (str.startsWith("'") && str.endsWith("'"))) {
                    return str.substring(1, str.length() - 1);
                }
            }

            return str;
        }

        protected abstract void display(String value);
    }

    public static class DisplayNode extends BaseDisplayNode {

        public DisplayNode(ExpressionNodes.ExpressionNode expr) {
            super(expr);
        }

        public DisplayNode(String value, boolean isProcessed) {
            super(value, isProcessed);
        }

        @Override
        public void validate(Scope scope) {
            clearErrors();
            if (value instanceof ExpressionNodes.ExpressionNode) {
                ((ExpressionNodes.ExpressionNode) value).validate(scope);
                propagateErrors((ExpressionNodes.ExpressionNode) value);
            }
        }

        @Override
        public Object execute() {
            Object result;
            if (value instanceof ExpressionNodes.ExpressionNode) {
                result = ((ExpressionNodes.ExpressionNode) value).execute();
            } else {
                result = value;
            }

            String displayStr = displayResult(result);
            display(displayStr);
            return null;
        }

        @Override
        protected void display(String value) {
            System.out.print(value);
        }
    }

    public static class DisplayNLNode extends BaseDisplayNode {

        public DisplayNLNode(ExpressionNodes.ExpressionNode expr) {
            super(expr);
        }

        public DisplayNLNode(String value, boolean isProcessed) {
            super(value, isProcessed);
        }

        @Override
        public void validate(Scope scope) {
            clearErrors();
            if (value instanceof ExpressionNodes.ExpressionNode) {
                ((ExpressionNodes.ExpressionNode) value).validate(scope);
                propagateErrors((ExpressionNodes.ExpressionNode) value);
            }
        }

        @Override
        public Object execute() {
            Object result;
            if (value instanceof ExpressionNodes.ExpressionNode) {
                result = ((ExpressionNodes.ExpressionNode) value).execute();
            } else {
                result = value;
            }

            String displayStr = displayResult(result);
            display(displayStr);
            return null;
        }

        @Override
        protected void display(String value) {
            System.out.println(value);
        }
    }

    // Multi display node
    public static class MultiDisplayNode extends CoreNodes.ASTNode {

        private List<Object> items;

        public MultiDisplayNode(List<Object> items) {
            super();
            this.items = new ArrayList<>(items);
        }

        @Override
        public void validate(CoreNodes.Scope scope) {
            clearErrors();

            if (items == null || items.isEmpty()) {
                addError("Multi-display statement has no items to display");
                return;
            }

            for (Object item : items) {
                if (item instanceof ExpressionNodes.ExpressionNode) {
                    // Validate expression
                    ExpressionNodes.ExpressionNode expr = (ExpressionNodes.ExpressionNode) item;
                    expr.validate(scope);
                    propagateErrors(expr);
                } else if (item instanceof String) {
                    String str = (String) item;

                    // Check if it's a quoted literal or a variable reference
                    if (isQuotedLiteral(str)) {
                        // Validate literal format
                        validateStringLiteral(str);
                    } else {
                        // It's a variable reference - validate variable exists
                        if (!scope.isDeclared(str)) {
                            addError("Undefined variable in multi-display: '" + str + "'");
                        } else if (!scope.isInitialized(str)) {
                            addError("Variable '" + str + "' used before initialization" + " at line " + this.getLineNumber());
                        }
                    }
                }
            }
        }

        /**
         * Check if string is a quoted literal
         */
        private boolean isQuotedLiteral(String str) {
            return (str.startsWith("\"") && str.endsWith("\""))
                    || (str.startsWith("'") && str.endsWith("'"));
        }

        /**
         * Validate string literal format
         */
        private void validateStringLiteral(String literal) {
            if (literal == null) {
                return;
            }

            if (literal.startsWith("'") && !literal.endsWith("'")) {
                addError("Mismatched single quotes in display literal: '" + literal + "'");
            } else if (literal.startsWith("\"") && !literal.endsWith("\"")) {
                addError("Mismatched double quotes in display literal: '" + literal + "'");
            }

            // Validate character literal length
            if (literal.startsWith("'") && literal.endsWith("'") && literal.length() != 3) {
                addError("Character literal must contain exactly one character: '" + literal + "'");
            }
        }

        @Override
        public Object execute() {
            if (!CoreNodes.GlobalContext.shouldExecute()) {
                return null;
            }

            StringBuilder output = new StringBuilder();
            for (int i = 0; i < items.size(); i++) {
                Object item = items.get(i);
                if (item instanceof ExpressionNodes.ExpressionNode) {
                    Object value = ((ExpressionNodes.ExpressionNode) item).execute();
                    output.append(value);
                } else if (item instanceof String) {
                    String str = (String) item;

                    // If it's a string literal, remove the quotes
                    // Check if it's an array variable
                    if (ast.arrays.ArrayCoreNodes.isArray(str)) {
                        output.append(ast.arrays.ArrayCoreNodes.formatArrayForDisplay(str));
                    } else if (CoreNodes.GlobalContext.symbolTable.containsKey(str)) {
                        // It's a variable
                        String value = CoreNodes.GlobalContext.symbolTable.get(str);

                        // Check if it's an array reference in the symbol table
                        if (value != null && value.startsWith("ARRAY:")) {
                            output.append(ast.arrays.ArrayCoreNodes.formatArrayForDisplay(value.substring(6)));
                        } else {
                            output.append(value != null ? CoreNodes.GlobalContext.getVariableValue(str) : "null");
                        }
                    } else if (str.startsWith("\"") && str.endsWith("\"")) {
                        output.append(str.substring(1, str.length() - 1));
                    } else if (str.startsWith("'") && str.endsWith("'")) {
                        output.append(str.substring(1, str.length() - 1));
                    } else {
                        output.append(str);
                    }
                }
            }
            Debug.print(output.toString());
            return null;
        }

        // Getter for testing
        public List<Object> getItems() {
            return new ArrayList<>(items);
        }
    }

    // Multi display with newline node
    public static class MultiDisplayNLNode extends CoreNodes.ASTNode {

        private List<Object> items;

        public MultiDisplayNLNode(List<Object> items) {
            super();
            this.items = new ArrayList<>(items);
        }

        @Override
        public void validate(CoreNodes.Scope scope) {
            clearErrors();

            if (items == null || items.isEmpty()) {
                addError("Multi-display statement has no items to display");
                return;
            }

            for (Object item : items) {
                if (item instanceof ExpressionNodes.ExpressionNode) {
                    // Validate expression
                    ExpressionNodes.ExpressionNode expr = (ExpressionNodes.ExpressionNode) item;
                    expr.validate(scope);
                    propagateErrors(expr);
                } else if (item instanceof String) {
                    String str = (String) item;

                    // Check if it's a quoted literal or a variable reference
                    if (isQuotedLiteral(str)) {
                        // Validate literal format
                        validateStringLiteral(str);
                    } else {
                        // It's a variable reference - validate variable exists
                        if (!scope.isDeclared(str)) {
                            addError("Undefined variable in multi-display: '" + str + "'");
                        } else if (!scope.isInitialized(str)) {
                            addError("Variable '" + str + "' used before initialization" + " at line " + this.getLineNumber());
                        }
                    }
                }
            }
        }

        /**
         * Check if string is a quoted literal
         */
        private boolean isQuotedLiteral(String str) {
            return (str.startsWith("\"") && str.endsWith("\""))
                    || (str.startsWith("'") && str.endsWith("'"));
        }

        /**
         * Validate string literal format
         */
        private void validateStringLiteral(String literal) {
            if (literal == null) {
                return;
            }

            if (literal.startsWith("'") && !literal.endsWith("'")) {
                addError("Mismatched single quotes in display literal: '" + literal + "'");
            } else if (literal.startsWith("\"") && !literal.endsWith("\"")) {
                addError("Mismatched double quotes in display literal: '" + literal + "'");
            }

            // Validate character literal length
            if (literal.startsWith("'") && literal.endsWith("'") && literal.length() != 3) {
                addError("Character literal must contain exactly one character: '" + literal + "'");
            }
        }

        @Override
        public Object execute() {
            if (!CoreNodes.GlobalContext.shouldExecute()) {
                return null;
            }

            StringBuilder output = new StringBuilder();
            for (int i = 0; i < items.size(); i++) {
                Object item = items.get(i);
                if (item instanceof ExpressionNodes.ExpressionNode) {
                    Object value = ((ExpressionNodes.ExpressionNode) item).execute();
                    output.append(value);
                } else if (item instanceof String) {
                    String str = (String) item;

                    // If it's a string literal, remove the quotes
                    if (ast.arrays.ArrayCoreNodes.isArray(str)) {
                        output.append(ast.arrays.ArrayCoreNodes.formatArrayForDisplay(str));
                    } else if (CoreNodes.GlobalContext.symbolTable.containsKey(str)) {
                        // It's a variable
                        String value = CoreNodes.GlobalContext.symbolTable.get(str);

                        // Check if it's an array reference in the symbol table
                        if (value != null && value.startsWith("ARRAY:")) {
                            output.append(ast.arrays.ArrayCoreNodes.formatArrayForDisplay(value.substring(6)));
                        } else {
                            output.append(value != null ? CoreNodes.GlobalContext.getVariableValue(str) : "null");
                        }
                    } else if (str.startsWith("\"") && str.endsWith("\"")) {
                        output.append(str.substring(1, str.length() - 1));
                    } else if (str.startsWith("'") && str.endsWith("'")) {
                        output.append(str.substring(1, str.length() - 1));
                    } else {
                        output.append(str);
                    }
                }
            }
            Debug.println(output.toString());
            return null;
        }

        // Getter for testing
        public List<Object> getItems() {
            return new ArrayList<>(items);
        }
    }

    // Input statement node
    public static class InputNode extends CoreNodes.ASTNode {

        private String varName;

        public InputNode(String varName) {
            super();
            this.varName = varName;
        }

        @Override
        public void validate(CoreNodes.Scope scope) {
            clearErrors();

            // Check variable exists
            if (!scope.isDeclared(varName)) {
                addError("Undefined variable in input: '" + varName + "'");
                return;
            }

            // Get variable type for input validation
            String varType = scope.lookup(varName);

            // Note: Type-specific input validation happens at runtime
            // LETTER type can only accept single character input
            // NUMBER type requires numeric input
            // SENTENCE accepts any string
            // LOGIC accepts boolean values
            // Mark variable as will-be-initialized (since input will assign to it)
            scope.markInitialized(varName);
        }

        @Override
        public Object execute() {
            if (!CoreNodes.GlobalContext.symbolTable.containsKey(varName)) {
                throw new RuntimeException("Undefined variable: " + varName);
            }

            BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
            try {
                // MUST use System.out directly (not Debug.log) so the IDE can detect the prompt
                System.out.print("Enter value for " + varName + ": ");
                System.out.flush(); // Force flush — critical when stdout is piped
                String userInput = reader.readLine();

                // readLine() returns null when stdin is closed/EOF
                if (userInput == null) {
                    throw new RuntimeException("No input received for variable '" + varName + "'");
                }

                String currentValue = CoreNodes.GlobalContext.symbolTable.get(varName);
                // Guard against null (uninitialized variable)
                if (currentValue == null) {
                    currentValue = "";
                }
                boolean isNumber = currentValue.matches("-?\\d+(\\.\\d+)?");
                boolean isLetter = currentValue.startsWith("'") && currentValue.endsWith("'");

                if (isNumber) {
                    try {
                        Double.parseDouble(userInput);
                        CoreNodes.GlobalContext.symbolTable.put(varName, userInput);
                    } catch (NumberFormatException e) {
                        Debug.errln("Error: Numeric input required for NUMBER variable '" + varName + "'.");
                    }
                } else if (isLetter) {
                    if (userInput.length() != 1) {
                        Debug.errln("LETTER input must be a single character.");
                    } else {
                        CoreNodes.GlobalContext.symbolTable.put(varName, "'" + userInput + "'");
                    }
                } else {
                    CoreNodes.GlobalContext.symbolTable.put(varName, "\"" + userInput + "\"");
                }
            } catch (IOException e) {
                Debug.errln("Error: Failed to read input.");
            }
            return null;
        }

        // Getter for testing
        public String getVarName() {
            return varName;
        }
    }

}
