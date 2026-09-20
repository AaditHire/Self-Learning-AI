package ast.math;

import java.util.*;

/**
 * Math library for GOCO language.
 * Provides mathematical constants and functions.
 * Used via: IMPORT math. then math.PI, math.POW(2, 3), etc.
 */
public class MathLibrary {

    // ==================== Constants ====================

    private static final Map<String, Double> CONSTANTS = new HashMap<>();
    static {
        CONSTANTS.put("PI", 3.141592653589793);
        CONSTANTS.put("E", 2.718281828459045);
    }

    public static boolean hasConstant(String name) {
        return CONSTANTS.containsKey(name.toUpperCase());
    }

    public static Object getConstant(String name) {
        Double val = CONSTANTS.get(name.toUpperCase());
        if (val == null) {
            throw new RuntimeException("Unknown math constant: " + name);
        }
        return String.valueOf(val);
    }

    // ==================== Function Metadata ====================

    // function name -> param count
    private static final Map<String, Integer> PARAM_COUNTS = new HashMap<>();
    // function name -> return type
    private static final Map<String, String> RETURN_TYPES = new HashMap<>();

    static {
        // 1-arg functions
        String[] oneArgFuncs = {"ABS", "SIGN", "SQRT", "EXP", "LOG", "LOG10",
                "ROUND", "CEIL", "FLOOR", "DEG2RAD", "RAD2DEG",
                "SIN", "COS", "TAN", "ASIN", "ACOS", "ATAN"};
        for (String f : oneArgFuncs) {
            PARAM_COUNTS.put(f, 1);
            RETURN_TYPES.put(f, "NUMBER");
        }

        // 2-arg functions
        String[] twoArgFuncs = {"POW", "LOGN", "RANDOM", "MIN", "MAX"};
        for (String f : twoArgFuncs) {
            PARAM_COUNTS.put(f, 2);
            RETURN_TYPES.put(f, "NUMBER");
        }

        // 3-arg functions
        PARAM_COUNTS.put("CLAMP", 3);
        RETURN_TYPES.put("CLAMP", "NUMBER");
    }

    public static int getParamCount(String functionName) {
        Integer count = PARAM_COUNTS.get(functionName.toUpperCase());
        return count != null ? count : -1; // -1 means function not found
    }

    public static String getReturnType(String functionName) {
        String type = RETURN_TYPES.get(functionName.toUpperCase());
        return type != null ? type : "UNKNOWN";
    }

    // ==================== Function Dispatch ====================

    public static Object call(String functionName, List<Object> args) {
        String func = functionName.toUpperCase();

        switch (func) {
            case "ABS": return doAbs(args);
            case "SIGN": return doSign(args);
            case "SQRT": return doSqrt(args);
            case "POW": return doPow(args);
            case "EXP": return doExp(args);
            case "LOG": return doLog(args);
            case "LOG10": return doLog10(args);
            case "LOGN": return doLogN(args);
            case "ROUND": return doRound(args);
            case "CEIL": return doCeil(args);
            case "FLOOR": return doFloor(args);
            case "RANDOM": return doRandom(args);
            case "MIN": return doMin(args);
            case "MAX": return doMax(args);
            case "CLAMP": return doClamp(args);
            case "DEG2RAD": return doDeg2Rad(args);
            case "RAD2DEG": return doRad2Deg(args);
            case "SIN": return doSin(args);
            case "COS": return doCos(args);
            case "TAN": return doTan(args);
            case "ASIN": return doAsin(args);
            case "ACOS": return doAcos(args);
            case "ATAN": return doAtan(args);
            default:
                throw new RuntimeException("Unknown math function: " + functionName);
        }
    }

    // ==================== Helper ====================

    private static double toDouble(Object obj) {
        if (obj == null) throw new RuntimeException("math function received null argument");
        String s = obj.toString().trim();
        // Remove quotes if present
        if (s.length() >= 2 && ((s.startsWith("\"") && s.endsWith("\"")) || (s.startsWith("'") && s.endsWith("'")))) {
            s = s.substring(1, s.length() - 1);
        }
        try {
            return Double.parseDouble(s);
        } catch (NumberFormatException e) {
            throw new RuntimeException("math function expected a number but got: " + obj);
        }
    }

    private static String formatResult(double val) {
        return String.valueOf(val);
    }

    // ==================== Function Implementations ====================

    private static Object doAbs(List<Object> args) {
        return formatResult(Math.abs(toDouble(args.get(0))));
    }

    private static Object doSign(List<Object> args) {
        return formatResult(Math.signum(toDouble(args.get(0))));
    }

    private static Object doSqrt(List<Object> args) {
        double x = toDouble(args.get(0));
        if (x < 0) throw new RuntimeException("Cannot compute square root of negative number: " + x);
        return formatResult(Math.sqrt(x));
    }

    private static Object doPow(List<Object> args) {
        return formatResult(Math.pow(toDouble(args.get(0)), toDouble(args.get(1))));
    }

    private static Object doExp(List<Object> args) {
        return formatResult(Math.exp(toDouble(args.get(0))));
    }

    private static Object doLog(List<Object> args) {
        double x = toDouble(args.get(0));
        if (x <= 0) throw new RuntimeException("Cannot compute logarithm of non-positive number: " + x);
        return formatResult(Math.log(x));
    }

    private static Object doLog10(List<Object> args) {
        double x = toDouble(args.get(0));
        if (x <= 0) throw new RuntimeException("Cannot compute log10 of non-positive number: " + x);
        return formatResult(Math.log10(x));
    }

    private static Object doLogN(List<Object> args) {
        double x = toDouble(args.get(0));
        double base = toDouble(args.get(1));
        if (x <= 0) throw new RuntimeException("Cannot compute logarithm of non-positive number: " + x);
        if (base <= 0 || base == 1) throw new RuntimeException("Invalid logarithm base: " + base);
        return formatResult(Math.log(x) / Math.log(base));
    }

    private static Object doRound(List<Object> args) {
        return formatResult(Math.round(toDouble(args.get(0))));
    }

    private static Object doCeil(List<Object> args) {
        return formatResult(Math.ceil(toDouble(args.get(0))));
    }

    private static Object doFloor(List<Object> args) {
        return formatResult(Math.floor(toDouble(args.get(0))));
    }

    private static Object doRandom(List<Object> args) {
        double min = toDouble(args.get(0));
        double max = toDouble(args.get(1));
        if (min > max) throw new RuntimeException("RANDOM: min (" + min + ") cannot be greater than max (" + max + ")");
        // Random number between min (inclusive) and max (inclusive)
        double range = max - min + 1;
        double result = Math.floor(Math.random() * range) + min;
        return formatResult(result);
    }

    private static Object doMin(List<Object> args) {
        return formatResult(Math.min(toDouble(args.get(0)), toDouble(args.get(1))));
    }

    private static Object doMax(List<Object> args) {
        return formatResult(Math.max(toDouble(args.get(0)), toDouble(args.get(1))));
    }

    private static Object doClamp(List<Object> args) {
        double x = toDouble(args.get(0));
        double min = toDouble(args.get(1));
        double max = toDouble(args.get(2));
        return formatResult(Math.max(min, Math.min(max, x)));
    }

    private static Object doDeg2Rad(List<Object> args) {
        return formatResult(Math.toRadians(toDouble(args.get(0))));
    }

    private static Object doRad2Deg(List<Object> args) {
        return formatResult(Math.toDegrees(toDouble(args.get(0))));
    }

    private static Object doSin(List<Object> args) {
        return formatResult(Math.sin(toDouble(args.get(0))));
    }

    private static Object doCos(List<Object> args) {
        return formatResult(Math.cos(toDouble(args.get(0))));
    }

    private static Object doTan(List<Object> args) {
        return formatResult(Math.tan(toDouble(args.get(0))));
    }

    private static Object doAsin(List<Object> args) {
        double x = toDouble(args.get(0));
        if (x < -1 || x > 1) throw new RuntimeException("ASIN argument out of range [-1, 1]: " + x);
        return formatResult(Math.asin(x));
    }

    private static Object doAcos(List<Object> args) {
        double x = toDouble(args.get(0));
        if (x < -1 || x > 1) throw new RuntimeException("ACOS argument out of range [-1, 1]: " + x);
        return formatResult(Math.acos(x));
    }

    private static Object doAtan(List<Object> args) {
        return formatResult(Math.atan(toDouble(args.get(0))));
    }
}
