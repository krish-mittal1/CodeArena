"""
Bot service — manage bot players, fallback matchmaking, and bot behavior.

Features:
  - Select random bot with similar ELO
  - Generate bot code submissions (correct/wrong variants)
  - Track bot match completion
"""

import random
import uuid
import logging
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.user import User
from backend.core.constants import Language

logger = logging.getLogger(__name__)

# Bot usernames — realistic looking but clearly labeled
BOT_USERNAMES = [
    "AlphaBot_7",
    "CodeNinja_Bot",
    "SilverCoder_AI",
    "LogicMaster_Bot",
    "PythonPro_AI",
    "AlgoWizard_Bot",
    "SmartSolver_7",
    "CyberCoder_AI",
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Bot Code Generators (correct and wrong solutions)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class BotCodeGenerator:
    """Generate realistic code solutions for different problem types."""
    
    @staticmethod
    def generate_solution(problem_title: str, language: str = Language.PYTHON) -> tuple[str, bool]:
        """
        Generate a bot solution.
        Returns (code, is_likely_correct) tuple.
        
        - 40% chance of correct solution
        - 60% chance of wrong/suboptimal solution
        """
        is_correct = random.random() < 0.4
        
        if language == Language.PYTHON:
            return BotCodeGenerator._python_solution(problem_title, is_correct)
        elif language == Language.CPP:
            return BotCodeGenerator._cpp_solution(problem_title, is_correct)
        elif language == Language.JAVA:
            return BotCodeGenerator._java_solution(problem_title, is_correct)
        elif language == Language.JAVASCRIPT:
            return BotCodeGenerator._js_solution(problem_title, is_correct)
        else:
            return BotCodeGenerator._python_solution(problem_title, is_correct)
    
    @staticmethod
    def _python_solution(problem_title: str, is_correct: bool) -> tuple[str, bool]:
        """Generate Python solution based on problem type."""
        title_lower = problem_title.lower()
        
        if "rotated" in title_lower or "search" in title_lower:
            code = """# Binary search on rotated array
def search(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        if nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1
""" if is_correct else """# Buggy linear search
def search(nums, target):
    for i in range(len(nums)):
        if nums[i] == target:
            return i
    return -1
"""
        
        elif "3sum" in title_lower or "sum" in title_lower:
            code = """# Two pointer approach
def threeSum(nums):
    nums.sort()
    result = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i-1]:
            continue
        left, right = i + 1, len(nums) - 1
        while left < right:
            s = nums[i] + nums[left] + nums[right]
            if s == 0:
                result.append([nums[i], nums[left], nums[right]])
                while left < right and nums[left] == nums[left+1]:
                    left += 1
                while left < right and nums[right] == nums[right-1]:
                    right -= 1
                left += 1
                right -= 1
            elif s < 0:
                left += 1
            else:
                right -= 1
    return result
""" if is_correct else """# Wrong approach (duplicates)
def threeSum(nums):
    nums.sort()
    return [[nums[i], nums[i+1], nums[i+2]] for i in range(len(nums) - 2)]
"""
        
        elif "longest" in title_lower or "substring" in title_lower:
            code = """# Sliding window
def lengthOfLongestSubstring(s):
    char_map = {}
    start = 0
    max_len = 0
    for i, char in enumerate(s):
        if char in char_map:
            start = max(start, char_map[char] + 1)
        char_map[char] = i
        max_len = max(max_len, i - start + 1)
    return max_len
""" if is_correct else """# Wrong (counts duplicates)
def lengthOfLongestSubstring(s):
    return len(set(s))
"""
        
        else:
            # Generic solution template
            code = """# Solution
def solve(x):
    return x
""" if is_correct else """# Incomplete solution
def solve(x):
    pass
"""
        
        return code, is_correct
    
    @staticmethod
    def _cpp_solution(problem_title: str, is_correct: bool) -> tuple[str, bool]:
        """Generate C++ solution."""
        code = """#include <vector>
using namespace std;

class Solution {
public:
    int search(vector<int>& nums, int target) {
        int left = 0, right = nums.size() - 1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (nums[mid] == target) return mid;
            if (nums[left] <= nums[mid]) {
                if (nums[left] <= target && target < nums[mid]) {
                    right = mid - 1;
                } else {
                    left = mid + 1;
                }
            } else {
                if (nums[mid] < target && target <= nums[right]) {
                    left = mid + 1;
                } else {
                    right = mid - 1;
                }
            }
        }
        return -1;
    }
};
""" if is_correct else """#include <vector>
using namespace std;

class Solution {
public:
    int search(vector<int>& nums, int target) {
        for (int i = 0; i < nums.size(); i++) {
            if (nums[i] == target) return i;
        }
        return -1;
    }
};
"""
        return code, is_correct
    
    @staticmethod
    def _java_solution(problem_title: str, is_correct: bool) -> tuple[str, bool]:
        """Generate Java solution."""
        code = """class Solution {
    public int search(int[] nums, int target) {
        int left = 0, right = nums.length - 1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (nums[mid] == target) return mid;
            if (nums[left] <= nums[mid]) {
                if (nums[left] <= target && target < nums[mid]) {
                    right = mid - 1;
                } else {
                    left = mid + 1;
                }
            } else {
                if (nums[mid] < target && target <= nums[right]) {
                    left = mid + 1;
                } else {
                    right = mid - 1;
                }
            }
        }
        return -1;
    }
}
""" if is_correct else """class Solution {
    public int search(int[] nums, int target) {
        for (int i = 0; i < nums.length; i++) {
            if (nums[i] == target) return i;
        }
        return -1;
    }
}
"""
        return code, is_correct
    
    @staticmethod
    def _js_solution(problem_title: str, is_correct: bool) -> tuple[str, bool]:
        """Generate JavaScript solution."""
        code = """/**
 * @param {number[]} nums
 * @param {number} target
 * @return {number}
 */
var search = function(nums, target) {
    let left = 0, right = nums.length - 1;
    while (left <= right) {
        let mid = Math.floor((left + right) / 2);
        if (nums[mid] === target) return mid;
        if (nums[left] <= nums[mid]) {
            if (nums[left] <= target && target < nums[mid]) {
                right = mid - 1;
            } else {
                left = mid + 1;
            }
        } else {
            if (nums[mid] < target && target <= nums[right]) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
    }
    return -1;
};
""" if is_correct else """var search = function(nums, target) {
    for (let i = 0; i < nums.length; i++) {
        if (nums[i] === target) return i;
    }
    return -1;
};
"""
        return code, is_correct


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Bot Selection and Management
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def get_all_bots(db: AsyncSession) -> List[User]:
    """Get all bot users from database."""
    result = await db.execute(
        select(User).where(User.is_bot == True)
    )
    return list(result.scalars().all())


async def get_random_bot_for_elo(db: AsyncSession, player_elo: int) -> Optional[User]:
    """Select a random bot with similar ELO (within ±200)."""
    min_elo = max(0, player_elo - 200)
    max_elo = player_elo + 200
    
    result = await db.execute(
        select(User).where(
            (User.is_bot == True) &
            (User.elo >= min_elo) &
            (User.elo <= max_elo)
        )
    )
    bots = list(result.scalars().all())
    
    if not bots:
        # Fallback: get any bot
        result = await db.execute(select(User).where(User.is_bot == True))
        bots = list(result.scalars().all())
    
    return random.choice(bots) if bots else None


async def is_bot_username_available(db: AsyncSession, username: str) -> bool:
    """Check if a bot username is already taken."""
    result = await db.execute(
        select(User).where(User.username == username)
    )
    return result.scalar_one_or_none() is None


async def create_bot_user(
    db: AsyncSession,
    username: str,
    initial_elo: int = 0,
) -> User:
    """Create a new bot user."""
    bot = User(
        username=username,
        email=f"{username}@bot.local",
        password_hash="",  # Bots don't authenticate
        is_bot=True,
        elo=initial_elo,
    )
    db.add(bot)
    await db.commit()
    await db.refresh(bot)
    logger.info(f"Created bot user: {username} (ELO={initial_elo})")
    return bot


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Bot Match Simulation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_bot_match_outcome() -> bool:
    """
    Determine if the bot will win or lose this match.
    Returns: True if bot wins, False if bot loses.
    
    - 50% win rate for realism
    """
    return random.random() < 0.5
