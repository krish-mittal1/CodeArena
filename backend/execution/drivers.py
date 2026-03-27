"""
LeetCode-style driver script generator.

For each supported language, generates a hidden 'main' wrapper that:
1. Reads test case input (as JSON lines)
2. Deserializes into native types
3. Instantiates the user's Solution class
4. Calls the target method
5. Serializes the result to stdout as JSON

Test case inputs are stored as JSON in input.txt (one JSON value per parameter, one per line).
Expected outputs are stored as a single JSON value.
"""

from __future__ import annotations
import json
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Type mapping helpers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Supported parameter types (matches LeetCode conventions)
# int, int[], int[][], str, str[], float, float[], bool, bool[]
# List[int], List[str], List[List[int]], etc.

def _python_type_hint(param_type: str) -> str:
    """Convert our type string to Python type hint."""
    mapping = {
        "int": "int",
        "int[]": "List[int]",
        "int[][]": "List[List[int]]",
        "str": "str",
        "str[]": "List[str]",
        "float": "float",
        "float[]": "List[float]",
        "bool": "bool",
        "bool[]": "List[bool]",
    }
    return mapping.get(param_type, "Any")


def _cpp_type(param_type: str) -> str:
    """Convert our type string to C++ type."""
    mapping = {
        "int": "int",
        "int[]": "vector<int>",
        "int[][]": "vector<vector<int>>",
        "str": "string",
        "str[]": "vector<string>",
        "float": "double",
        "float[]": "vector<double>",
        "bool": "bool",
        "bool[]": "vector<bool>",
    }
    return mapping.get(param_type, "int")


def _java_type(param_type: str) -> str:
    """Convert our type string to Java type."""
    mapping = {
        "int": "int",
        "int[]": "int[]",
        "int[][]": "int[][]",
        "str": "String",
        "str[]": "String[]",
        "float": "double",
        "float[]": "double[]",
        "bool": "boolean",
        "bool[]": "boolean[]",
    }
    return mapping.get(param_type, "int")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Python Driver
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def generate_python_driver(
    method_name: str,
    parameters: List[Dict[str, str]],
    return_type: str,
) -> str:
    """
    Generate a Python driver script that:
    1. Imports the user's code.py (which contains class Solution)
    2. Reads JSON lines from stdin for each parameter
    3. Calls Solution().method_name(...)
    4. Prints result as JSON to stdout
    """
    param_names = [p["name"] for p in parameters]
    call_args = ", ".join(param_names)
    
    read_lines = ""
    for p in parameters:
        read_lines += f"    {p['name']} = json.loads(input())\n"

    return f'''import sys
import json

# Import user code
sys.path.insert(0, '/sandbox')
from solution import Solution

def main():
    import sys
    input_data = sys.stdin.read().strip().split('\\n')
    idx = 0
{_indent_read_lines(parameters)}
    sol = Solution()
    result = sol.{method_name}({call_args})
    print(json.dumps(result))

if __name__ == "__main__":
    main()
'''


def _indent_read_lines(parameters: List[Dict[str, str]]) -> str:
    lines = ""
    for p in parameters:
        lines += f"    {p['name']} = json.loads(input_data[idx])\n"
        lines += f"    idx += 1\n"
    return lines


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  JavaScript Driver
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def generate_javascript_driver(
    method_name: str,
    parameters: List[Dict[str, str]],
    return_type: str,
) -> str:
    """
    Generate a Node.js driver script.
    User code.js must export a function or a Solution class.
    """
    param_names = [p["name"] for p in parameters]
    call_args = ", ".join(param_names)
    
    read_lines = ""
    for i, p in enumerate(parameters):
        read_lines += f"    const {p['name']} = JSON.parse(lines[{i}]);\n"
    
    return f'''const fs = require('fs');
const input = fs.readFileSync('/dev/stdin', 'utf8').trim().split('\\n');
const lines = input;

// Load user code
const userModule = require('/sandbox/code.js');

// Support both: class Solution or direct function export
let solution;
if (typeof userModule === 'function') {{
    solution = new userModule();
}} else if (userModule.Solution) {{
    solution = new userModule.Solution();
}} else if (typeof userModule.{method_name} === 'function') {{
    solution = userModule;
}} else {{
    // Try default export
    solution = userModule;
}}

function main() {{
{read_lines}
    let result;
    if (typeof solution.{method_name} === 'function') {{
        result = solution.{method_name}({call_args});
    }} else if (typeof solution === 'function') {{
        result = solution({call_args});
    }} else {{
        throw new Error('Cannot find method {method_name} in user code');
    }}
    console.log(JSON.stringify(result));
}}

main();
'''


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  C++ Driver
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _cpp_json_parser(param_type: str, var_name: str) -> str:
    """Generate C++ code to parse a JSON line into the given type."""
    if param_type == "int":
        return f"    int {var_name} = stoi(line);"
    elif param_type == "str":
        return f'    string {var_name} = parseJsonString(line);'
    elif param_type == "int[]":
        return f"    vector<int> {var_name} = parseJsonIntArray(line);"
    elif param_type == "int[][]":
        return f"    vector<vector<int>> {var_name} = parseJson2DIntArray(line);"
    elif param_type == "str[]":
        return f"    vector<string> {var_name} = parseJsonStringArray(line);"
    elif param_type == "float":
        return f"    double {var_name} = stod(line);"
    elif param_type == "bool":
        return f'    bool {var_name} = (line == "true");'
    else:
        return f"    int {var_name} = stoi(line);"


def _cpp_json_serializer(return_type: str) -> str:
    """Generate C++ code to serialize result to JSON stdout."""
    if return_type == "int":
        return '    cout << result << endl;'
    elif return_type == "str":
        return '    cout << "\\"" << result << "\\"" << endl;'
    elif return_type == "bool":
        return '    cout << (result ? "true" : "false") << endl;'
    elif return_type == "float":
        return '    cout << fixed << setprecision(5) << result << endl;'
    elif return_type == "int[]":
        return '''    cout << "[";
    for (size_t i = 0; i < result.size(); i++) {
        if (i > 0) cout << ",";
        cout << result[i];
    }
    cout << "]" << endl;'''
    elif return_type == "int[][]":
        return '''    cout << "[";
    for (size_t i = 0; i < result.size(); i++) {
        if (i > 0) cout << ",";
        cout << "[";
        for (size_t j = 0; j < result[i].size(); j++) {
            if (j > 0) cout << ",";
            cout << result[i][j];
        }
        cout << "]";
    }
    cout << "]" << endl;'''
    elif return_type == "str[]":
        return '''    cout << "[";
    for (size_t i = 0; i < result.size(); i++) {
        if (i > 0) cout << ",";
        cout << "\\"" << result[i] << "\\"";
    }
    cout << "]" << endl;'''
    else:
        return '    cout << result << endl;'


def generate_cpp_driver(
    method_name: str,
    parameters: List[Dict[str, str]],
    return_type: str,
) -> str:
    """Generate a C++ driver with JSON parsing utilities."""
    param_names = [p["name"] for p in parameters]
    call_args = ", ".join(param_names)
    
    read_blocks = ""
    for p in parameters:
        read_blocks += f"    getline(cin, line);\n"
        read_blocks += _cpp_json_parser(p["type"], p["name"]) + "\n"
    
    serialize_block = _cpp_json_serializer(return_type)
    cpp_ret_type = _cpp_type(return_type)
    
    return f'''#include <bits/stdc++.h>
using namespace std;

// ── JSON Parsing Utilities ──
string parseJsonString(const string& s) {{
    string res;
    bool inStr = false;
    for (size_t i = 0; i < s.size(); i++) {{
        if (s[i] == '"') {{ inStr = !inStr; continue; }}
        if (inStr) {{
            if (s[i] == '\\\\' && i+1 < s.size()) {{ res += s[++i]; continue; }}
            res += s[i];
        }}
    }}
    return res;
}}

vector<int> parseJsonIntArray(const string& s) {{
    vector<int> res;
    string num;
    bool inNum = false;
    for (char c : s) {{
        if (c == '-' || isdigit(c)) {{
            num += c;
            inNum = true;
        }} else if (inNum) {{
            res.push_back(stoi(num));
            num.clear();
            inNum = false;
        }}
    }}
    if (inNum) res.push_back(stoi(num));
    return res;
}}

vector<vector<int>> parseJson2DIntArray(const string& s) {{
    vector<vector<int>> res;
    int depth = 0;
    string current;
    for (char c : s) {{
        if (c == '[') {{
            depth++;
            if (depth == 2) current.clear();
        }} else if (c == ']') {{
            if (depth == 2 && !current.empty()) {{
                res.push_back(parseJsonIntArray("[" + current + "]"));
            }}
            depth--;
        }} else if (depth == 2) {{
            current += c;
        }}
    }}
    return res;
}}

vector<string> parseJsonStringArray(const string& s) {{
    vector<string> res;
    bool inStr = false;
    string current;
    for (size_t i = 0; i < s.size(); i++) {{
        if (s[i] == '"') {{
            if (inStr) {{
                res.push_back(current);
                current.clear();
            }}
            inStr = !inStr;
        }} else if (inStr) {{
            current += s[i];
        }}
    }}
    return res;
}}

// ── Include user code ──
#include "/sandbox/code.cpp"

int main() {{
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    
    string line;
{read_blocks}
    Solution sol;
    {cpp_ret_type} result = sol.{method_name}({call_args});

{serialize_block}
    return 0;
}}
'''


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Java Driver
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _java_json_parser(param_type: str, var_name: str) -> str:
    """Generate Java code to parse a JSON line into the given type."""
    if param_type == "int":
        return f"        int {var_name} = Integer.parseInt(lines[idx++].trim());"
    elif param_type == "str":
        return f'        String {var_name} = parseJsonString(lines[idx++].trim());'
    elif param_type == "int[]":
        return f"        int[] {var_name} = parseJsonIntArray(lines[idx++].trim());"
    elif param_type == "int[][]":
        return f"        int[][] {var_name} = parseJson2DIntArray(lines[idx++].trim());"
    elif param_type == "str[]":
        return f"        String[] {var_name} = parseJsonStringArray(lines[idx++].trim());"
    elif param_type == "bool":
        return f'        boolean {var_name} = lines[idx++].trim().equals("true");'
    else:
        return f"        int {var_name} = Integer.parseInt(lines[idx++].trim());"


def _java_json_serializer(return_type: str) -> str:
    """Generate Java code to serialize result to JSON stdout."""
    if return_type == "int":
        return '        System.out.println(result);'
    elif return_type == "str":
        return '        System.out.println("\\"" + result + "\\"");'
    elif return_type == "bool":
        return '        System.out.println(result ? "true" : "false");'
    elif return_type == "int[]":
        return '''        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < result.length; i++) {
            if (i > 0) sb.append(",");
            sb.append(result[i]);
        }
        sb.append("]");
        System.out.println(sb.toString());'''
    elif return_type == "int[][]":
        return '''        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < result.length; i++) {
            if (i > 0) sb.append(",");
            sb.append("[");
            for (int j = 0; j < result[i].length; j++) {
                if (j > 0) sb.append(",");
                sb.append(result[i][j]);
            }
            sb.append("]");
        }
        sb.append("]");
        System.out.println(sb.toString());'''
    elif return_type == "str[]":
        return '''        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < result.length; i++) {
            if (i > 0) sb.append(",");
            sb.append("\\"").append(result[i]).append("\\"");
        }
        sb.append("]");
        System.out.println(sb.toString());'''
    else:
        return '        System.out.println(result);'


def generate_java_driver(
    method_name: str,
    parameters: List[Dict[str, str]],
    return_type: str,
) -> str:
    """Generate a Java driver with JSON parsing utilities."""
    param_names = [p["name"] for p in parameters]
    call_args = ", ".join(param_names)
    
    read_blocks = ""
    for p in parameters:
        read_blocks += _java_json_parser(p["type"], p["name"]) + "\n"
    
    serialize_block = _java_json_serializer(return_type)
    java_ret_type = _java_type(return_type)
    
    return f'''import java.util.*;
import java.io.*;

public class Main {{

    static String parseJsonString(String s) {{
        s = s.trim();
        if (s.startsWith("\\"") && s.endsWith("\\""))
            return s.substring(1, s.length() - 1);
        return s;
    }}

    static int[] parseJsonIntArray(String s) {{
        s = s.trim();
        if (s.equals("[]")) return new int[0];
        s = s.substring(1, s.length() - 1);
        String[] parts = s.split(",");
        int[] res = new int[parts.length];
        for (int i = 0; i < parts.length; i++)
            res[i] = Integer.parseInt(parts[i].trim());
        return res;
    }}

    static int[][] parseJson2DIntArray(String s) {{
        s = s.trim();
        if (s.equals("[]")) return new int[0][];
        List<int[]> list = new ArrayList<>();
        int depth = 0;
        StringBuilder current = new StringBuilder();
        for (char c : s.toCharArray()) {{
            if (c == '[') {{
                depth++;
                if (depth == 2) current = new StringBuilder();
            }} else if (c == ']') {{
                if (depth == 2) {{
                    list.add(parseJsonIntArray("[" + current + "]"));
                }}
                depth--;
            }} else if (depth == 2) {{
                current.append(c);
            }}
        }}
        return list.toArray(new int[0][]);
    }}

    static String[] parseJsonStringArray(String s) {{
        s = s.trim();
        if (s.equals("[]")) return new String[0];
        List<String> list = new ArrayList<>();
        boolean inStr = false;
        StringBuilder current = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {{
            char c = s.charAt(i);
            if (c == '"') {{
                if (inStr) {{
                    list.add(current.toString());
                    current = new StringBuilder();
                }}
                inStr = !inStr;
            }} else if (inStr) {{
                current.append(c);
            }}
        }}
        return list.toArray(new String[0]);
    }}

    public static void main(String[] args) throws Exception {{
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb2 = new StringBuilder();
        String l;
        while ((l = br.readLine()) != null) sb2.append(l).append("\\n");
        String[] lines = sb2.toString().trim().split("\\n");
        int idx = 0;

{read_blocks}
        Solution sol = new Solution();
        {java_ret_type} result = sol.{method_name}({call_args});

{serialize_block}
    }}
}}
'''


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Public API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def generate_driver(
    language: str,
    method_name: str,
    parameters: List[Dict[str, str]],
    return_type: str,
) -> Optional[str]:
    """
    Generate driver code for the given language and problem signature.
    Returns None if signature data is missing (falls back to raw execution).
    """
    if not method_name or not parameters or not return_type:
        return None
    
    generators = {
        "python": generate_python_driver,
        "cpp": generate_cpp_driver,
        "java": generate_java_driver,
        "javascript": generate_javascript_driver,
    }
    
    gen = generators.get(language)
    if not gen:
        logger.warning(f"No driver generator for language: {language}")
        return None
    
    return gen(method_name, parameters, return_type)


def convert_test_input_to_json(
    raw_input: str,
    parameters: List[Dict[str, str]],
) -> str:
    """
    Convert a raw competitive-programming style input to JSON lines.
    
    For problems with LeetCode signature metadata, test case inputs
    should already be stored as JSON lines (one per parameter).
    This function is a passthrough for already-formatted inputs.
    """
    return raw_input
