import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
os.environ["POSTGRES_USER"] = "postgres"  # dummy for config
os.environ["POSTGRES_PASSWORD"] = "postgres"
os.environ["POSTGRES_DB"] = "postgres"

from backend.execution.sandbox import sandbox

async def test_cpp():
    code = """#include <iostream>
using namespace std;
int main() {
    int a, b;
    if (cin >> a >> b) {
        cout << a + b << endl;
    }
    return 0;
}
"""
    print("Testing C++...")
    result = await sandbox.execute("cpp", code, "1 2\n")
    print(f"C++ result: {result.to_dict()}")

async def test_java():
    code = """import java.util.Scanner;
public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextInt()) {
            int a = sc.nextInt();
            int b = sc.nextInt();
            System.out.println(a + b);
        }
    }
}
"""
    print("Testing Java...")
    result = await sandbox.execute("java", code, "1 2\n")
    print(f"Java result: {result.to_dict()}")

async def test_js():
    code = """const fs = require('fs');
const input = fs.readFileSync('/dev/stdin', 'utf-8').trim().split(/\\s+/);
if (input.length >= 2) {
    console.log(parseInt(input[0]) + parseInt(input[1]));
}
"""
    print("Testing JS...")
    result = await sandbox.execute("javascript", code, "1 2\n")
    print(f"JS result: {result.to_dict()}")

async def test_py():
    code = """import sys
data = sys.stdin.read().split()
if len(data) >= 2:
    print(int(data[0]) + int(data[1]))
"""
    print("Testing Python...")
    result = await sandbox.execute("python", code, "1 2\n")
    print(f"Python result: {result.to_dict()}")

async def main():
    await test_py()
    await test_js()
    await test_cpp()
    await test_java()

if __name__ == "__main__":
    asyncio.run(main())
