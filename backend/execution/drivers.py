"""
LeetCode-style hidden driver generator.

Each generated driver:
1. Reads one JSON value per parameter from stdin
2. Deserializes into language-native values
3. Instantiates Solution
4. Calls the requested method
5. Serializes the return value back to JSON-like stdout

Special structures currently supported:
- ListNode
- TreeNode (LeetCode-style level-order arrays with nulls)
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


def _uses_listnode(parameters: List[Dict[str, str]], return_type: str) -> bool:
    return any(p.get("type") == "ListNode" for p in parameters) or return_type == "ListNode"


def _uses_treenode(parameters: List[Dict[str, str]], return_type: str) -> bool:
    return any(p.get("type") == "TreeNode" for p in parameters) or return_type == "TreeNode"


def _python_type_hint(param_type: str) -> str:
    mapping = {
        "int": "int",
        "long": "int",
        "int[]": "List[int]",
        "long[]": "List[int]",
        "int[][]": "List[List[int]]",
        "str": "str",
        "string": "str",
        "str[]": "List[str]",
        "string[]": "List[str]",
        "char[][]": "List[List[str]]",
        "string[][]": "List[List[str]]",
        "float": "float",
        "float[]": "List[float]",
        "bool": "bool",
        "boolean": "bool",
        "bool[]": "List[bool]",
        "boolean[]": "List[bool]",
        "ListNode": "Optional['ListNode']",
        "TreeNode": "Optional['TreeNode']",
    }
    return mapping.get(param_type, "Any")


def _cpp_type(param_type: str) -> str:
    mapping = {
        "int": "int",
        "long": "long long",
        "int[]": "vector<int>",
        "long[]": "vector<long long>",
        "int[][]": "vector<vector<int>>",
        "str": "string",
        "string": "string",
        "str[]": "vector<string>",
        "string[]": "vector<string>",
        "char[][]": "vector<vector<char>>",
        "string[][]": "vector<vector<string>>",
        "float": "double",
        "float[]": "vector<double>",
        "bool": "bool",
        "boolean": "bool",
        "bool[]": "vector<bool>",
        "boolean[]": "vector<bool>",
        "ListNode": "ListNode*",
        "TreeNode": "TreeNode*",
    }
    return mapping.get(param_type, "int")


def _java_type(param_type: str) -> str:
    mapping = {
        "int": "int",
        "long": "long",
        "int[]": "int[]",
        "long[]": "long[]",
        "int[][]": "int[][]",
        "str": "String",
        "string": "String",
        "str[]": "String[]",
        "string[]": "String[]",
        "char[][]": "char[][]",
        "string[][]": "String[][]",
        "float": "double",
        "float[]": "double[]",
        "bool": "boolean",
        "boolean": "boolean",
        "bool[]": "boolean[]",
        "boolean[]": "boolean[]",
        "ListNode": "ListNode",
        "TreeNode": "TreeNode",
    }
    return mapping.get(param_type, "int")


def _indent_python_reads(parameters: List[Dict[str, str]]) -> str:
    lines = ""
    for p in parameters:
        ptype = p.get("type")
        if ptype == "ListNode":
            lines += f"    {p['name']} = build_linked_list(json.loads(input_data[idx]))\n"
        elif ptype == "TreeNode":
            lines += f"    {p['name']} = build_tree(json.loads(input_data[idx]))\n"
        elif ptype == "char[][]":
            # Accept [["1","0"], ...] or legacy ["10","01"] string rows.
            lines += (
                f"    __raw_{p['name']} = json.loads(input_data[idx])\n"
                f"    if __raw_{p['name']} and isinstance(__raw_{p['name']}[0], str):\n"
                f"        {p['name']} = [list(row) for row in __raw_{p['name']}]\n"
                f"    else:\n"
                f"        {p['name']} = [[(c if isinstance(c, str) else str(c))[0] for c in row] for row in __raw_{p['name']}]\n"
            )
        else:
            lines += f"    {p['name']} = json.loads(input_data[idx])\n"
        lines += "    idx += 1\n"
    return lines


def generate_python_driver(method_name: str, parameters: List[Dict[str, str]], return_type: str) -> str:
    param_names = [p["name"] for p in parameters]
    call_args = ", ".join(param_names)
    uses_listnode = _uses_listnode(parameters, return_type)
    uses_treenode = _uses_treenode(parameters, return_type)

    listnode_helpers = ""
    if uses_listnode:
        listnode_helpers = """
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def build_linked_list(values):
    if values is None:
        return None
    dummy = ListNode(0)
    cur = dummy
    for value in values:
        cur.next = ListNode(value)
        cur = cur.next
    return dummy.next

def linked_list_to_array(head):
    out = []
    cur = head
    while cur is not None:
        out.append(cur.val)
        cur = cur.next
    return out
"""

    treenode_helpers = ""
    if uses_treenode:
        treenode_helpers = """
from collections import deque

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def build_tree(values):
    # LeetCode level-order: only non-null nodes own left/right slots.
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = deque([root])
    i = 1
    while queue and i < len(values):
        node = queue.popleft()
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1
    return root

def tree_to_array(root):
    if root is None:
        return []
    out = []
    queue = deque([root])
    while queue:
        node = queue.popleft()
        if node is None:
            out.append(None)
            continue
        out.append(node.val)
        queue.append(node.left)
        queue.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out
"""

    serializer_line = "    print(json.dumps(result))"
    if return_type == "ListNode":
        serializer_line = "    print(json.dumps(linked_list_to_array(result)))"
    elif return_type == "TreeNode":
        serializer_line = "    print(json.dumps(tree_to_array(result)))"
    elif return_type == "char[][]":
        serializer_line = (
            "    print(json.dumps([[c if isinstance(c, str) else str(c) for c in row] for row in result]))"
        )
    elif return_type == "string[][]":
        serializer_line = "    print(json.dumps(result))"

    return f"""import sys
import json

{listnode_helpers}
{treenode_helpers}

sys.path.insert(0, '/sandbox/in')
from solution import Solution

def main():
    input_data = sys.stdin.read().strip().split('\\n')
    idx = 0
{_indent_python_reads(parameters)}    sol = Solution()
    result = sol.{method_name}({call_args})
{serializer_line}

if __name__ == "__main__":
    main()
"""


def generate_javascript_driver(method_name: str, parameters: List[Dict[str, str]], return_type: str) -> str:
    param_names = [p["name"] for p in parameters]
    call_args = ", ".join(param_names)
    uses_listnode = _uses_listnode(parameters, return_type)
    uses_treenode = _uses_treenode(parameters, return_type)

    read_lines = ""
    for idx, p in enumerate(parameters):
        if p.get("type") == "ListNode":
            read_lines += f"    const {p['name']} = buildLinkedList(JSON.parse(lines[{idx}]));\n"
        elif p.get("type") == "TreeNode":
            read_lines += f"    const {p['name']} = buildTree(JSON.parse(lines[{idx}]));\n"
        elif p.get("type") == "char[][]":
            read_lines += (
                f"    let {p['name']} = JSON.parse(lines[{idx}]);\n"
                f"    if ({p['name']}.length && typeof {p['name']}[0] === 'string') "
                f"{p['name']} = {p['name']}.map(row => row.split(''));\n"
                f"    else {p['name']} = {p['name']}.map(row => row.map(c => String(c)[0]));\n"
            )
        else:
            read_lines += f"    const {p['name']} = JSON.parse(lines[{idx}]);\n"

    listnode_helpers = ""
    if uses_listnode:
        listnode_helpers = """
class ListNode {
    constructor(val = 0, next = null) {
        this.val = val;
        this.next = next;
    }
}

function buildLinkedList(values) {
    if (values == null) return null;
    const dummy = new ListNode(0);
    let cur = dummy;
    for (const value of values) {
        cur.next = new ListNode(value);
        cur = cur.next;
    }
    return dummy.next;
}

function linkedListToArray(head) {
    const out = [];
    let cur = head;
    while (cur) {
        out.push(cur.val);
        cur = cur.next;
    }
    return out;
}
"""

    treenode_helpers = ""
    if uses_treenode:
        treenode_helpers = """
class TreeNode {
    constructor(val = 0, left = null, right = null) {
        this.val = val;
        this.left = left;
        this.right = right;
    }
}

function buildTree(values) {
    // LeetCode level-order: only non-null nodes own left/right slots.
    if (!values || values.length === 0 || values[0] === null) return null;
    const root = new TreeNode(values[0]);
    const queue = [root];
    let i = 1;
    while (queue.length && i < values.length) {
        const node = queue.shift();
        if (i < values.length && values[i] !== null) {
            node.left = new TreeNode(values[i]);
            queue.push(node.left);
        }
        i++;
        if (i < values.length && values[i] !== null) {
            node.right = new TreeNode(values[i]);
            queue.push(node.right);
        }
        i++;
    }
    return root;
}

function treeToArray(root) {
    if (!root) return [];
    const queue = [root];
    const out = [];
    for (let idx = 0; idx < queue.length; idx++) {
        const node = queue[idx];
        if (!node) {
            out.push(null);
            continue;
        }
        out.push(node.val);
        queue.push(node.left ?? null);
        queue.push(node.right ?? null);
    }
    while (out.length && out[out.length - 1] === null) out.pop();
    return out;
}

globalThis.TreeNode = TreeNode;
"""

    result_printer = "    console.log(JSON.stringify(result));"
    if return_type == "ListNode":
        result_printer = "    console.log(JSON.stringify(linkedListToArray(result)));"
    elif return_type == "TreeNode":
        result_printer = "    console.log(JSON.stringify(treeToArray(result)));"

    # Expose ListNode globally when present so user code can construct nodes.
    listnode_global = "globalThis.ListNode = ListNode;\n" if uses_listnode else ""

    return f"""const fs = require('fs');
const raw = fs.readFileSync(0, 'utf8').trim();
const lines = raw ? raw.split('\\n') : [];

{listnode_helpers}
{listnode_global}{treenode_helpers}

const userModule = require('/sandbox/in/code.js');

let solution;
if (typeof userModule === 'function') {{
    solution = new userModule();
}} else if (userModule.Solution) {{
    solution = new userModule.Solution();
}} else if (typeof userModule.{method_name} === 'function') {{
    solution = userModule;
}} else {{
    solution = userModule;
}}

function main() {{
{read_lines}    let result;
    if (typeof solution.{method_name} === 'function') {{
        result = solution.{method_name}({call_args});
    }} else if (typeof solution === 'function') {{
        result = solution({call_args});
    }} else {{
        throw new Error('Cannot find method {method_name} in user code');
    }}
{result_printer}
}}

main();
"""


def _cpp_json_parser(param_type: str, var_name: str) -> str:
    if param_type == "int":
        return f"    int {var_name} = stoi(line);"
    if param_type == "long":
        return f"    long long {var_name} = stoll(line);"
    if param_type in {"str", "string"}:
        return f"    string {var_name} = parseJsonString(line);"
    if param_type == "int[]":
        return f"    vector<int> {var_name} = parseJsonIntArray(line);"
    if param_type == "long[]":
        return f"    vector<long long> {var_name} = parseJsonLongArray(line);"
    if param_type == "int[][]":
        return f"    vector<vector<int>> {var_name} = parseJson2DIntArray(line);"
    if param_type == "char[][]":
        return f"    vector<vector<char>> {var_name} = parseJson2DCharArray(line);"
    if param_type == "string[][]":
        return f"    vector<vector<string>> {var_name} = parseJson2DStringArray(line);"
    if param_type in {"str[]", "string[]"}:
        return f"    vector<string> {var_name} = parseJsonStringArray(line);"
    if param_type == "float":
        return f"    double {var_name} = stod(line);"
    if param_type in {"bool", "boolean"}:
        return f'    bool {var_name} = (line == "true");'
    if param_type == "ListNode":
        return (
            f"    vector<int> __{var_name}Vals = parseJsonIntArray(line);\n"
            f"    ListNode* {var_name} = buildLinkedList(__{var_name}Vals);"
        )
    if param_type == "TreeNode":
        return (
            f"    vector<optional<int>> __{var_name}Vals = parseJsonTreeArray(line);\n"
            f"    TreeNode* {var_name} = buildTree(__{var_name}Vals);"
        )
    return f"    int {var_name} = stoi(line);"


def _cpp_json_serializer(return_type: str) -> str:
    if return_type in {"int", "long"}:
        return "    cout << result << endl;"
    if return_type in {"str", "string"}:
        return '    cout << "\\"" << result << "\\"" << endl;'
    if return_type in {"bool", "boolean"}:
        return '    cout << (result ? "true" : "false") << endl;'
    if return_type == "float":
        return "    cout << fixed << setprecision(5) << result << endl;"
    if return_type == "int[]":
        return """    cout << "[";
    for (size_t i = 0; i < result.size(); i++) {
        if (i > 0) cout << ",";
        cout << result[i];
    }
    cout << "]" << endl;"""
    if return_type == "long[]":
        return """    cout << "[";
    for (size_t i = 0; i < result.size(); i++) {
        if (i > 0) cout << ",";
        cout << result[i];
    }
    cout << "]" << endl;"""
    if return_type == "int[][]":
        return """    cout << "[";
    for (size_t i = 0; i < result.size(); i++) {
        if (i > 0) cout << ",";
        cout << "[";
        for (size_t j = 0; j < result[i].size(); j++) {
            if (j > 0) cout << ",";
            cout << result[i][j];
        }
        cout << "]";
    }
    cout << "]" << endl;"""
    if return_type == "char[][]":
        return """    cout << "[";
    for (size_t i = 0; i < result.size(); i++) {
        if (i > 0) cout << ",";
        cout << "[";
        for (size_t j = 0; j < result[i].size(); j++) {
            if (j > 0) cout << ",";
            cout << "\\\"" << result[i][j] << "\\\"";
        }
        cout << "]";
    }
    cout << "]" << endl;"""
    if return_type == "string[][]":
        return """    cout << "[";
    for (size_t i = 0; i < result.size(); i++) {
        if (i > 0) cout << ",";
        cout << "[";
        for (size_t j = 0; j < result[i].size(); j++) {
            if (j > 0) cout << ",";
            cout << "\\\"" << result[i][j] << "\\\"";
        }
        cout << "]";
    }
    cout << "]" << endl;"""
    if return_type in {"str[]", "string[]"}:
        return """    cout << "[";
    for (size_t i = 0; i < result.size(); i++) {
        if (i > 0) cout << ",";
        cout << "\\\"" << result[i] << "\\\"";
    }
    cout << "]" << endl;"""
    if return_type == "ListNode":
        return """    cout << "[";
    ListNode* cur = result;
    bool first = true;
    while (cur != nullptr) {
        if (!first) cout << ",";
        cout << cur->val;
        first = false;
        cur = cur->next;
    }
    cout << "]" << endl;"""
    if return_type == "TreeNode":
        return "    cout << treeToJson(result) << endl;"
    return "    cout << result << endl;"


def generate_cpp_driver(method_name: str, parameters: List[Dict[str, str]], return_type: str) -> str:
    param_names = [p["name"] for p in parameters]
    call_args = ", ".join(param_names)
    uses_listnode = _uses_listnode(parameters, return_type)
    uses_treenode = _uses_treenode(parameters, return_type)

    read_blocks = ""
    for p in parameters:
        read_blocks += "    getline(cin, line);\n"
        read_blocks += _cpp_json_parser(p["type"], p["name"]) + "\n"

    listnode_defs = ""
    if uses_listnode:
        listnode_defs = """
struct ListNode {
    int val;
    ListNode* next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode* n) : val(x), next(n) {}
};

ListNode* buildLinkedList(const vector<int>& values) {
    ListNode dummy(0);
    ListNode* cur = &dummy;
    for (int value : values) {
        cur->next = new ListNode(value);
        cur = cur->next;
    }
    return dummy.next;
}
"""

    treenode_defs = ""
    if uses_treenode:
        treenode_defs = """
struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode() : val(0), left(nullptr), right(nullptr) {}
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
    TreeNode(int x, TreeNode* l, TreeNode* r) : val(x), left(l), right(r) {}
};

vector<optional<int>> parseJsonTreeArray(const string& s) {
    vector<optional<int>> res;
    string token;
    auto flush = [&]() {
        if (token.empty()) return;
        if (token == "null") res.push_back(nullopt);
        else res.push_back(stoi(token));
        token.clear();
    };
    for (char c : s) {
        if (c == '-' || isdigit(static_cast<unsigned char>(c))) {
            token += c;
        } else if (isalpha(static_cast<unsigned char>(c))) {
            token += c;
        } else {
            flush();
        }
    }
    flush();
    return res;
}

TreeNode* buildTree(const vector<optional<int>>& values) {
    // LeetCode level-order: only non-null nodes own left/right slots.
    if (values.empty() || !values[0].has_value()) return nullptr;
    TreeNode* root = new TreeNode(*values[0]);
    queue<TreeNode*> q;
    q.push(root);
    size_t i = 1;
    while (!q.empty() && i < values.size()) {
        TreeNode* node = q.front();
        q.pop();
        if (i < values.size()) {
            if (values[i].has_value()) {
                node->left = new TreeNode(*values[i]);
                q.push(node->left);
            }
            ++i;
        }
        if (i < values.size()) {
            if (values[i].has_value()) {
                node->right = new TreeNode(*values[i]);
                q.push(node->right);
            }
            ++i;
        }
    }
    return root;
}

string treeToJson(TreeNode* root) {
    if (!root) return "[]";
    vector<string> values;
    queue<TreeNode*> q;
    q.push(root);
    while (!q.empty()) {
        TreeNode* node = q.front();
        q.pop();
        if (!node) {
            values.push_back("null");
            continue;
        }
        values.push_back(to_string(node->val));
        q.push(node->left);
        q.push(node->right);
    }
    while (!values.empty() && values.back() == "null") values.pop_back();
    string out = "[";
    for (size_t i = 0; i < values.size(); ++i) {
        if (i > 0) out += ",";
        out += values[i];
    }
    out += "]";
    return out;
}
"""

    return f"""#include <bits/stdc++.h>
using namespace std;

string parseJsonString(const string& s) {{
    string res;
    bool inStr = false;
    for (size_t i = 0; i < s.size(); i++) {{
        if (s[i] == '"') {{ inStr = !inStr; continue; }}
        if (inStr) {{
            if (s[i] == '\\\\' && i + 1 < s.size()) {{ res += s[++i]; continue; }}
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
        if (c == '-' || isdigit(static_cast<unsigned char>(c))) {{
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

vector<long long> parseJsonLongArray(const string& s) {{
    vector<long long> res;
    string num;
    bool inNum = false;
    for (char c : s) {{
        if (c == '-' || isdigit(static_cast<unsigned char>(c))) {{
            num += c;
            inNum = true;
        }} else if (inNum) {{
            res.push_back(stoll(num));
            num.clear();
            inNum = false;
        }}
    }}
    if (inNum) res.push_back(stoll(num));
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
            if (s[i] != '\\r') current += s[i];
        }}
    }}
    return res;
}}

vector<vector<string>> parseJson2DStringArray(const string& s) {{
    vector<vector<string>> res;
    int depth = 0;
    bool inStr = false;
    string current;
    for (size_t i = 0; i < s.size(); i++) {{
        char c = s[i];
        if (c == '"' ) {{
            if (inStr) {{
                if (depth >= 2 && !res.empty()) res.back().push_back(current);
                current.clear();
            }}
            inStr = !inStr;
            continue;
        }}
        if (inStr) {{
            current += c;
            continue;
        }}
        if (c == '[') {{
            depth++;
            if (depth == 2) res.emplace_back();
        }} else if (c == ']') {{
            depth--;
        }}
    }}
    return res;
}}

vector<vector<char>> parseJson2DCharArray(const string& s) {{
    string trimmed = s;
    while (!trimmed.empty() && isspace(static_cast<unsigned char>(trimmed.front()))) trimmed.erase(trimmed.begin());
    while (!trimmed.empty() && isspace(static_cast<unsigned char>(trimmed.back()))) trimmed.pop_back();
    size_t look = 1;
    while (look < trimmed.size() && isspace(static_cast<unsigned char>(trimmed[look]))) look++;
    bool nested = trimmed.size() >= 2 && trimmed[0] == '[' && look < trimmed.size() && trimmed[look] == '[';

    if (!nested) {{
        vector<string> rows = parseJsonStringArray(s);
        vector<vector<char>> res;
        for (const auto& row : rows) {{
            res.emplace_back(row.begin(), row.end());
        }}
        return res;
    }}

    vector<vector<string>> cells = parseJson2DStringArray(s);
    vector<vector<char>> res;
    res.reserve(cells.size());
    for (const auto& row : cells) {{
        vector<char> out;
        out.reserve(row.size());
        for (const auto& cell : row) {{
            out.push_back(cell.empty() ? '\\0' : cell[0]);
        }}
        res.push_back(std::move(out));
    }}
    return res;
}}

{listnode_defs}
{treenode_defs}

#include "/sandbox/code.cpp"

int main() {{
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);

    string line;
{read_blocks}    Solution sol;
    {_cpp_type(return_type)} result = sol.{method_name}({call_args});

{_cpp_json_serializer(return_type)}
    return 0;
}}
"""


def _java_json_parser(param_type: str, var_name: str) -> str:
    if param_type == "int":
        return f"        int {var_name} = Integer.parseInt(lines[idx++].trim());"
    if param_type == "long":
        return f"        long {var_name} = Long.parseLong(lines[idx++].trim());"
    if param_type in {"str", "string"}:
        return f"        String {var_name} = parseJsonString(lines[idx++].trim());"
    if param_type == "int[]":
        return f"        int[] {var_name} = parseJsonIntArray(lines[idx++].trim());"
    if param_type == "long[]":
        return f"        long[] {var_name} = parseJsonLongArray(lines[idx++].trim());"
    if param_type == "int[][]":
        return f"        int[][] {var_name} = parseJson2DIntArray(lines[idx++].trim());"
    if param_type == "char[][]":
        return f"        char[][] {var_name} = parseJson2DCharArray(lines[idx++].trim());"
    if param_type == "string[][]":
        return f"        String[][] {var_name} = parseJson2DStringArray(lines[idx++].trim());"
    if param_type in {"str[]", "string[]"}:
        return f"        String[] {var_name} = parseJsonStringArray(lines[idx++].trim());"
    if param_type in {"bool", "boolean"}:
        return f'        boolean {var_name} = lines[idx++].trim().equals("true");'
    if param_type == "float":
        return f"        double {var_name} = Double.parseDouble(lines[idx++].trim());"
    if param_type == "ListNode":
        return f"        ListNode {var_name} = buildLinkedList(parseJsonIntArray(lines[idx++].trim()));"
    if param_type == "TreeNode":
        return f"        TreeNode {var_name} = buildTree(parseJsonTreeArray(lines[idx++].trim()));"
    return f"        int {var_name} = Integer.parseInt(lines[idx++].trim());"


def _java_json_serializer(return_type: str) -> str:
    if return_type in {"int", "long"}:
        return "        System.out.println(result);"
    if return_type in {"str", "string"}:
        return '        System.out.println("\\"" + result + "\\"");'
    if return_type in {"bool", "boolean"}:
        return '        System.out.println(result ? "true" : "false");'
    if return_type == "float":
        return "        System.out.println(result);"
    if return_type == "int[]":
        return """        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < result.length; i++) {
            if (i > 0) sb.append(",");
            sb.append(result[i]);
        }
        sb.append("]");
        System.out.println(sb.toString());"""
    if return_type == "long[]":
        return """        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < result.length; i++) {
            if (i > 0) sb.append(",");
            sb.append(result[i]);
        }
        sb.append("]");
        System.out.println(sb.toString());"""
    if return_type == "int[][]":
        return """        StringBuilder sb = new StringBuilder("[");
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
        System.out.println(sb.toString());"""
    if return_type == "char[][]":
        return """        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < result.length; i++) {
            if (i > 0) sb.append(",");
            sb.append("[");
            for (int j = 0; j < result[i].length; j++) {
                if (j > 0) sb.append(",");
                sb.append("\\\"").append(result[i][j]).append("\\\"");
            }
            sb.append("]");
        }
        sb.append("]");
        System.out.println(sb.toString());"""
    if return_type == "string[][]":
        return """        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < result.length; i++) {
            if (i > 0) sb.append(",");
            sb.append("[");
            for (int j = 0; j < result[i].length; j++) {
                if (j > 0) sb.append(",");
                sb.append("\\\"").append(result[i][j]).append("\\\"");
            }
            sb.append("]");
        }
        sb.append("]");
        System.out.println(sb.toString());"""
    if return_type in {"str[]", "string[]"}:
        return """        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < result.length; i++) {
            if (i > 0) sb.append(",");
            sb.append("\\\"").append(result[i]).append("\\\"");
        }
        sb.append("]");
        System.out.println(sb.toString());"""
    if return_type == "ListNode":
        return """        StringBuilder sb = new StringBuilder("[");
        ListNode cur = result;
        boolean first = true;
        while (cur != null) {
            if (!first) sb.append(",");
            sb.append(cur.val);
            first = false;
            cur = cur.next;
        }
        sb.append("]");
        System.out.println(sb.toString());"""
    if return_type == "TreeNode":
        return "        System.out.println(treeToJson(result));"
    return "        System.out.println(result);"


def generate_java_driver(method_name: str, parameters: List[Dict[str, str]], return_type: str) -> str:
    param_names = [p["name"] for p in parameters]
    call_args = ", ".join(param_names)
    uses_listnode = _uses_listnode(parameters, return_type)
    uses_treenode = _uses_treenode(parameters, return_type)

    read_blocks = ""
    for p in parameters:
        read_blocks += _java_json_parser(p["type"], p["name"]) + "\n"

    listnode_defs = ""
    if uses_listnode:
        listnode_defs = """
class ListNode {
    int val;
    ListNode next;
    ListNode() {}
    ListNode(int val) { this.val = val; }
    ListNode(int val, ListNode next) { this.val = val; this.next = next; }
}
"""

    treenode_defs = ""
    if uses_treenode:
        treenode_defs = """
class TreeNode {
    int val;
    TreeNode left;
    TreeNode right;
    TreeNode() {}
    TreeNode(int val) { this.val = val; }
    TreeNode(int val, TreeNode left, TreeNode right) { this.val = val; this.left = left; this.right = right; }
}
"""

    return f"""import java.util.*;
import java.io.*;

{listnode_defs}
{treenode_defs}

public class Main {{

    static String parseJsonString(String s) {{
        s = s.trim();
        if (s.startsWith("\\\"") && s.endsWith("\\\"")) return s.substring(1, s.length() - 1);
        return s;
    }}

    static int[] parseJsonIntArray(String s) {{
        s = s.trim();
        if (s.equals("[]") || s.equals("null") || s.isEmpty()) return new int[0];
        s = s.substring(1, s.length() - 1);
        if (s.isEmpty()) return new int[0];
        String[] parts = s.split(",");
        int[] res = new int[parts.length];
        for (int i = 0; i < parts.length; i++) res[i] = Integer.parseInt(parts[i].trim());
        return res;
    }}

    static long[] parseJsonLongArray(String s) {{
        s = s.trim();
        if (s.equals("[]") || s.equals("null") || s.isEmpty()) return new long[0];
        s = s.substring(1, s.length() - 1);
        if (s.isEmpty()) return new long[0];
        String[] parts = s.split(",");
        long[] res = new long[parts.length];
        for (int i = 0; i < parts.length; i++) res[i] = Long.parseLong(parts[i].trim());
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
                if (depth == 2) list.add(parseJsonIntArray("[" + current + "]"));
                depth--;
            }} else if (depth == 2) {{
                current.append(c);
            }}
        }}
        return list.toArray(new int[0][]);
    }}

    static char[][] parseJson2DCharArray(String s) {{
        s = s.trim();
        if (s.equals("[]")) return new char[0][];
        int look = 1;
        while (look < s.length() && Character.isWhitespace(s.charAt(look))) look++;
        boolean nested = s.startsWith("[") && look < s.length() && s.charAt(look) == '[';
        if (!nested) {{
            String[] rows = parseJsonStringArray(s);
            char[][] res = new char[rows.length][];
            for (int i = 0; i < rows.length; i++) res[i] = rows[i].toCharArray();
            return res;
        }}
        String[][] cells = parseJson2DStringArray(s);
        char[][] res = new char[cells.length][];
        for (int i = 0; i < cells.length; i++) {{
            res[i] = new char[cells[i].length];
            for (int j = 0; j < cells[i].length; j++) {{
                res[i][j] = cells[i][j].isEmpty() ? '\\0' : cells[i][j].charAt(0);
            }}
        }}
        return res;
    }}

    static String[][] parseJson2DStringArray(String s) {{
        s = s.trim();
        if (s.equals("[]")) return new String[0][];
        List<List<String>> list = new ArrayList<>();
        int depth = 0;
        boolean inStr = false;
        StringBuilder current = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {{
            char c = s.charAt(i);
            if (c == '"') {{
                if (inStr) {{
                    if (depth >= 2 && !list.isEmpty()) list.get(list.size() - 1).add(current.toString());
                    current = new StringBuilder();
                }}
                inStr = !inStr;
            }} else if (inStr) {{
                current.append(c);
            }} else if (c == '[') {{
                depth++;
                if (depth == 2) list.add(new ArrayList<>());
            }} else if (c == ']') {{
                depth--;
            }}
        }}
        String[][] res = new String[list.size()][];
        for (int i = 0; i < list.size(); i++) res[i] = list.get(i).toArray(new String[0]);
        return res;
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

    static Integer[] parseJsonTreeArray(String s) {{
        s = s.trim();
        if (s.equals("[]") || s.equals("null") || s.isEmpty()) return new Integer[0];
        s = s.substring(1, s.length() - 1).trim();
        if (s.isEmpty()) return new Integer[0];
        String[] parts = s.split(",");
        Integer[] values = new Integer[parts.length];
        for (int i = 0; i < parts.length; i++) {{
            String token = parts[i].trim();
            values[i] = token.equals("null") ? null : Integer.parseInt(token);
        }}
        return values;
    }}

    static ListNode buildLinkedList(int[] values) {{
        ListNode dummy = new ListNode(0);
        ListNode cur = dummy;
        for (int value : values) {{
            cur.next = new ListNode(value);
            cur = cur.next;
        }}
        return dummy.next;
    }}

    static TreeNode buildTree(Integer[] values) {{
        // LeetCode level-order: only non-null nodes own left/right slots.
        if (values.length == 0 || values[0] == null) return null;
        TreeNode root = new TreeNode(values[0]);
        Queue<TreeNode> queue = new LinkedList<>();
        queue.add(root);
        int i = 1;
        while (!queue.isEmpty() && i < values.length) {{
            TreeNode node = queue.poll();
            if (i < values.length) {{
                if (values[i] != null) {{
                    node.left = new TreeNode(values[i]);
                    queue.add(node.left);
                }}
                i++;
            }}
            if (i < values.length) {{
                if (values[i] != null) {{
                    node.right = new TreeNode(values[i]);
                    queue.add(node.right);
                }}
                i++;
            }}
        }}
        return root;
    }}

    static String treeToJson(TreeNode root) {{
        if (root == null) return "[]";
        List<String> values = new ArrayList<>();
        LinkedList<TreeNode> queue = new LinkedList<>();
        queue.add(root);
        while (!queue.isEmpty()) {{
            TreeNode node = queue.poll();
            if (node == null) {{
                values.add("null");
                continue;
            }}
            values.add(String.valueOf(node.val));
            queue.add(node.left);
            queue.add(node.right);
        }}
        while (!values.isEmpty() && values.get(values.size() - 1).equals("null")) {{
            values.remove(values.size() - 1);
        }}
        return "[" + String.join(",", values) + "]";
    }}

    public static void main(String[] args) throws Exception {{
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder rawBuilder = new StringBuilder();
        String lineRead;
        while ((lineRead = br.readLine()) != null) rawBuilder.append(lineRead).append("\\n");
        String raw = rawBuilder.toString().trim();
        String[] lines = raw.isEmpty() ? new String[0] : raw.split("\\n");
        int idx = 0;

{read_blocks}        Solution sol = new Solution();
        {_java_type(return_type)} result = sol.{method_name}({call_args});

{_java_json_serializer(return_type)}
    }}
}}
"""


def generate_driver(language: str, method_name: str, parameters: List[Dict[str, str]], return_type: str) -> Optional[str]:
    if not method_name or not parameters or not return_type:
        return None

    generators = {
        "python": generate_python_driver,
        "cpp": generate_cpp_driver,
        "java": generate_java_driver,
        "javascript": generate_javascript_driver,
    }
    generator = generators.get(language)
    if not generator:
        logger.warning("No driver generator for language: %s", language)
        return None
    return generator(method_name, parameters, return_type)


def convert_test_input_to_json(raw_input: str, parameters: List[Dict[str, str]]) -> str:
    return raw_input
