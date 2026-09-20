package ast.arrays;

import ast.nodes.CoreNodes;
import java.util.*;

/**
 * Arrays library for GOCO language.
 * Provides array manipulation functions.
 * Used via: IMPORT arrays. then arrays.LENGTH(arr), arrays.PUSH(arr, val), etc.
 */
public class ArraysLibrary {

    // ==================== Function Metadata ====================

    private static final Map<String, Integer> PARAM_COUNTS = new HashMap<>();
    private static final Map<String, String> RETURN_TYPES = new HashMap<>();

    static {
        // 1-arg functions
        PARAM_COUNTS.put("LENGTH", 1);
        RETURN_TYPES.put("LENGTH", "NUMBER");
        PARAM_COUNTS.put("POP", 1);
        RETURN_TYPES.put("POP", "UNKNOWN"); // depends on array type
        PARAM_COUNTS.put("SORT", 1);
        RETURN_TYPES.put("SORT", "VOID");
        PARAM_COUNTS.put("REVERSE", 1);
        RETURN_TYPES.put("REVERSE", "VOID");
        PARAM_COUNTS.put("SUM", 1);
        RETURN_TYPES.put("SUM", "NUMBER");
        PARAM_COUNTS.put("AVG", 1);
        RETURN_TYPES.put("AVG", "NUMBER");

        // 2-arg functions
        PARAM_COUNTS.put("PUSH", 2);
        RETURN_TYPES.put("PUSH", "VOID");
        PARAM_COUNTS.put("CONCAT", 2);
        RETURN_TYPES.put("CONCAT", "UNKNOWN"); // returns array
        PARAM_COUNTS.put("APPEND", 2);
        RETURN_TYPES.put("APPEND", "VOID");
        PARAM_COUNTS.put("FIND", 2);
        RETURN_TYPES.put("FIND", "NUMBER");
        PARAM_COUNTS.put("CONTAINS", 2);
        RETURN_TYPES.put("CONTAINS", "LOGIC");
        PARAM_COUNTS.put("COUNT", 2);
        RETURN_TYPES.put("COUNT", "NUMBER");
        PARAM_COUNTS.put("JOIN", 2);
        RETURN_TYPES.put("JOIN", "SENTENCE");
        PARAM_COUNTS.put("FILL", 2);
        RETURN_TYPES.put("FILL", "VOID");

        PARAM_COUNTS.put("SLICE", 3);
        RETURN_TYPES.put("SLICE", "UNKNOWN"); // returns array
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
            case "LENGTH":
                return doLength(args);
            case "PUSH":
                return doPush(args);
            case "POP":
                return doPop(args);
            case "SORT":
                return doSort(args);
            case "REVERSE":
                return doReverse(args);
            case "CONCAT":
                return doConcat(args);
            case "APPEND":
                return doAppend(args);
            case "SLICE":
                return doSlice(args);
            case "FIND":
                return doFind(args);
            case "CONTAINS":
                return doContains(args);
            case "COUNT":
                return doCount(args);
            case "SUM":
                return doSum(args);
            case "AVG":
                return doAvg(args);
            case "JOIN":
                return doJoin(args);
            case "FILL":
                return doFill(args);
            default:
                throw new RuntimeException("Unknown arrays function: " + functionName);
        }
    }

    // ==================== Helpers ====================

    private static String getArrayName(Object obj) {
        if (obj == null)
            throw new RuntimeException("Array function received null argument");
        String name = obj.toString().trim();
        // Remove quotes if present
        if (name.length() >= 2
                && ((name.startsWith("\"") && name.endsWith("\"")) || (name.startsWith("'") && name.endsWith("'")))) {
            name = name.substring(1, name.length() - 1);
        }
        // Check if this is a direct array name in the symbol table
        if (ArrayCoreNodes.isArray(name)) {
            return name;
        }
        // Try looking up in symbol table to find the array variable
        for (Map.Entry<String, String> entry : CoreNodes.GlobalContext.symbolTable.entrySet()) {
            if (entry.getValue().equals(name) || entry.getKey().equals(name)) {
                if (ArrayCoreNodes.isArray(entry.getKey())) {
                    return entry.getKey();
                }
            }
        }
        throw new RuntimeException("Variable is not an array: " + name);
    }

    private static ArrayCoreNodes.ArrayValue getArray(Object obj) {
        String name = getArrayName(obj);
        return ArrayCoreNodes.getArray(name);
    }

    private static int toInt(Object obj) {
        String s = obj.toString().trim();
        if (s.length() >= 2 && ((s.startsWith("\"") && s.endsWith("\"")) || (s.startsWith("'") && s.endsWith("'")))) {
            s = s.substring(1, s.length() - 1);
        }
        try {
            return (int) Double.parseDouble(s);
        } catch (NumberFormatException e) {
            throw new RuntimeException("arrays function expected a number but got: " + obj);
        }
    }

    private static String toStr(Object obj) {
        if (obj == null)
            return "";
        String s = obj.toString();
        return s;
    }

    private static String stripQuotes(String s) {
        if (s.length() >= 2 && ((s.startsWith("\"") && s.endsWith("\"")) || (s.startsWith("'") && s.endsWith("'")))) {
            return s.substring(1, s.length() - 1);
        }
        return s;
    }

    // ==================== Function Implementations ====================

    private static Object doLength(List<Object> args) {
        ArrayCoreNodes.ArrayValue arr = getArray(args.get(0));
        return String.valueOf((double) arr.length());
    }

    private static Object doPush(List<Object> args) {
        ArrayCoreNodes.ArrayValue arr = getArray(args.get(0));
        Object value = args.get(1);
        String valueStr = value.toString();

        if (arr.getType().equals("NUMBER") && !ArrayCoreNodes.isNumeric(valueStr)) {
            throw new RuntimeException("Cannot push non-numeric value to NUMBER array: " + valueStr);
        }

        arr.push(valueStr);
        return null;
    }

    private static Object doPop(List<Object> args) {
        ArrayCoreNodes.ArrayValue arr = getArray(args.get(0));
        String popped = arr.pop();

        // Remove quotes for display
        if (popped.startsWith("\"") && popped.endsWith("\"")
                || popped.startsWith("'") && popped.endsWith("'")) {
            return popped.substring(1, popped.length() - 1);
        }
        return popped;
    }

    private static Object doSort(List<Object> args) {
        ArrayCoreNodes.ArrayValue arr = getArray(args.get(0));
        List<String> elements = new ArrayList<>();
        for (int i = 0; i < arr.length(); i++) {
            elements.add(arr.getElement(i));
        }

        if (arr.getType().equals("NUMBER")) {
            // Sort numerically
            elements.sort((a, b) -> {
                double da = Double.parseDouble(a);
                double db = Double.parseDouble(b);
                return Double.compare(da, db);
            });
        } else {
            // Sort lexicographically
            elements.sort((a, b) -> {
                String sa = stripQuotes(a);
                String sb = stripQuotes(b);
                return sa.compareTo(sb);
            });
        }

        // Update array in-place
        for (int i = 0; i < elements.size(); i++) {
            arr.setElement(i, elements.get(i));
        }
        return null;
    }

    private static Object doReverse(List<Object> args) {
        ArrayCoreNodes.ArrayValue arr = getArray(args.get(0));
        int len = arr.length();
        for (int i = 0; i < len / 2; i++) {
            String temp = arr.getElement(i);
            arr.setElement(i, arr.getElement(len - 1 - i));
            arr.setElement(len - 1 - i, temp);
        }
        return null;
    }

    private static Object doConcat(List<Object> args) {
        ArrayCoreNodes.ArrayValue arr1 = getArray(args.get(0));
        ArrayCoreNodes.ArrayValue arr2 = getArray(args.get(1));

        // Create a new array with elements from both
        String resultName = "__concat_result_" + System.nanoTime();
        ArrayCoreNodes.ArrayValue resultArr = new ArrayCoreNodes.ArrayValue(arr1.getType());
        for (int i = 0; i < arr1.length(); i++) {
            resultArr.addElement(arr1.getElement(i));
        }
        for (int i = 0; i < arr2.length(); i++) {
            resultArr.addElement(arr2.getElement(i));
        }
        ArrayCoreNodes.putArray(resultName, resultArr);
        CoreNodes.GlobalContext.symbolTable.put(resultName, "ARRAY:" + arr1.getType());

        return resultName;
    }

    private static Object doAppend(List<Object> args) {
        ArrayCoreNodes.ArrayValue arr1 = getArray(args.get(0));
        ArrayCoreNodes.ArrayValue arr2 = getArray(args.get(1));

        for (int i = 0; i < arr2.length(); i++) {
            arr1.push(arr2.getElement(i));
        }
        return null;
    }

    private static Object doSlice(List<Object> args) {
        ArrayCoreNodes.ArrayValue arr = getArray(args.get(0));
        int start = toInt(args.get(1));
        int end = toInt(args.get(2));

        if (start < 0)
            start = 0;
        if (end >= arr.length())
            end = arr.length() - 1;

        String resultName = "__slice_result_" + System.nanoTime();
        ArrayCoreNodes.ArrayValue resultArr = new ArrayCoreNodes.ArrayValue(arr.getType());
        for (int i = start; i <= end && i < arr.length(); i++) {
            resultArr.addElement(arr.getElement(i));
        }
        ArrayCoreNodes.putArray(resultName, resultArr);
        CoreNodes.GlobalContext.symbolTable.put(resultName, "ARRAY:" + arr.getType());

        return resultName;
    }

    private static Object doFind(List<Object> args) {
        ArrayCoreNodes.ArrayValue arr = getArray(args.get(0));
        String target = toStr(args.get(1));

        for (int i = 0; i < arr.length(); i++) {
            String elem = arr.getElement(i);
            if (elem.equals(target) || stripQuotes(elem).equals(stripQuotes(target))) {
                return String.valueOf((double) i);
            }
        }
        return String.valueOf(-1.0);
    }

    private static Object doContains(List<Object> args) {
        ArrayCoreNodes.ArrayValue arr = getArray(args.get(0));
        String target = toStr(args.get(1));

        for (int i = 0; i < arr.length(); i++) {
            String elem = arr.getElement(i);
            if (elem.equals(target) || stripQuotes(elem).equals(stripQuotes(target))) {
                return String.valueOf(true);
            }
        }
        return String.valueOf(false);
    }

    private static Object doCount(List<Object> args) {
        ArrayCoreNodes.ArrayValue arr = getArray(args.get(0));
        String target = toStr(args.get(1));
        int count = 0;

        for (int i = 0; i < arr.length(); i++) {
            String elem = arr.getElement(i);
            if (elem.equals(target) || stripQuotes(elem).equals(stripQuotes(target))) {
                count++;
            }
        }
        return String.valueOf((double) count);
    }

    private static Object doSum(List<Object> args) {
        ArrayCoreNodes.ArrayValue arr = getArray(args.get(0));
        double sum = 0;
        for (int i = 0; i < arr.length(); i++) {
            try {
                sum += Double.parseDouble(arr.getElement(i));
            } catch (NumberFormatException e) {
                throw new RuntimeException("SUM: array element is not a number: " + arr.getElement(i));
            }
        }
        return String.valueOf(sum);
    }

    private static Object doAvg(List<Object> args) {
        ArrayCoreNodes.ArrayValue arr = getArray(args.get(0));
        if (arr.length() == 0) {
            throw new RuntimeException("AVG: cannot compute average of empty array");
        }
        double sum = 0;
        for (int i = 0; i < arr.length(); i++) {
            try {
                sum += Double.parseDouble(arr.getElement(i));
            } catch (NumberFormatException e) {
                throw new RuntimeException("AVG: array element is not a number: " + arr.getElement(i));
            }
        }
        return String.valueOf(sum / arr.length());
    }

    private static Object doJoin(List<Object> args) {
        ArrayCoreNodes.ArrayValue arr = getArray(args.get(0));
        String separator = stripQuotes(toStr(args.get(1)));

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < arr.length(); i++) {
            if (i > 0)
                sb.append(separator);
            String elem = arr.getElement(i);
            if (arr.getType().equals("NUMBER") && !elem.contains(".")) {
                try {
                    elem = String.valueOf(Double.parseDouble(elem));
                } catch (NumberFormatException e) {
                    // ignore
                }
            }
            sb.append(stripQuotes(elem));
        }
        return sb.toString();
    }

    private static Object doFill(List<Object> args) {
        ArrayCoreNodes.ArrayValue arr = getArray(args.get(0));
        String value = toStr(args.get(1));

        for (int i = 0; i < arr.length(); i++) {
            arr.setElement(i, value);
        }
        return null;
    }
}
