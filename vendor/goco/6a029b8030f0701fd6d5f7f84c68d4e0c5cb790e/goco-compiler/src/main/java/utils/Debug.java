package utils;

public final class Debug {

    public static final boolean ENABLED = false;

    private Debug() {
    }

    // log methods
    // only print when this.ENABLED = true (using System.out)

    public static void log(String msg) {
        if (ENABLED) {
            System.out.print(msg);
        }
    }

    public static void log(String msg, Object... args) {
        if (ENABLED) {
            System.out.printf(msg, args);
        }
    }

    public static void log(Object obj) {
        if (ENABLED) {
            System.out.print(obj);
        }
    }

    public static void logln(String msg) {
        if (ENABLED) {
            System.out.println(msg);
        }
    }

    public static void logln(String msg, Object... args) {
        if (ENABLED) {
            System.out.printf(msg + "%n", args);
        }
    }

    public static void logln(Object obj) {
        if (ENABLED) {
            System.out.println(obj);
        }
    }

    // print methods
    // always print (using System.out)

    public static void print(String msg) {
        System.out.print(msg);
    }

    public static void print(String msg, Object... args) {
        System.out.printf(msg, args);
    }

    public static void print(Object obj) {
        System.out.print(obj);
    }

    public static void println(String msg) {
        System.out.println(msg);
    }

    public static void println(String msg, Object... args) {
        System.out.printf(msg + "%n", args);
    }

    public static void println(Object obj) {
        System.out.println(obj);
    }

    // error methods
    // always print (using System.err)

    public static void err(String msg) {
        System.err.print(msg);
    }

    public static void err(String msg, Object... args) {
        System.err.printf(msg, args);
    }

    public static void err(Object obj) {
        System.err.print(obj);
    }

    public static void errln(String msg) {
        System.err.println(msg);
    }

    public static void errln(String msg, Object... args) {
        System.err.printf(msg + "%n", args);
    }

    public static void errln(Object obj) {
        System.err.println(obj);
    }

}
