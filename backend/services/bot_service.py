"""
Bot service - manage fallback opponents, bot profiles, and bot behavior.

The goal is not to make bots perfect. The goal is to make them feel like
believable coding opponents with:
  - stable identities
  - skill levels tied to ELO
  - realistic timing
  - topic-aware strengths and mistakes
"""

from __future__ import annotations

import hashlib
import logging
import random
import uuid
from dataclasses import dataclass
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.constants import Difficulty, Language
from backend.models.user import User

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BotProfile:
    username: str
    elo: int
    preferred_languages: tuple[str, ...]
    confidence: float
    speed: float
    strengths: tuple[str, ...]
    vibe: str = "clean"


BOT_PROFILES: tuple[BotProfile, ...] = (
    BotProfile("AaravCodes", 100, (Language.PYTHON, Language.JAVASCRIPT), 0.24, 0.78, ("arrays", "basic"), "clean"),
    BotProfile("KavyaLoops", 200, (Language.PYTHON, Language.CPP), 0.33, 0.82, ("strings", "sliding window"), "clean"),
    BotProfile("RohanBuilds", 300, (Language.CPP, Language.PYTHON), 0.43, 0.9, ("two pointers", "binary search"), "clean"),
    BotProfile("IshitaLogic", 400, (Language.PYTHON, Language.JAVA), 0.53, 1.0, ("linked list", "greedy"), "clean"),
    BotProfile("NeelStack", 500, (Language.CPP, Language.PYTHON), 0.62, 1.08, ("intervals", "greedy", "arrays"), "clean"),
    BotProfile("AnayaDev", 600, (Language.PYTHON, Language.CPP), 0.72, 1.14, ("sliding window", "prefix sum", "trees"), "clean"),
    BotProfile("KabirCodes", 700, (Language.CPP, Language.JAVA), 0.81, 1.2, ("binary search", "graphs", "dp"), "clean"),
    BotProfile("SiyaByte", 800, (Language.CPP, Language.PYTHON), 0.9, 1.28, ("linked list", "dp", "graphs", "two pointers"), "clean"),
)

BOT_USERNAMES = [profile.username for profile in BOT_PROFILES]
BOT_PROFILE_BY_USERNAME = {profile.username: profile for profile in BOT_PROFILES}


def _stable_index(seed: str, size: int) -> int:
    if size <= 0:
        return 0
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % size


def _difficulty_modifier(difficulty: Optional[str]) -> float:
    value = str(difficulty or Difficulty.MEDIUM).lower()
    if value == Difficulty.EASY:
        return 0.12
    if value == Difficulty.HARD:
        return -0.15
    return 0.0


def _topic_bonus(problem_title: str, profile: BotProfile) -> float:
    title_lower = problem_title.lower()
    for topic in profile.strengths:
        if topic in title_lower:
            return 0.08

    if "substring" in title_lower and "sliding window" in profile.strengths:
        return 0.08
    if "window" in title_lower and "sliding window" in profile.strengths:
        return 0.08
    if "linked" in title_lower and "linked list" in profile.strengths:
        return 0.08
    if "search" in title_lower and "binary search" in profile.strengths:
        return 0.08
    if "jump" in title_lower and "greedy" in profile.strengths:
        return 0.08
    return 0.0


def get_profile_for_username(username: str) -> Optional[BotProfile]:
    return BOT_PROFILE_BY_USERNAME.get(username)


def choose_language(profile: BotProfile, problem_title: str, attempt_index: int = 0) -> str:
    languages = profile.preferred_languages or (Language.PYTHON,)
    idx = _stable_index(f"{profile.username}:{problem_title}:{attempt_index}", len(languages))
    return languages[idx]


def get_bot_submit_delay_seconds(
    profile: BotProfile,
    difficulty: Optional[str],
    attempt_index: int,
    match_duration_seconds: int,
) -> int:
    difficulty_value = str(difficulty or Difficulty.MEDIUM).lower()
    base = {
        Difficulty.EASY: 18,
        Difficulty.MEDIUM: 34,
        Difficulty.HARD: 58,
    }.get(difficulty_value, 34)

    speed_factor = max(profile.speed, 0.65)
    delay = int(base / speed_factor)

    if attempt_index > 0:
        delay = max(8, int(delay * 0.55))

    return min(delay, max(12, match_duration_seconds // 3))


def get_bot_max_attempts(profile: BotProfile, difficulty: Optional[str]) -> int:
    if profile.confidence >= 0.72:
        return 2
    if profile.confidence >= 0.55 and str(difficulty or "").lower() != Difficulty.HARD:
        return 2
    return 1


def get_correctness_probability(
    profile: BotProfile,
    problem_title: str,
    difficulty: Optional[str],
    attempt_index: int,
) -> float:
    probability = profile.confidence
    probability += _difficulty_modifier(difficulty)
    probability += _topic_bonus(problem_title, profile)
    probability += attempt_index * 0.12
    return max(0.12, min(probability, 0.96))


def _rng_for_submission(profile: BotProfile, problem_title: str, difficulty: Optional[str], attempt_index: int) -> random.Random:
    seed = f"{profile.username}:{problem_title}:{difficulty}:{attempt_index}"
    return random.Random(seed)


class BotCodeGenerator:
    """Generate code that feels like it came from different opponent skill levels."""

    @staticmethod
    def generate_solution(
        problem_title: str,
        language: str = Language.PYTHON,
        difficulty: Optional[str] = Difficulty.MEDIUM,
        bot_profile: Optional[BotProfile] = None,
        attempt_index: int = 0,
    ) -> tuple[str, bool]:
        profile = bot_profile or BOT_PROFILES[0]
        probability = get_correctness_probability(profile, problem_title, difficulty, attempt_index)
        rng = _rng_for_submission(profile, problem_title, difficulty, attempt_index)
        is_correct = rng.random() < probability

        if language == Language.PYTHON:
            return BotCodeGenerator._python_solution(problem_title, is_correct)
        if language == Language.CPP:
            return BotCodeGenerator._cpp_solution(problem_title, is_correct)
        if language == Language.JAVA:
            return BotCodeGenerator._java_solution(problem_title, is_correct)
        if language == Language.JAVASCRIPT:
            return BotCodeGenerator._js_solution(problem_title, is_correct)
        return BotCodeGenerator._python_solution(problem_title, is_correct)

    @staticmethod
    def _python_solution(problem_title: str, is_correct: bool) -> tuple[str, bool]:
        title_lower = problem_title.lower()

        if "rotated" in title_lower and "minimum" in title_lower:
            code = """class Solution:
    def findMin(self, nums):
        left, right = 0, len(nums) - 1
        while left < right:
            mid = (left + right) // 2
            if nums[mid] > nums[right]:
                left = mid + 1
            else:
                right = mid
        return nums[left]
""" if is_correct else """class Solution:
    def findMin(self, nums):
        return min(nums[:-1])
"""
        elif "rotated" in title_lower or "search" in title_lower:
            code = """class Solution:
    def search(self, nums, target):
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
""" if is_correct else """class Solution:
    def search(self, nums, target):
        for i, value in enumerate(nums):
            if value == target:
                return i
        return -1
"""
        elif "minimum window substring" in title_lower:
            code = """from collections import Counter

class Solution:
    def minWindow(self, s, t):
        need = Counter(t)
        missing = len(t)
        left = start = end = 0

        for right, ch in enumerate(s, 1):
            if need[ch] > 0:
                missing -= 1
            need[ch] -= 1

            while missing == 0:
                if end == 0 or right - left < end - start:
                    start, end = left, right
                need[s[left]] += 1
                if need[s[left]] > 0:
                    missing += 1
                left += 1

        return s[start:end]
""" if is_correct else """class Solution:
    def minWindow(self, s, t):
        return t if t in s else ""
"""
        elif "permutation in string" in title_lower:
            code = """from collections import Counter

class Solution:
    def checkInclusion(self, s1, s2):
        need = Counter(s1)
        window = Counter()
        left = 0

        for right, ch in enumerate(s2):
            window[ch] += 1
            if right - left + 1 > len(s1):
                window[s2[left]] -= 1
                if window[s2[left]] == 0:
                    del window[s2[left]]
                left += 1
            if window == need:
                return True
        return False
""" if is_correct else """class Solution:
    def checkInclusion(self, s1, s2):
        return sorted(s1) == sorted(s2)
"""
        elif "substring" in title_lower or "window" in title_lower:
            code = """class Solution:
    def lengthOfLongestSubstring(self, s):
        last_seen = {}
        left = 0
        best = 0
        for right, ch in enumerate(s):
            if ch in last_seen and last_seen[ch] >= left:
                left = last_seen[ch] + 1
            last_seen[ch] = right
            best = max(best, right - left + 1)
        return best
""" if is_correct else """class Solution:
    def lengthOfLongestSubstring(self, s):
        return len(set(s))
"""
        elif "linked list" in title_lower and "reverse" in title_lower:
            code = """class Solution:
    def reverseList(self, head):
        prev = None
        current = head
        while current:
            nxt = current.next
            current.next = prev
            prev = current
            current = nxt
        return prev
""" if is_correct else """class Solution:
    def reverseList(self, head):
        return head
"""
        elif "merge two sorted lists" in title_lower:
            code = """class Solution:
    def mergeTwoLists(self, list1, list2):
        dummy = ListNode(0)
        tail = dummy
        while list1 and list2:
            if list1.val <= list2.val:
                tail.next = list1
                list1 = list1.next
            else:
                tail.next = list2
                list2 = list2.next
            tail = tail.next
        tail.next = list1 or list2
        return dummy.next
""" if is_correct else """class Solution:
    def mergeTwoLists(self, list1, list2):
        return list1 or list2
"""
        elif "3 sum" in title_lower or "3sum" in title_lower:
            code = """class Solution:
    def threeSum(self, nums):
        nums.sort()
        answer = []
        for i in range(len(nums) - 2):
            if i > 0 and nums[i] == nums[i - 1]:
                continue
            left, right = i + 1, len(nums) - 1
            while left < right:
                total = nums[i] + nums[left] + nums[right]
                if total == 0:
                    answer.append([nums[i], nums[left], nums[right]])
                    left += 1
                    right -= 1
                    while left < right and nums[left] == nums[left - 1]:
                        left += 1
                    while left < right and nums[right] == nums[right + 1]:
                        right -= 1
                elif total < 0:
                    left += 1
                else:
                    right -= 1
        return answer
""" if is_correct else """class Solution:
    def threeSum(self, nums):
        nums.sort()
        return [nums[:3]] if len(nums) >= 3 else []
"""
        elif "container" in title_lower or "rain water" in title_lower:
            code = """class Solution:
    def maxArea(self, height):
        left, right = 0, len(height) - 1
        best = 0
        while left < right:
            best = max(best, (right - left) * min(height[left], height[right]))
            if height[left] < height[right]:
                left += 1
            else:
                right -= 1
        return best
""" if is_correct else """class Solution:
    def maxArea(self, height):
        return max(height)
"""
        elif "jump game ii" in title_lower:
            code = """class Solution:
    def jump(self, nums):
        jumps = 0
        current_end = 0
        farthest = 0
        for i in range(len(nums) - 1):
            farthest = max(farthest, i + nums[i])
            if i == current_end:
                jumps += 1
                current_end = farthest
        return jumps
""" if is_correct else """class Solution:
    def jump(self, nums):
        return len(nums) - 1
"""
        elif "jump game" in title_lower:
            code = """class Solution:
    def canJump(self, nums):
        reach = 0
        for i, jump in enumerate(nums):
            if i > reach:
                return False
            reach = max(reach, i + jump)
        return True
""" if is_correct else """class Solution:
    def canJump(self, nums):
        return nums[0] > 0
"""
        else:
            code = """class Solution:
    def solve(self, x):
        return x
""" if is_correct else """class Solution:
    def solve(self, x):
        return None
"""

        return code, is_correct

    @staticmethod
    def _cpp_solution(problem_title: str, is_correct: bool) -> tuple[str, bool]:
        title_lower = problem_title.lower()
        if "linked list" in title_lower or "reverse" in title_lower:
            code = """class Solution {
public:
    ListNode* reverseList(ListNode* head) {
        ListNode* prev = nullptr;
        while (head) {
            ListNode* nextNode = head->next;
            head->next = prev;
            prev = head;
            head = nextNode;
        }
        return prev;
    }
};
""" if is_correct else """class Solution {
public:
    ListNode* reverseList(ListNode* head) {
        return head;
    }
};
"""
        else:
            code = """#include <vector>
using namespace std;

class Solution {
public:
    int search(vector<int>& nums, int target) {
        int left = 0, right = (int)nums.size() - 1;
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
        for (int i = 0; i < (int)nums.size(); i++) {
            if (nums[i] == target) return i;
        }
        return -1;
    }
};
"""
        return code, is_correct

    @staticmethod
    def _java_solution(problem_title: str, is_correct: bool) -> tuple[str, bool]:
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
        code = """/**
 * @param {number[]} nums
 * @param {number} target
 * @return {number}
 */
var search = function(nums, target) {
    let left = 0;
    let right = nums.length - 1;
    while (left <= right) {
        const mid = Math.floor((left + right) / 2);
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


async def get_all_bots(db: AsyncSession) -> List[User]:
    result = await db.execute(select(User).where(User.is_bot == True))
    return list(result.scalars().all())


async def get_random_bot_for_elo(
    db: AsyncSession,
    player_elo: int,
    player_hint: Optional[str] = None,
) -> Optional[User]:
    """
    Select a believable opponent:
      - close ELO first
      - deterministic per player if player_hint is provided
      - stable identity instead of pure randomness
    """
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
        result = await db.execute(select(User).where(User.is_bot == True))
        bots = list(result.scalars().all())

    if not bots:
        return None

    bots.sort(key=lambda bot: (abs(bot.elo - player_elo), bot.username))

    if player_hint:
        top_pool = bots[: min(3, len(bots))]
        return top_pool[_stable_index(player_hint, len(top_pool))]

    return random.choice(bots)


async def is_bot_username_available(db: AsyncSession, username: str) -> bool:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none() is None


async def create_bot_user(
    db: AsyncSession,
    username: str,
    initial_elo: int = 0,
) -> User:
    bot = User(
        username=username,
        email=f"{username.lower()}@bot.local",
        password_hash="",
        is_bot=True,
        elo=initial_elo,
    )
    db.add(bot)
    await db.commit()
    await db.refresh(bot)
    logger.info("Created bot user: %s (ELO=%s)", username, initial_elo)
    return bot


def get_bot_match_outcome(profile: Optional[BotProfile] = None) -> bool:
    confidence = profile.confidence if profile else 0.5
    return random.random() < confidence
