package ast.strings;

import java.util.*;
import ast.nodes.CoreNodes;
import ast.arrays.ArrayCoreNodes;

/**
 * Strings library for GOCO language.
 * Provides string manipulation functions.
 * Used via: IMPORT strings. then strings.UPPER("hello"), strings.LENGTH(s), etc.
 */
public class StringsLibrary {

    // ==================== Function Metadata ====================

    private static final Map<String, Integer> PARAM_COUNTS = new HashMap<>();
    private static final Map<String, String> RETURN_TYPES = new HashMap<>();

    static {
        // 1-arg functions
        PARAM_COUNTS.put("LENGTH", 1);     RETURN_TYPES.put("LENGTH", "NUMBER");
        PARAM_COUNTS.put("UPPER", 1);      RETURN_TYPES.put("UPPER", "SENTENCE");
        PARAM_COUNTS.put("LOWER", 1);      RETURN_TYPES.put("LOWER", "SENTENCE");
        PARAM_COUNTS.put("REVERSE", 1);    RETURN_TYPES.put("REVERSE", "SENTENCE");
        PARAM_COUNTS.put("TO_NUMBER", 1);  RETURN_TYPES.put("TO_NUMBER", "NUMBER");
        PARAM_COUNTS.put("TO_SENTENCE", 1); RETURN_TYPES.put("TO_SENTENCE", "SENTENCE");

        // 2-arg functions
        PARAM_COUNTS.put("EQUALS", 2);     RETURN_TYPES.put("EQUALS", "LOGIC");
        PARAM_COUNTS.put("STARTSWITH", 2); RETURN_TYPES.put("STARTSWITH", "LOGIC");
        PARAM_COUNTS.put("ENDSWITH", 2);   RETURN_TYPES.put("ENDSWITH", "LOGIC");
        PARAM_COUNTS.put("CONTAINS", 2);   RETURN_TYPES.put("CONTAINS", "LOGIC");
        PARAM_COUNTS.put("FIND", 2);       RETURN_TYPES.put("FIND", "NUMBER");
        PARAM_COUNTS.put("COUNT", 2);      RETURN_TYPES.put("COUNT", "NUMBER");
        PARAM_COUNTS.put("CHARAT", 2);     RETURN_TYPES.put("CHARAT", "LETTER");
        PARAM_COUNTS.put("CONCAT", 2);     RETURN_TYPES.put("CONCAT", "SENTENCE");
        PARAM_COUNTS.put("APPEND", 2);     RETURN_TYPES.put("APPEND", "VOID");
        PARAM_COUNTS.put("REPEAT", 2);     RETURN_TYPES.put("REPEAT", "SENTENCE");
        PARAM_COUNTS.put("TRIM", 2);       RETURN_TYPES.put("TRIM", "SENTENCE");
        PARAM_COUNTS.put("SPLIT", 2);      RETURN_TYPES.put("SPLIT", "ARRAY:SENTENCE");

        // 3-arg functions
        PARAM_COUNTS.put("SET", 3);        RETURN_TYPES.put("SET", "VOID");
        PARAM_COUNTS.put("SUB", 3);        RETURN_TYPES.put("SUB", "SENTENCE");
        PARAM_COUNTS.put("REPLACE", 3);    RETURN_TYPES.put("REPLACE", "SENTENCE");
    }

    public static int getParamCount(String functionName) {
        Integer count = PARAM_COUNTS.get(functionName.toUpperCase());
        return count != null ? count : -1;
    }

    public static String getReturnType(String functionName) {
        String type = RETURN_TYPES.get(functionName.toUpperCase());
        return type != null ? type : "UNKNOWN";
    }

    // ==================== Function Dispatch ====================

    public static Object call(String functionName, List<Object> args) {
        String func = functionName.toUpperCase();

        switch (func) {
            case "LENGTH": return doLength(args);
            case "EQUALS": return doEquals(args);
            case "STARTSWITH": return doStartsWith(args);
            case "ENDSWITH": return doEndsWith(args);
            case "CONTAINS": return doContains(args);
            case "FIND": return doFind(args);
            case "COUNT": return doCount(args);
            case "CHARAT": return doCharAt(args);
            case "CONCAT": return doConcat(args);
            case "APPEND": return doAppend(args);
            case "SET": return doSet(args);
            case "REPEAT": return doRepeat(args);
            case "UPPER": return doUpper(args);
            case "LOWER": return doLower(args);
            case "TRIM": return doTrim(args);
            case "SUB": return doSub(args);
            case "REPLACE": return doReplace(args);
            case "REVERSE": return doReverse(args);
            case "SPLIT": return doSplit(args);
            case "TO_NUMBER": return doToNumber(args);
            case "TO_SENTENCE": return doToSentence(args);
            default:
                throw new RuntimeException("Unknown strings function: " + functionName);
        }
    }

    // ==================== Helpers ====================

    private static String toStr(Object obj) {
        if (obj == null) return "";
        String s = obj.toString();
        // Remove surrounding quotes if present
        if (s.length() >= 2) {
            if ((s.startsWith("\"") && s.endsWith("\"")) || (s.startsWith("'") && s.endsWith("'"))) {
                return s.substring(1, s.length() - 1);
            }
        }
        return s;
    }

    private static int toInt(Object obj) {
        String s = toStr(obj);
        try {
            return (int) Double.parseDouble(s);
        } catch (NumberFormatException e) {
            throw new RuntimeException("strings function expected a number but got: " + obj);
        }
    }

    // ==================== Function Implementations ====================

    private static Object doLength(List<Object> args) {
        String s = toStr(args.get(0));
        return String.valueOf((double) s.length());
    }

    private static Object doEquals(List<Object> args) {
        String s1 = toStr(args.get(0));
        String s2 = toStr(args.get(1));
        return String.valueOf(s1.equals(s2));
    }

    private static Object doStartsWith(List<Object> args) {
        String s = toStr(args.get(0));
        String prefix = toStr(args.get(1));
        return String.valueOf(s.startsWith(prefix));
    }

    private static Object doEndsWith(List<Object> args) {
        String s = toStr(args.get(0));
        String suffix = toStr(args.get(1));
        return String.valueOf(s.endsWith(suffix));
    }

    private static Object doContains(List<Object> args) {
        String s = toStr(args.get(0));
        String keyword = toStr(args.get(1));
        return String.valueOf(s.contains(keyword));
    }

    private static Object doFind(List<Object> args) {
        String s = toStr(args.get(0));
        String keyword = toStr(args.get(1));
        return String.valueOf((double) s.indexOf(keyword));
    }

    private static Object doCount(List<Object> args) {
        String s = toStr(args.get(0));
        String keyword = toStr(args.get(1));
        if (keyword.isEmpty()) return String.valueOf(0.0);
        int count = 0;
        int idx = 0;
        while ((idx = s.indexOf(keyword, idx)) != -1) {
            count++;
            idx += keyword.length();
        }
        return String.valueOf((double) count);
    }

    private static Object doCharAt(List<Object> args) {
        String s = toStr(args.get(0));
        int index = toInt(args.get(1));
        if (index < 0 || index >= s.length()) {
            throw new RuntimeException("CHARAT index " + index + " out of bounds for string of length " + s.length());
        }
        return String.valueOf(s.charAt(index));
    }

    private static Object doConcat(List<Object> args) {
        String s1 = toStr(args.get(0));
        String s2 = toStr(args.get(1));
        return s1 + s2;
    }

    private static Object doAppend(List<Object> args) {
        // APPEND modifies the first string variable in-place
        // The first argument should be a variable name reference
        String varName = findVariableName(args.get(0));
        String s2 = toStr(args.get(1));

        if (varName != null && CoreNodes.GlobalContext.symbolTable.containsKey(varName)) {
            String current = toStr(CoreNodes.GlobalContext.symbolTable.get(varName));
            CoreNodes.GlobalContext.symbolTable.put(varName, "\"" + current + s2 + "\"");
        } else {
            throw new RuntimeException("APPEND requires a variable as the first argument");
        }
        return null;
    }

    private static Object doSet(List<Object> args) {
        // SET(s, l, i) - set character at index i in string variable s to letter l
        String varName = findVariableName(args.get(0));
        String letter = toStr(args.get(1));
        int index = toInt(args.get(2));

        if (letter.length() != 1) {
            throw new RuntimeException("SET expects a single character, got: " + letter);
        }

        if (varName != null && CoreNodes.GlobalContext.symbolTable.containsKey(varName)) {
            String current = toStr(CoreNodes.GlobalContext.symbolTable.get(varName));
            if (index < 0 || index >= current.length()) {
                throw new RuntimeException("SET index " + index + " out of bounds for string of length " + current.length());
            }
            char[] chars = current.toCharArray();
            chars[index] = letter.charAt(0);
            CoreNodes.GlobalContext.symbolTable.put(varName, "\"" + new String(chars) + "\"");
        } else {
            throw new RuntimeException("SET requires a variable as the first argument");
        }
        return null;
    }

    private static Object doRepeat(List<Object> args) {
        String s = toStr(args.get(0));
        int n = toInt(args.get(1));
        if (n < 0) throw new RuntimeException("REPEAT count cannot be negative: " + n);
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            sb.append(s);
        }
        return sb.toString();
    }

    private static Object doUpper(List<Object> args) {
        return toStr(args.get(0)).toUpperCase();
    }

    private static Object doLower(List<Object> args) {
        return toStr(args.get(0)).toLowerCase();
    }

    private static Object doTrim(List<Object> args) {
        String s = toStr(args.get(0));
        String chars = toStr(args.get(1));

        if (chars.isEmpty()) {
            return s.trim();
        }

        // Strip leading chars
        int start = 0;
        while (start < s.length() && chars.indexOf(s.charAt(start)) >= 0) {
            start++;
        }
        // Strip trailing chars
        int end = s.length();
        while (end > start && chars.indexOf(s.charAt(end - 1)) >= 0) {
            end--;
        }
        return s.substring(start, end);
    }

    private static Object doSub(List<Object> args) {
        String s = toStr(args.get(0));
        int start = toInt(args.get(1));
        int end = toInt(args.get(2));

        if (start < 0) start = 0;
        if (end >= s.length()) end = s.length() - 1;
        if (start > end) return "";

        return s.substring(start, end + 1); // inclusive end
    }

    private static Object doReplace(List<Object> args) {
        String s = toStr(args.get(0));
        String oldStr = toStr(args.get(1));
        String newStr = toStr(args.get(2));
        return s.replace(oldStr, newStr);
    }

    private static Object doReverse(List<Object> args) {
        String s = toStr(args.get(0));
        return new StringBuilder(s).reverse().toString();
    }

    private static Object doSplit(List<Object> args) {
        String s = toStr(args.get(0));
        String delimiter = toStr(args.get(1));

        String[] parts;
        if (delimiter.isEmpty()) {
            // Split into individual characters
            parts = new String[s.length()];
            for (int i = 0; i < s.length(); i++) {
                parts[i] = String.valueOf(s.charAt(i));
            }
        } else {
            parts = s.split(java.util.regex.Pattern.quote(delimiter), -1);
        }

        // Create a new array and register it
        String arrayName = "__split_result_" + System.nanoTime();
        ArrayCoreNodes.ArrayValue arrayValue = new ArrayCoreNodes.ArrayValue("SENTENCE");
        for (String part : parts) {
            arrayValue.addElement("\"" + part + "\"");
        }
        ArrayCoreNodes.putArray(arrayName, arrayValue);
        CoreNodes.GlobalContext.symbolTable.put(arrayName, "ARRAY:SENTENCE");

        return arrayName;
    }

    private static Object doToNumber(List<Object> args) {
        String s = toStr(args.get(0));
        try {
            return String.valueOf(Double.parseDouble(s));
        } catch (NumberFormatException e) {
            throw new RuntimeException("TO_NUMBER: cannot convert '" + s + "' to a number");
        }
    }

    private static Object doToSentence(List<Object> args) {
        String s = toStr(args.get(0));
        // If it's a number, format it nicely
        try {
            double num = Double.parseDouble(s);
            return String.valueOf(num);
        } catch (NumberFormatException e) {
            return s;
        }
    }

    /**
     * Try to determine the variable name from an argument.
     * When passed through the library system, the argument is the raw value
     * from the symbol table. We need to find which variable holds this value.
     */
    private static String findVariableName(Object obj) {
        if (obj == null) return null;
        String val = obj.toString();
        // Look through symbol table for a matching value
        for (Map.Entry<String, String> entry : CoreNodes.GlobalContext.symbolTable.entrySet()) {
            if (entry.getValue().equals(val)) {
                return entry.getKey();
            }
        }
        return null;
    }
}
