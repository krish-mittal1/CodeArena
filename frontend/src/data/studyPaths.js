/**
 * Curated interview study paths — titles matched against problem catalog at runtime.
 */

export const STUDY_PATHS = [
    {
        id: 'core-30',
        title: 'Core Interview 30',
        description: 'Essential patterns asked at most tech interviews. Start here.',
        problems: [
            'Two Sum', 'Valid Anagram', 'Valid Palindrome', 'Best Time to Buy and Sell Stock',
            'Contains Duplicate', 'Product of Array Except Self', 'Maximum Subarray',
            'Merge Intervals', '3 Sum', 'Container With Most Water',
            'Longest Substring Without Repeating Characters', 'Minimum Window Substring',
            'Group Anagrams', 'Longest Palindromic Substring',
            'Binary Tree Level Order Traversal', 'Invert Binary Tree', 'Maximum Depth of Binary Tree',
            'Lowest Common Ancestor of a Binary Tree', 'Validate Binary Search Tree',
            'Merge Two Sorted Lists', 'Reverse Linked List', 'Add Two Numbers',
            'Search in Rotated Sorted Array', 'Find Minimum in Rotated Sorted Array',
            'Jump Game', 'Word Break', 'Gas Station',
            'Decode String', 'Task Scheduler', 'IPO',
        ].map((title, i) => ({ title, day: Math.floor(i / 2) + 1 })),
    },
    {
        id: 'faang-30-day',
        title: 'FAANG 30-Day Ramp',
        description: 'Easy → medium progression over 30 days. Two problems per day.',
        problems: [
            'Two Sum', 'Valid Palindrome', 'Merge Sorted Array', 'Move Zeroes',
            'Contains Duplicate', 'Best Time to Buy and Sell Stock', 'Maximum Subarray',
            'Product of Array Except Self', 'Merge Intervals', '3 Sum',
            'Longest Substring Without Repeating Characters', 'Group Anagrams',
            'Binary Tree Level Order Traversal', 'Invert Binary Tree', 'Same Tree',
            'Maximum Depth of Binary Tree', 'Path Sum', 'Lowest Common Ancestor of a Binary Tree',
            'Merge Two Sorted Lists', 'Reverse Linked List', 'Middle of the Linked List',
            'Search in Rotated Sorted Array', 'Find First and Last Position of Element in Sorted Array',
            'Word Break', 'Jump Game', 'House Robber III',
            'Set Matrix Zeroes', 'Print the matrix in spiral manner', 'Rotate Array', 'Trapping Rain Water',
        ].map((title, i) => ({ title, day: i + 1 })),
    },
    {
        id: 'google-sprint',
        title: 'Google Sprint',
        description: '15 high-frequency problems for Google-style interviews.',
        company: 'Google',
        problems: [
            'Two Sum', 'Merge Intervals', 'Binary Tree Level Order Traversal',
            'Invert Binary Tree', 'Lowest Common Ancestor of a Binary Tree',
            'Longest Substring Without Repeating Characters', 'Container With Most Water',
            'Product of Array Except Self', 'Word Break', 'Jump Game',
            'Search in Rotated Sorted Array', 'Valid Anagram', '3 Sum',
            'Maximum Subarray', 'Merge Two Sorted Lists',
        ].map((title, i) => ({ title, day: i + 1 })),
    },
];

export function resolvePathProgress(path, catalog, solvedIds) {
    const solvedSet = new Set(solvedIds || []);
    const byTitle = Object.fromEntries((catalog || []).map((p) => [p.title, p]));
    const items = path.problems.map((entry) => {
        const prob = byTitle[entry.title];
        return {
            ...entry,
            problem_id: prob?.id,
            difficulty: prob?.difficulty,
            solved: prob ? solvedSet.has(prob.id) : false,
            found: !!prob,
        };
    });
    const found = items.filter((i) => i.found);
    const solved = found.filter((i) => i.solved).length;
    return {
        items,
        total: found.length,
        solved,
        pct: found.length ? Math.round((100 * solved) / found.length) : 0,
    };
}
