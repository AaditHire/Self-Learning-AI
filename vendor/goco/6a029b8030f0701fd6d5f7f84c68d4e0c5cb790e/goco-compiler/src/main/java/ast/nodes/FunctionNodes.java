package ast.nodes;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import utils.Debug;

public class FunctionNodes {

    /**
     * Represents a single function parameter with optional default value.
     */
    public static class FunctionParameter {
        private String type;
        private String name;
        private ExpressionNodes.ExpressionNode defaultValue; // null if no default

        public FunctionParameter(String type, String name, ExpressionNodes.ExpressionNode defaultValue) {
            this.type = type.toUpperCase();
            this.name = name;
            this.defaultValue = defaultValue;
        }

        public String getType() { return type; }
        public String getName() { return name; }
        public ExpressionNodes.ExpressionNode getDefaultValue() { return defaultValue; }
        public boolean hasDefault() { return defaultValue != null; }
    }

    /**
     * Exception thrown by RETURN statements to unwind the call stack.
     */
    public static class ReturnException extends RuntimeException {
        private Object value;

        public ReturnException(Object value) {
            super("Return executed");
            this.value = value;
        }

        public Object getValue() { return value; }
    }

    /**
     * Function declaration node.
     * Syntax: FUNCTION name(params) { body }. OR FUNCTION name(params) { body } RETURNS TYPE.
     */
    public static class FunctionDeclarationNode extends CoreNodes.ASTNode {
        private String name;
        private List<FunctionParameter> parameters;
        private List<CoreNodes.ASTNode> body;
        private String returnType; // null means void

        public FunctionDeclarationNode(String name, List<FunctionParameter> parameters,
                                        List<CoreNodes.ASTNode> body, String returnType) {
            super();
            this.name = name;
            this.parameters = parameters;
            this.body = body;
            this.returnType = returnType;
        }

        @Override
        public void validate(CoreNodes.Scope scope) {
            clearErrors();

            // Check for duplicate function name
            if (CoreNodes.GlobalContext.functionTable.containsKey(name)) {
                addError("Function '" + name + "' is already declared");
                return;
            }

            // Validate parameter list
            // - no duplicate param names
            // - defaults must come after non-defaults
            boolean seenDefault = false;
            java.util.Set<String> paramNames = new java.util.HashSet<>();
            for (FunctionParameter param : parameters) {
                if (paramNames.contains(param.getName())) {
                    addError("Duplicate parameter name '" + param.getName() + "' in function '" + name + "'");
                }
                paramNames.add(param.getName());

                if (param.hasDefault()) {
                    seenDefault = true;
                } else if (seenDefault) {
                    addError("Non-default parameter '" + param.getName() +
                             "' follows default parameter in function '" + name + "'");
                }

                // Validate parameter type
                if (!CoreNodes.TypeChecker.isValidType(param.getType())) {
                    addError("Invalid parameter type '" + param.getType() + "' in function '" + name + "'");
                }

                // Validate default value expression if present
                if (param.hasDefault()) {
                    param.getDefaultValue().validate(scope);
                    propagateErrors(param.getDefaultValue());
                }
            }

            // Validate return type if specified
            if (returnType != null && !CoreNodes.TypeChecker.isValidType(returnType)) {
                addError("Invalid return type '" + returnType + "' for function '" + name + "'");
            }

            // Create function scope for body validation
            CoreNodes.Scope functionScope = scope.enterScope("function");

            // Declare parameters in function scope
            for (FunctionParameter param : parameters) {
                if (!functionScope.declareAndInitialize(param.getName(), param.getType())) {
                    addError("Cannot declare parameter '" + param.getName() + "' in function '" + name + "'");
                }
            }

            // Validate body statements
            for (CoreNodes.ASTNode statement : body) {
                if (statement != null) {
                    statement.validate(functionScope);
                    propagateErrors(statement);
                }
            }

            // Register function in scope for recursive calls / forward declarations
            if (!hasErrors()) {
                CoreNodes.GlobalContext.functionTable.put(name, this);
            }
        }

        @Override
        public Object execute() {
            // Register function in the function table at execution time
            CoreNodes.GlobalContext.functionTable.put(name, this);
            Debug.logln("DEBUG: Registered function: " + name);
            return null;
        }

        /**
         * Execute the function body with the given argument values.
         */
        public Object call(List<Object> argValues) {
            // Save current symbol table state for parameters
            Map<String, String> savedValues = new HashMap<>();
            for (FunctionParameter param : parameters) {
                if (CoreNodes.GlobalContext.symbolTable.containsKey(param.getName())) {
                    savedValues.put(param.getName(), CoreNodes.GlobalContext.symbolTable.get(param.getName()));
                }
            }

            try {
                // Bind arguments to parameters
                for (int i = 0; i < parameters.size(); i++) {
                    FunctionParameter param = parameters.get(i);
                    String value;

                    if (i < argValues.size()) {
                        // Argument provided
                        value = argValues.get(i).toString();
                    } else if (param.hasDefault()) {
                        // Use default value
                        value = param.getDefaultValue().execute().toString();
                    } else {
                        throw new RuntimeException("Missing argument for parameter '" + param.getName() +
                                                   "' in function '" + name + "'");
                    }

                    CoreNodes.GlobalContext.symbolTable.put(param.getName(), value);
                }

                // Execute body
                for (CoreNodes.ASTNode statement : body) {
                    statement.execute();
                }

                // If we get here without a ReturnException, return null (void)
                return null;

            } catch (ReturnException e) {
                return e.getValue();
            } finally {
                // Restore saved parameter values or remove them
                for (FunctionParameter param : parameters) {
                    if (savedValues.containsKey(param.getName())) {
                        CoreNodes.GlobalContext.symbolTable.put(param.getName(), savedValues.get(param.getName()));
                    } else {
                        CoreNodes.GlobalContext.symbolTable.remove(param.getName());
                    }
                }
            }
        }

        // Getters
        public String getName() { return name; }
        public List<FunctionParameter> getParameters() { return parameters; }
        public List<CoreNodes.ASTNode> getBody() { return body; }
        public String getReturnType() { return returnType; }
        public int getRequiredParamCount() {
            int count = 0;
            for (FunctionParameter p : parameters) {
                if (!p.hasDefault()) count++;
            }
            return count;
        }
    }

    /**
     * Function call expression node - can be used wherever an expression is expected.
     */
    public static class FunctionCallNode extends ExpressionNodes.ExpressionNode {
        private String functionName;
        private List<ExpressionNodes.ExpressionNode> arguments;

        public FunctionCallNode(String functionName, List<ExpressionNodes.ExpressionNode> arguments) {
            super();
            this.functionName = functionName;
            this.arguments = arguments;
        }

        @Override
        public void validate(CoreNodes.Scope scope) {
            clearErrors();

            // Check function exists
            FunctionDeclarationNode func = CoreNodes.GlobalContext.functionTable.get(functionName);
            if (func == null) {
                addError("Undefined function: '" + functionName + "'");
                this.expressionType = CoreNodes.TypeChecker.TYPE_UNKNOWN;
                return;
            }

            // Validate argument count
            int minArgs = func.getRequiredParamCount();
            int maxArgs = func.getParameters().size();
            if (arguments.size() < minArgs) {
                addError("Function '" + functionName + "' requires at least " + minArgs +
                         " argument(s) but got " + arguments.size());
            } else if (arguments.size() > maxArgs) {
                addError("Function '" + functionName + "' accepts at most " + maxArgs +
                         " argument(s) but got " + arguments.size());
            }

            // Validate argument expressions
            for (ExpressionNodes.ExpressionNode arg : arguments) {
                arg.validate(scope);
                propagateErrors(arg);
            }

            // Set expression type from function's return type
            if (func.getReturnType() != null) {
                this.expressionType = CoreNodes.TypeChecker.normalizeType(func.getReturnType());
            } else {
                this.expressionType = CoreNodes.TypeChecker.TYPE_VOID;
            }
        }

        @Override
        public Object execute() {
            FunctionDeclarationNode func = CoreNodes.GlobalContext.functionTable.get(functionName);
            if (func == null) {
                throw new RuntimeException("Undefined function: " + functionName);
            }

            // Evaluate arguments
            List<Object> argValues = new ArrayList<>();
            for (ExpressionNodes.ExpressionNode arg : arguments) {
                argValues.add(arg.execute());
            }

            // Call the function
            return func.call(argValues);
        }

        // Getters
        public String getFunctionName() { return functionName; }
        public List<ExpressionNodes.ExpressionNode> getArguments() { return arguments; }
    }

    /**
     * Function call as a standalone statement (result is discarded).
     */
    public static class FunctionCallStatementNode extends CoreNodes.ASTNode {
        private FunctionCallNode callNode;

        public FunctionCallStatementNode(FunctionCallNode callNode) {
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

        public FunctionCallNode getCallNode() { return callNode; }
    }

    /**
     * RETURN statement node.
     */
    public static class ReturnNode extends CoreNodes.ASTNode {
        private ExpressionNodes.ExpressionNode expression; // null for void return

        public ReturnNode(ExpressionNodes.ExpressionNode expression) {
            super();
            this.expression = expression;
        }

        @Override
        public void validate(CoreNodes.Scope scope) {
            clearErrors();

            // Check we're inside a function
            if (!scope.isInFunction()) {
                addError("RETURN statement must be inside a function");
                return;
            }

            // Validate expression if present
            if (expression != null) {
                expression.validate(scope);
                propagateErrors(expression);
            }
        }

        @Override
        public Object execute() {
            Object value = null;
            if (expression != null) {
                value = expression.execute();
            }
            throw new ReturnException(value);
        }

        public ExpressionNodes.ExpressionNode getExpression() { return expression; }
    }
}
