package ast.nodes;

/**
 * AST Node for IMPORT statement.
 * Syntax: IMPORT math. / IMPORT strings. / IMPORT arrays.
 */
public class ImportNode extends CoreNodes.ASTNode {

    private String libraryName;

    // Valid library names
    private static final String[] VALID_LIBRARIES = {"math", "strings", "arrays"};

    public ImportNode(String libraryName) {
        super();
        this.libraryName = libraryName.toLowerCase();
    }

    @Override
    public void validate(CoreNodes.Scope scope) {
        clearErrors();

        // Check if library name is valid
        boolean valid = false;
        for (String lib : VALID_LIBRARIES) {
            if (lib.equals(libraryName)) {
                valid = true;
                break;
            }
        }

        if (!valid) {
            addError("Unknown library: '" + libraryName + "'. Valid libraries are: math, strings, arrays");
            return;
        }

        // Check for duplicate imports
        if (CoreNodes.GlobalContext.importedLibraries.contains(libraryName)) {
            addError("Library '" + libraryName + "' is already imported");
            return;
        }

        // Register the import at validation time
        CoreNodes.GlobalContext.importedLibraries.add(libraryName);
    }

    @Override
    public Object execute() {
        // Register the import at execution time (in case validation was skipped)
        CoreNodes.GlobalContext.importedLibraries.add(libraryName);
        return null;
    }

    public String getLibraryName() {
        return libraryName;
    }
}
