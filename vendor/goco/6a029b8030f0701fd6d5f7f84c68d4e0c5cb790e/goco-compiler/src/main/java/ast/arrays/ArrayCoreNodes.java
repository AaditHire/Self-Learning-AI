package ast.arrays;

import java.util.*;

public class ArrayCoreNodes {

    /**
     * Class representing a multi-dimensional array
     */
    public static class MultiDimensionalArrayValue extends ArrayValue {

        private int[] dimensions;
        private Map<String, ArrayValue> nestedArrays;

        public MultiDimensionalArrayValue(String type, int[] dimensions) {
            super(type);
            this.dimensions = dimensions;
            this.nestedArrays = new HashMap<>();
            setDimensions(dimensions.length); // Set the dimension count, not the array

            // For now, this just stores the dimension info
            // You'll need to implement the actual multi-dimensional storage
            // based on your language's requirements
        }

        public int[] getDimensionSizes() {
            return dimensions;
        }

        public int getDimension(int index) {
            if (index < 0 || index >= dimensions.length) {
                throw new RuntimeException("Invalid dimension index: " + index);
            }
            return dimensions[index];
        }

        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder();
            sb.append("Array");
            sb.append(java.util.Arrays.toString(dimensions));
            sb.append("<").append(getType()).append(">");
            return sb.toString();
        }
    }

    /**
     * Class representing an array in our language
     */
    public static class ArrayValue {

        private String name;
        private String type;
        private int dimensions;
        private List<String> elements;

        public ArrayValue(String type) {
            this.type = type.toUpperCase();
            this.dimensions = 1;
            this.elements = new ArrayList<>();
        }

        public ArrayValue(String type, List<String> elements) {
            this.type = type.toUpperCase();
            this.dimensions = 1;
            this.elements = new ArrayList<>(elements);
        }

        // Add setter for dimensions
        public void setDimensions(int dimensions) {
            this.dimensions = dimensions;
        }

        // Add getter for dimensions
        public int getDimensions() {
            return dimensions;
        }

        public void addElement(String value) {
            elements.add(value);
        }

        public String getElement(int index) {
            if (index < 0 || index >= elements.size()) {
                throw new RuntimeException("Array index " + index + " out of bounds for length " + elements.size());
            }
            return elements.get(index);
        }

        public void setElement(int index, String value) {
            if (index < 0 || index >= elements.size()) {
                throw new RuntimeException("Array index " + index + " out of bounds for length " + elements.size());
            }
            elements.set(index, value);
        }

        public String pop() {
            if (elements.isEmpty()) {
                throw new RuntimeException("Cannot pop from an empty array");
            }
            return elements.remove(elements.size() - 1);
        }

        public void push(String value) {
            elements.add(value);
        }

        public int length() {
            return elements.size();
        }

        public String getType() {
            return type;
        }

        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder();
            sb.append("[");
            for (int i = 0; i < elements.size(); i++) {
                String element = elements.get(i);
                switch (type) {
                    case "SENTENCE":
                        if (!element.startsWith("\"") || !element.endsWith("\"")) {
                            element = "\"" + element + "\"";
                        }
                        break;
                    case "LETTER":
                        if (!element.startsWith("'") || !element.endsWith("'")) {
                            element = "'" + element + "'";
                        }
                        break;
                    case "LOGIC":
                        element = element.toLowerCase();
                        break;
                }
                sb.append(element);
                if (i < elements.size() - 1) {
                    sb.append(", ");
                }
            }
            sb.append("]");
            return sb.toString();
        }

        public void validateArrayElement(String value) {
            // Remove quotes if present for type checking
            String checkValue = value;
            if ((checkValue.startsWith("\"") && checkValue.endsWith("\""))
                    || (checkValue.startsWith("'") && checkValue.endsWith("'"))) {
                checkValue = checkValue.substring(1, checkValue.length() - 1);
            }

            switch (this.type) {
                case "NUMBER":
                    if (!isNumeric(value)) {
                        throw new RuntimeException("Non-numeric value in NUMBER array: " + value);
                    }
                    break;
                case "SENTENCE":
                    // Allow any string - just ensure it's properly quoted if needed
                    if (!value.startsWith("\"") && !value.startsWith("'")) {
                        // Value doesn't have quotes, but that's OK for SENTENCE
                    }
                    break;
                case "LETTER":
                    // Check if it's a single character (with or without quotes)
                    if (value.startsWith("'") && value.endsWith("'") && value.length() == 3) {
                        // Quoted char literal - valid
                    } else if (value.length() == 1) {
                        // Single character without quotes - valid
                    } else {
                        throw new RuntimeException("Invalid LETTER value: " + value + " - must be a single character");
                    }
                    break;
                case "LOGIC":
                    if (!value.equalsIgnoreCase("true") && !value.equalsIgnoreCase("false")) {
                        throw new RuntimeException("Invalid LOGIC value: " + value);
                    }
                    break;
            }
        }
    }

    /**
     * Static map to store arrays separately from regular variables
     */
    private static HashMap<String, ArrayValue> arrayTable = new HashMap<>();
    private static int nestedArrayCounter = 0;

    /**
     * Utility method to check if a variable is an array
     */
    public static boolean isArray(String varName) {
        return arrayTable.containsKey(varName);
    }

    /**
     * Get array from table
     */
    public static ArrayValue getArray(String varName) {
        return arrayTable.get(varName);
    }

    /**
     * Put array in table
     */
    public static void putArray(String varName, ArrayValue array) {
        arrayTable.put(varName, array);
    }

    /**
     * Generate a unique name for a nested sub-array
     */
    public static String generateNestedArrayName(String parentName) {
        return "__nested_" + parentName + "_" + (nestedArrayCounter++);
    }

    /**
     * Utility method to check if a string is numeric
     */
    public static boolean isNumeric(String str) {
        if (str == null || str.isEmpty()) {
            return false;
        }

        // Remove quotes if present
        if ((str.startsWith("\"") && str.endsWith("\""))
                || (str.startsWith("'") && str.endsWith("'"))) {
            str = str.substring(1, str.length() - 1);
        }

        try {
            Double.parseDouble(str);
            return true;
        } catch (NumberFormatException e) {
            return false;
        }
    }

    /**
     * Utility method to validate if a value is appropriate for the array type
     */
    public static boolean isValidForType(String type, String value) {
        switch (type) {
            case "NUMBER":
                return isNumeric(value);
            case "LOGIC":
                return value.equals("true") || value.equals("false");
            case "LETTER":
                return value.length() == 1 || (value.startsWith("'") && value.endsWith("'") && value.length() == 3);
            case "SENTENCE":
                return true; // All values are valid for SENTENCE
            default:
                return true; // Unknown types are assumed valid
        }
    }

    /**
     * Helper method for displaying array elements
     */
    public static String getArrayElementForDisplay(String arrayName, int... indices) {
        if (!isArray(arrayName)) {
            throw new RuntimeException("Variable is not an array: " + arrayName);
        }

        ArrayValue array = arrayTable.get(arrayName);

        if (array instanceof MultiDimensionalArrayValue) {
            MultiDimensionalArrayValue mdArray = (MultiDimensionalArrayValue) array;
            if (indices.length != mdArray.getDimensions()) {
                throw new RuntimeException("Expected " + mdArray.getDimensions()
                        + " indices for multi-dimensional array, got " + indices.length);
            }

            // Navigate through dimensions
            // This is a simplified implementation - you'll need to implement
            // the actual storage mechanism for multi-dimensional arrays
            String elementValue = "0"; // Placeholder
            String arrayType = mdArray.getType();

            // Format based on type
            switch (arrayType) {
                case "NUMBER":
                    return elementValue;
                case "SENTENCE":
                    if (elementValue.startsWith("\"") && elementValue.endsWith("\"")) {
                        return elementValue.substring(1, elementValue.length() - 1);
                    }
                    return elementValue;
                case "LETTER":
                    if (elementValue.startsWith("'") && elementValue.endsWith("'")) {
                        return elementValue.substring(1, elementValue.length() - 1);
                    }
                    return elementValue;
                case "LOGIC":
                    return elementValue.toLowerCase();
                default:
                    return elementValue;
            }
        } else {
            // Single dimension array
            if (indices.length != 1) {
                throw new RuntimeException("Expected 1 index for single-dimension array, got " + indices.length);
            }
            String elementValue = array.getElement(indices[0]);
            String arrayType = array.getType();

            switch (arrayType) {
                case "NUMBER":
                    return elementValue;
                case "SENTENCE":
                    if (elementValue.startsWith("\"") && elementValue.endsWith("\"")) {
                        return elementValue.substring(1, elementValue.length() - 1);
                    }
                    return elementValue;
                case "LETTER":
                    if (elementValue.startsWith("'") && elementValue.endsWith("'")) {
                        return elementValue.substring(1, elementValue.length() - 1);
                    }
                    return elementValue;
                case "LOGIC":
                    return elementValue.toLowerCase();
                default:
                    return elementValue;
            }
        }
    }

    /**
     * Format array for display
     */
    public static String formatArrayForDisplay(String arrayName) {
        if (!isArray(arrayName)) {
            throw new RuntimeException("Variable is not an array: " + arrayName);
        }

        ArrayValue array = arrayTable.get(arrayName);
        return array.toString();
    }
}
