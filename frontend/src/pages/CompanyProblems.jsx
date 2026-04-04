import { useMemo, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Building2, Check, Clock, Code2, Play, Search, Terminal, ChevronRight, Zap } from 'lucide-react';
import { COMPANIES } from '../utils/companies';
import { problemApi } from '../api/auth';
import CompanyLogo from '../components/ui/CompanyLogo';

function normalizeCompanyName(value) {
    return (value || '').toLowerCase().replace(/[^a-z0-9]/g, '');
}

function companyNameMatches(datasetName, mappedName) {
    const dataset = normalizeCompanyName(datasetName);
    const mapped = normalizeCompanyName(mappedName);

    if (!dataset || !mapped) return false;
    return dataset === mapped || dataset.includes(mapped) || mapped.includes(dataset);
}

function companyNamesFor(...categories) {
    return COMPANIES.filter((company) => categories.includes(company.category)).map((company) => company.name);
}

const ARRAY_CORE_COMPANIES = companyNamesFor('FAANG+', 'Big Tech', 'Finance & Trading', 'Product (Global)');
const ARRAY_BROAD_COMPANIES = companyNamesFor('FAANG+', 'Big Tech', 'Finance & Trading', 'Indian IT', 'Product (India)', 'Product (Global)', 'Consulting');
const ARRAY_PRODUCT_COMPANIES = companyNamesFor('FAANG+', 'Big Tech', 'Product (India)', 'Product (Global)', 'Finance & Trading');
const ARRAY_FOUNDATION_COMPANIES = companyNamesFor('FAANG+', 'Big Tech', 'Indian IT', 'Product (India)', 'Consulting');
const BINARY_CORE_COMPANIES = companyNamesFor('FAANG+', 'Big Tech', 'Finance & Trading', 'Product (Global)');
const BINARY_BROAD_COMPANIES = companyNamesFor('FAANG+', 'Big Tech', 'Finance & Trading', 'Indian IT', 'Product (India)', 'Product (Global)', 'Consulting');
const BINARY_PRODUCT_COMPANIES = companyNamesFor('FAANG+', 'Big Tech', 'Finance & Trading', 'Product (India)', 'Product (Global)');
const BINARY_ADVANCED_COMPANIES = companyNamesFor('FAANG+', 'Big Tech', 'Finance & Trading', 'Product (Global)');
const STRING_CORE_COMPANIES = companyNamesFor('FAANG+', 'Big Tech', 'Finance & Trading', 'Product (India)', 'Product (Global)');
const STRING_BROAD_COMPANIES = companyNamesFor('FAANG+', 'Big Tech', 'Finance & Trading', 'Indian IT', 'Product (India)', 'Product (Global)', 'Consulting');
const STRING_FOUNDATION_COMPANIES = companyNamesFor('FAANG+', 'Big Tech', 'Indian IT', 'Product (India)', 'Consulting');
const STRING_ADVANCED_COMPANIES = companyNamesFor('FAANG+', 'Big Tech', 'Finance & Trading', 'Product (Global)');
const GREEDY_CORE_COMPANIES = companyNamesFor('FAANG+', 'Big Tech', 'Finance & Trading', 'Product (India)', 'Product (Global)');
const GREEDY_BROAD_COMPANIES = companyNamesFor('FAANG+', 'Big Tech', 'Finance & Trading', 'Indian IT', 'Product (India)', 'Product (Global)', 'Consulting');
const GREEDY_FOUNDATION_COMPANIES = companyNamesFor('FAANG+', 'Big Tech', 'Indian IT', 'Product (India)', 'Consulting');
const GREEDY_ADVANCED_COMPANIES = companyNamesFor('FAANG+', 'Big Tech', 'Finance & Trading', 'Product (Global)');
const TREE_DEPTH_COMPANIES = ["Google", "Amazon", "Microsoft"];
const TREE_COMPARE_COMPANIES = ["Google", "Amazon", "Microsoft"];
const TREE_INVERT_COMPANIES = ["Google", "Amazon", "Microsoft"];
const TREE_LEVEL_COMPANIES = ["Amazon", "Google", "Microsoft"];
const TREE_BST_COMPANIES = ["Google", "Amazon", "Microsoft"];
const TREE_ADVANCED_COMPANIES = ["Google", "Amazon", "Microsoft"];
const TREE_BALANCE_COMPANIES = ["Google", "Amazon", "Microsoft"];
const TREE_PATH_COMPANIES = ["Amazon", "Microsoft", "Oracle", "Adobe", "Goldman Sachs", "Samsung", "Atlassian"];
const TREE_SYMMETRY_COMPANIES = ["Amazon", "Microsoft"];
const TREE_MIN_DEPTH_COMPANIES = ["Amazon"];
const TREE_VIEW_COMPANIES = ["Google", "Amazon", "Microsoft", "Adobe"];
const TREE_ZIGZAG_COMPANIES = ["Amazon", "Microsoft", "Flipkart", "Walmart", "Cisco"];
const TREE_KTH_COMPANIES = ["Accolite", "Amazon", "Google"];
const TREE_BUILD_COMPANIES = ["Google", "Amazon", "Microsoft"];
const TREE_SUMTREE_COMPANIES = ["Amazon", "Microsoft", "Samsung", "Walmart"];
const TREE_LCA_COMPANIES = ["Google", "Amazon", "Microsoft", "Adobe"];
const TREE_FLATTEN_COMPANIES = ["Google", "Amazon", "Microsoft", "Adobe"];
const TREE_PATH_SUM_TWO_COMPANIES = ["Amazon", "Google", "Microsoft", "Oracle"];
const TREE_SUM_NUMBERS_COMPANIES = ["Google", "Amazon", "Microsoft"];
const TREE_PATHS_COMPANIES = ["Google", "Amazon", "Microsoft"];
const TREE_COMPLETE_COUNT_COMPANIES = ["Google", "Amazon", "Microsoft"];
const TREE_PATH_SUM_THREE_COMPANIES = ["Amazon", "Google", "Microsoft"];
const TREE_LEFT_LEAVES_COMPANIES = ["Amazon", "Google", "Microsoft"];
const TREE_LARGEST_ROW_COMPANIES = ["Amazon", "Google", "Microsoft"];
const TREE_COMPLETE_CHECK_COMPANIES = ["Amazon", "Google", "Microsoft"];
const TREE_HARD_CORE_COMPANIES = ["Google", "Amazon", "Microsoft", "Adobe"];
const TREE_HARD_BROAD_COMPANIES = ["Google", "Amazon", "Microsoft", "Meta", "Apple", "Adobe", "Oracle"];
const TREE_HARD_FINANCE_COMPANIES = ["Google", "Amazon", "Microsoft", "Adobe", "Goldman Sachs"];

export default function CompanyProblems() {
    const { companyId } = useParams();
    const navigate = useNavigate();
    const [difficultyFilter, setDifficultyFilter] = useState('all');
    const [topicFilter, setTopicFilter] = useState('all');
    const [searchQuery, setSearchQuery] = useState('');

    const company = COMPANIES.find((c) => c.id === companyId);

    const { data: problems = [], isLoading } = useQuery({
        queryKey: ['problems'],
        queryFn: problemApi.getAll,
    });

    const PROBLEM_METADATA = {
        "Print the matrix in spiral manner": {
            topic: "Matrix",
            companies: [
            "Visa", "Reddit", "Twilio", "Square", "Nutanix",
            "Flipkart", "Target", "AMD", "American Express",
            "Alibaba", "Unity Technologies", "Activision Blizzard",
            "Bain & Company", "Medtronic", "Goldman Sachs",
            "Splunk", "Bloomberg", "Dropbox", "PwC",
            "Philips Healthcare", "Oracle", "Ubisoft", "Uber",
            "JPMorgan Chase", "IBM", "TCS", "Cognizant",
            "Accenture", "Infosys", "Capgemini", "Wipro"
            ],
        },
        "3 Sum": {
            topic: "Two Pointers",
            companies: [
            "Teladoc Health", "Oracle", "DoorDash", "Nutanix", 
            "Epic Games", "ARM", "Wayfair", "Robinhood", 
            "Cloudflare", "Mastercard", "Optum", "Stripe", 
            "Goldman Sachs", "Bain & Company", "Visa", "Deloitte", 
            "MongoDB", "Airbnb", "Rakuten", "KPMG", "AMD", 
            "Johnson & Johnson", "Byju's", "Flipkart", "NVIDIA", 
            "Google", "Microsoft", "Amazon", "Meta", "Apple", 
            "Netflix", "Adobe"
            ],
        },
        "Container With Most Water": {
            topic: "Two Pointers",
            companies: [
                "Google", "Amazon", "Meta", "Microsoft", "Apple", "Netflix", "Adobe", "Uber",
                "Airbnb", "Stripe", "LinkedIn", "Snap", "Goldman Sachs", "JP Morgan",
                "Visa", "Mastercard", "NVIDIA", "Oracle", "Salesforce", "Shopify",
                "Databricks", "Twilio", "Deloitte", "PwC", "Flipkart", "Swiggy"
            ],
        },
        "Trapping Rain Water": {
            topic: "Two Pointers",
            companies: [
                "Google", "Amazon", "Microsoft", "Meta", "Apple", "Adobe", "Uber", "Airbnb",
                "Oracle", "NVIDIA", "Qualcomm", "X (Twitter)", "Spotify", "Samsung",
                "Goldman Sachs", "Morgan Stanley", "DE Shaw", "Citadel", "Razorpay",
                "Zomato", "PhonePe", "Shopify", "Palantir", "Accenture"
            ],
        },
        "Two Sum II - Input Array Is Sorted": {
            topic: "Two Pointers",
            companies: [
                "Google", "Amazon", "Microsoft", "Apple", "Meta", "Netflix", "Adobe", "IBM",
                "Intel", "VMware", "ServiceNow", "Atlassian", "Visa", "Mastercard",
                "Infosys", "TCS", "Wipro", "Cognizant", "Capgemini", "Tech Mahindra", "Tower Research",
                "Paytm", "Meesho", "Snowflake", "Ernst & Young"
            ],
        },
        "Valid Palindrome": {
            topic: "Two Pointers",
            companies: [
                "Google", "Amazon", "Microsoft", "Meta", "Apple", "Adobe", "Stripe",
                "LinkedIn", "Snap", "Spotify", "Jane Street", "KPMG", "HCL Technologies",
                "LTIMindtree", "Mphasis", "Persistent Systems", "CRED", "Zerodha",
                "Shopify", "Twilio"
            ],
        },
        "Sort an array of 0's 1's and 2's": {
            topic: "Sorting",
            companies: [
            "Flipkart", "JP Morgan", "Swiggy", "Qualcomm", 
            "NVIDIA", "PwC", "Morgan Stanley", "KPMG", 
            "Google", "Microsoft", "Amazon", "Meta", 
            "Apple", "Netflix", "Adobe"
            ],
        },
        "Find Minimum in Rotated Sorted Array": {
            topic: "Binary Search",
            companies: [
            "Ernst & Young", "Nutanix", "Red Hat", "Optum", 
            "HashiCorp", "Philips Healthcare", "DoorDash", "Target",
            "Ubisoft", "Zomato", "Airbnb", "Reddit", "KPMG", 
            "Morgan Stanley", "OYO Rooms", "Zynga", "Snowflake", 
            "Databricks", "IBM", "Uber", "Siemens Healthineers", 
            "Splunk", "Shopify", "American Express", "Twilio", "TCS", 
            "Cognizant", "Accenture", "Infosys", "Capgemini", "Wipro"
            ],
        },
        "Search in Rotated Sorted Array": {
            topic: "Binary Search",
            companies: [
                "Google", "Amazon", "Microsoft", "Meta", "Apple", "Adobe", "Oracle", "Uber",
                "Airbnb", "Goldman Sachs", "Morgan Stanley", "JP Morgan", "Visa", "Intel",
                "NVIDIA", "Qualcomm", "ServiceNow", "Atlassian", "Samsung", "Databricks",
                "Twilio", "Deloitte", "Infosys", "TCS", "Wipro", "Cognizant"
            ],
        },
        "Search Insert Position": {
            topic: "Binary Search",
            companies: [
                "Google", "Microsoft", "Amazon", "Meta", "Apple", "Netflix", "Adobe", "IBM",
                "LinkedIn", "X (Twitter)", "Spotify", "VMware", "PwC", "KPMG", "Tech Mahindra",
                "LTIMindtree", "Mphasis", "Persistent Systems", "Paytm", "PhonePe", "Meesho",
                "Palantir", "Capgemini", "Accenture"
            ],
        },
        "Koko Eating Bananas": {
            topic: "Binary Search",
            companies: [
                "Google", "Uber", "Amazon", "Apple", "Meta", "Adobe", "NVIDIA", "Salesforce",
                "Goldman Sachs", "Jane Street", "DE Shaw", "Citadel", "Tower Research",
                "Razorpay", "CRED", "Zerodha", "Shopify", "Snowflake", "Ernst & Young",
                "HCL Technologies", "Zomato"
            ],
        },
        "Median of Two Sorted Arrays": {
            topic: "Binary Search",
            companies: [
                "Google", "Amazon", "Apple", "Meta", "Microsoft", "Adobe", "Oracle", "IBM",
                "Airbnb", "Stripe", "Snap", "Samsung", "Visa", "Mastercard", "JP Morgan",
                "Morgan Stanley", "Palantir", "Databricks", "Swiggy", "Flipkart"
            ],
        },
        "Find First and Last Position of Element in Sorted Array": {
            topic: "Binary Search",
            companies: BINARY_BROAD_COMPANIES,
        },
        "Search a 2D Matrix": {
            topic: "Binary Search",
            companies: BINARY_CORE_COMPANIES,
        },
        "Peak Index in a Mountain Array": {
            topic: "Binary Search",
            companies: BINARY_PRODUCT_COMPANIES,
        },
        "Single Element in a Sorted Array": {
            topic: "Binary Search",
            companies: BINARY_CORE_COMPANIES,
        },
        "Capacity To Ship Packages Within D Days": {
            topic: "Binary Search",
            companies: BINARY_PRODUCT_COMPANIES,
        },
        "Minimum Number of Days to Make m Bouquets": {
            topic: "Binary Search",
            companies: BINARY_BROAD_COMPANIES,
        },
        "H-Index II": {
            topic: "Binary Search",
            companies: companyNamesFor('FAANG+', 'Big Tech', 'Finance & Trading', 'Consulting'),
        },
        "Successful Pairs of Spells and Potions": {
            topic: "Binary Search",
            companies: BINARY_CORE_COMPANIES,
        },
        "Split Array Largest Sum": {
            topic: "Binary Search",
            companies: BINARY_ADVANCED_COMPANIES,
        },
        "Maximum Depth of Binary Tree": {
            topic: "Binary Tree",
            companies: TREE_DEPTH_COMPANIES,
        },
        "Same Tree": {
            topic: "Binary Tree",
            companies: TREE_COMPARE_COMPANIES,
        },
        "Invert Binary Tree": {
            topic: "Binary Tree",
            companies: TREE_INVERT_COMPANIES,
        },
        "Binary Tree Level Order Traversal": {
            topic: "Binary Tree",
            companies: TREE_LEVEL_COMPANIES,
        },
        "Validate Binary Search Tree": {
            topic: "Binary Tree",
            companies: TREE_BST_COMPANIES,
        },
        "Binary Tree Maximum Path Sum": {
            topic: "Binary Tree",
            companies: TREE_ADVANCED_COMPANIES,
        },
        "Balanced Binary Tree": {
            topic: "Binary Tree",
            companies: TREE_BALANCE_COMPANIES,
        },
        "Diameter of Binary Tree": {
            topic: "Binary Tree",
            companies: TREE_BALANCE_COMPANIES,
        },
        "Path Sum": {
            topic: "Binary Tree",
            companies: TREE_PATH_COMPANIES,
        },
        "Symmetric Tree": {
            topic: "Binary Tree",
            companies: TREE_SYMMETRY_COMPANIES,
        },
        "Minimum Depth of Binary Tree": {
            topic: "Binary Tree",
            companies: TREE_MIN_DEPTH_COMPANIES,
        },
        "Binary Tree Right Side View": {
            topic: "Binary Tree",
            companies: TREE_VIEW_COMPANIES,
        },
        "Binary Tree Zigzag Level Order Traversal": {
            topic: "Binary Tree",
            companies: TREE_ZIGZAG_COMPANIES,
        },
        "Kth Smallest Element in a BST": {
            topic: "Binary Tree",
            companies: TREE_KTH_COMPANIES,
        },
        "Construct Binary Tree from Preorder and Inorder Traversal": {
            topic: "Binary Tree",
            companies: TREE_BUILD_COMPANIES,
        },
        "Transform to Sum Tree": {
            topic: "Binary Tree",
            companies: TREE_SUMTREE_COMPANIES,
        },
        "Lowest Common Ancestor of a Binary Tree": {
            topic: "Binary Tree",
            companies: TREE_LCA_COMPANIES,
        },
        "Flatten Binary Tree to Linked List": {
            topic: "Binary Tree",
            companies: TREE_FLATTEN_COMPANIES,
        },
        "Path Sum II": {
            topic: "Binary Tree",
            companies: TREE_PATH_SUM_TWO_COMPANIES,
        },
        "Sum Root to Leaf Numbers": {
            topic: "Binary Tree",
            companies: TREE_SUM_NUMBERS_COMPANIES,
        },
        "Binary Tree Paths": {
            topic: "Binary Tree",
            companies: TREE_PATHS_COMPANIES,
        },
        "Count Complete Tree Nodes": {
            topic: "Binary Tree",
            companies: TREE_COMPLETE_COUNT_COMPANIES,
        },
        "Path Sum III": {
            topic: "Binary Tree",
            companies: TREE_PATH_SUM_THREE_COMPANIES,
        },
        "Sum of Left Leaves": {
            topic: "Binary Tree",
            companies: TREE_LEFT_LEAVES_COMPANIES,
        },
        "Find Largest Value in Each Tree Row": {
            topic: "Binary Tree",
            companies: TREE_LARGEST_ROW_COMPANIES,
        },
        "Check Completeness of a Binary Tree": {
            topic: "Binary Tree",
            companies: TREE_COMPLETE_CHECK_COMPANIES,
        },
        "Recover Binary Search Tree": {
            topic: "Binary Tree",
            companies: TREE_HARD_CORE_COMPANIES,
        },
        "Binary Tree Cameras": {
            topic: "Binary Tree",
            companies: TREE_HARD_CORE_COMPANIES,
        },
        "House Robber III": {
            topic: "Binary Tree",
            companies: ["Amazon", "Google", "Meta"],
        },
        "All Nodes Distance K in Binary Tree": {
            topic: "Binary Tree",
            companies: TREE_HARD_BROAD_COMPANIES,
        },
        "Maximum Sum BST in Binary Tree": {
            topic: "Binary Tree",
            companies: TREE_HARD_FINANCE_COMPANIES,
        },
        "Distribute Coins in Binary Tree": {
            topic: "Binary Tree",
            companies: TREE_HARD_CORE_COMPANIES,
        },
        "Maximum Product of Splitted Binary Tree": {
            topic: "Binary Tree",
            companies: TREE_HARD_BROAD_COMPANIES,
        },
        "Smallest String Starting From Leaf": {
            topic: "Binary Tree",
            companies: TREE_HARD_CORE_COMPANIES,
        },
        "Vertical Order Traversal of a Binary Tree": {
            topic: "Binary Tree",
            companies: TREE_HARD_BROAD_COMPANIES,
        },
        "Boundary of Binary Tree": {
            topic: "Binary Tree",
            companies: TREE_HARD_CORE_COMPANIES,
        },
        "Jump Game": {
            topic: "Greedy",
            companies: [
                "Google", "Amazon", "Microsoft", "Meta", "Apple", "Adobe", "Uber", "Airbnb",
                "Stripe", "Oracle", "NVIDIA", "Intel", "Qualcomm", "VMware", "Atlassian",
                "Goldman Sachs", "Morgan Stanley", "JP Morgan", "Visa", "Infosys", "TCS",
                "Wipro", "Cognizant", "Flipkart", "Swiggy", "Zomato", "Shopify", "Databricks",
                "Deloitte", "Accenture"
            ],
        },
        "Jump Game II": {
            topic: "Greedy",
            companies: [
                "Google", "Amazon", "Meta", "Microsoft", "Apple", "Netflix", "Adobe", "Uber",
                "Salesforce", "IBM", "LinkedIn", "Snap", "Samsung", "ServiceNow", "Goldman Sachs",
                "DE Shaw", "Citadel", "Tower Research", "Mastercard", "HCL Technologies",
                "Tech Mahindra", "LTIMindtree", "Paytm", "PhonePe", "CRED", "Palantir", "Twilio"
            ],
        },
        "Gas Station": {
            topic: "Greedy",
            companies: [
                "Google", "Amazon", "Microsoft", "Meta", "Apple", "Adobe", "Uber", "Oracle",
                "NVIDIA", "Intel", "X (Twitter)", "Spotify", "JP Morgan", "Jane Street", "Visa",
                "Infosys", "Capgemini", "Mphasis", "Persistent Systems", "Razorpay", "Meesho",
                "Zerodha", "Snowflake", "PwC", "Ernst & Young"
            ],
        },
        "Partition Labels": {
            topic: "Greedy",
            companies: [
                "Google", "Amazon", "Meta", "Microsoft", "Apple", "Adobe", "Stripe", "Airbnb",
                "LinkedIn", "Snap", "Spotify", "ServiceNow", "Atlassian", "Morgan Stanley",
                "KPMG", "Wipro", "TCS", "Flipkart", "Swiggy", "Zomato", "Shopify", "Databricks",
                "Twilio", "Deloitte", "Capgemini"
            ],
        },
        "Non-overlapping Intervals": {
            topic: "Greedy",
            companies: [
                "Google", "Amazon", "Microsoft", "Meta", "Apple", "Adobe", "Salesforce", "Oracle",
                "IBM", "Qualcomm", "VMware", "Goldman Sachs", "Morgan Stanley", "JP Morgan",
                "DE Shaw", "Citadel", "Visa", "Mastercard", "Infosys", "Cognizant", "Tech Mahindra",
                "Razorpay", "PhonePe", "CRED", "Palantir", "Accenture", "PwC"
            ],
        },
        "Candy": {
            topic: "Greedy",
            companies: [
                "Google", "Amazon", "Microsoft", "Meta", "Apple", "Netflix", "Adobe", "Uber",
                "Airbnb", "Stripe", "NVIDIA", "Samsung", "Jane Street", "Tower Research",
                "Intel", "LinkedIn", "X (Twitter)", "Spotify", "Visa", "Mastercard",
                "HCL Technologies", "LTIMindtree", "Mphasis", "Persistent Systems", "Paytm",
                "Meesho", "Zerodha", "Snowflake", "Ernst & Young", "KPMG"
            ],
        },
        "Assign Cookies": {
            topic: "Greedy",
            companies: GREEDY_FOUNDATION_COMPANIES,
        },
        "Lemonade Change": {
            topic: "Greedy",
            companies: GREEDY_FOUNDATION_COMPANIES,
        },
        "Can Place Flowers": {
            topic: "Greedy",
            companies: GREEDY_FOUNDATION_COMPANIES,
        },
        "Task Scheduler": {
            topic: "Greedy",
            companies: GREEDY_CORE_COMPANIES,
        },
        "Minimum Number of Arrows to Burst Balloons": {
            topic: "Greedy",
            companies: GREEDY_BROAD_COMPANIES,
        },
        "Bag of Tokens": {
            topic: "Greedy",
            companies: GREEDY_CORE_COMPANIES,
        },
        "Course Schedule III": {
            topic: "Greedy",
            companies: GREEDY_ADVANCED_COMPANIES,
        },
        "Minimum Number of Refueling Stops": {
            topic: "Greedy",
            companies: GREEDY_ADVANCED_COMPANIES,
        },
        "Maximum Performance of a Team": {
            topic: "Greedy",
            companies: GREEDY_ADVANCED_COMPANIES,
        },
        "IPO": {
            topic: "Greedy",
            companies: GREEDY_ADVANCED_COMPANIES,
        },
        "Maximum Points You Can Obtain from Cards": {
            topic: "Sliding Window",
            companies: [
            "Salesforce", "JP Morgan", "NVIDIA", "Databricks", 
            "Swiggy", "Deloitte", "Visa", "Mastercard", 
            "Morgan Stanley", "Google", "Microsoft", "Amazon", 
            "Meta", "Apple", "Netflix", "Adobe"
            ],
        },
        "Fruit Into Baskets": {
            topic: "Sliding Window",
            companies: [
                "Morgan Stanley", "Swiggy", "Intel", "PwC", "Oracle", "Deloitte",
                "Google", "Microsoft", "Amazon", "Meta", "Apple", "Netflix", "Adobe"
            ],
        },
        "Longest Substring Without Repeating Characters": {
            topic: "Sliding Window",
            companies: [
            "Google", "Microsoft", "Amazon", "Meta", "Apple", 
            "Netflix", "Adobe", "NVIDIA", "Qualcomm", "Stripe",
            "Shopify", "Snowflake", "Twilio", "HCL Technologies", "Swiggy",
            "Airbnb", "LinkedIn", "Accenture"
            ],
        },
        "Max Consecutive Ones III": {
            topic: "Sliding Window",
            companies: [
                "HCL Technologies", "JP Morgan", "Zomato", "NVIDIA", "Morgan Stanley",
                "Goldman Sachs", "KPMG", "IBM", "Google", "Microsoft",
                "Amazon", "Meta", "Apple", "Netflix", "Adobe"
            ],
        },
        "Longest Substring With At Most K Distinct Characters": {
            topic: "Sliding Window",
            companies: [
                "Morgan Stanley", "Swiggy", "Intel", "PwC", "Oracle", "Deloitte",
                "Google", "Microsoft", "Amazon", "Meta", "Apple", "Netflix", "Adobe"
            ],
        },
        "Longest Repeating Character Replacement": {
            topic: "Sliding Window",
            companies: [
                "Databricks", "Shopify", "Oracle", "PwC", "NVIDIA", "Flipkart", "Uber",
                "Google", "Microsoft", "Amazon", "Meta", "Apple", "Netflix", "Adobe"
            ],
        },
        "Number of Substrings Containing All Three Characters": {
            topic: "Sliding Window",
            companies: [
                "Ernst & Young", "Flipkart", "Salesforce", "Goldman Sachs", "Zomato", "Intel",
                "Snowflake", "NVIDIA", "Google", "Microsoft", "Amazon", "Meta", "Apple", "Netflix", "Adobe"
            ],
        },
        "Binary Subarrays With Sum": {
            topic: "Sliding Window",
            companies: [
                "Stripe", "Flipkart", "Morgan Stanley", "Shopify", "Deloitte", "HCL Technologies", "Databricks",
                "Google", "Microsoft", "Amazon", "Meta", "Apple", "Netflix", "Adobe"
            ],
        },
        "Count number of Nice subarrays": {
            topic: "Sliding Window",
            companies: [
                "Oracle", "Deloitte", "IBM", "AMD", "ARM", "Salesforce", "Flipkart", "HCL Technologies",
                "Google", "Microsoft", "Amazon", "Meta", "Apple", "Netflix", "Adobe"
            ],
        },
        "Sliding Window Maximum": {
            topic: "Sliding Window",
            companies: [
                "Google", "Amazon", "Apple", "Adobe", "IBM", "Oracle", "NVIDIA", "Qualcomm",
                "ServiceNow", "Atlassian", "VMware", "Samsung", "Goldman Sachs", "JP Morgan",
                "Morgan Stanley", "DE Shaw", "Citadel", "Tower Research", "Visa", "Infosys",
                "TCS", "Cognizant", "Capgemini", "Razorpay", "Paytm", "PhonePe", "CRED",
                "Zerodha", "Palantir"
            ],
        },
        "Minimum Window Substring": {
            topic: "Sliding Window",
            companies: [
                "Google", "Microsoft", "Amazon", "Meta", "Apple", "Adobe", "Oracle", "IBM",
                "Airbnb", "LinkedIn", "Snap", "Spotify", "X (Twitter)", "Goldman Sachs", "Infosys", "Meesho",
                "Databricks", "Snowflake", "Twilio", "Flipkart", "Zomato", "Ernst & Young"
            ],
        },
        "Permutation in String": {
            topic: "Sliding Window",
            companies: [
                "Google", "Amazon", "Meta", "Microsoft", "Stripe", "Mastercard", "Intel",
                "Samsung", "Visa", "Jane Street", "Wipro", "Tech Mahindra", "LTIMindtree", "Mphasis",
                "Persistent Systems", "Razorpay", "Paytm", "PhonePe", "CRED", "Shopify",
                "Palantir", "Deloitte", "PwC", "KPMG"
            ],
        },
        "Traversal in Linked List": {
            topic: "Linked List",
            companies: [
                "Splunk", "HCL Technologies", "Uber", "PwC", "Goldman Sachs",
                "TCS", "Cognizant", "Accenture", "Infosys", "Capgemini", "Wipro"
            ],
        },
        "Reverse Linked List": {
            topic: "Linked List",
            companies: [
                "Google", "Amazon", "Microsoft", "Meta", "Apple", "Netflix", "Adobe", "Uber",
                "Airbnb", "Stripe", "Salesforce", "Oracle", "NVIDIA", "Intel", "IBM",
                "LinkedIn", "Snap", "Spotify", "Qualcomm", "ServiceNow", "Atlassian",
                "Goldman Sachs", "Morgan Stanley", "JP Morgan", "Visa", "Mastercard",
                "Infosys", "TCS", "Wipro", "HCL Technologies", "Cognizant", "Tech Mahindra",
                "LTIMindtree", "Mphasis", "Persistent Systems", "Flipkart", "Swiggy", "Zomato",
                "Shopify", "Databricks", "Snowflake", "Twilio", "Deloitte", "Accenture",
                "Capgemini", "PwC", "KPMG", "Ernst & Young"
            ],
        },
        "Merge Two Sorted Lists": {
            topic: "Linked List",
            companies: [
                "Google", "Amazon", "Microsoft", "Meta", "Apple", "Adobe", "Uber", "Airbnb",
                "Oracle", "NVIDIA", "IBM", "LinkedIn", "Snap", "Samsung", "VMware",
                "Goldman Sachs", "Morgan Stanley", "JP Morgan", "DE Shaw", "Jane Street",
                "Citadel", "Tower Research", "Visa", "Mastercard", "Infosys", "TCS",
                "Wipro", "Cognizant", "HCL Technologies", "Flipkart", "Razorpay", "PhonePe",
                "Meesho", "Zerodha", "Palantir", "Shopify", "Databricks", "Twilio",
                "Deloitte", "PwC"
            ],
        },
        "Middle of the Linked List": {
            topic: "Linked List",
            companies: [
                "Google", "Amazon", "Microsoft", "Meta", "Apple", "Netflix", "Adobe", "Stripe",
                "Salesforce", "Intel", "Qualcomm", "X (Twitter)", "Spotify", "ServiceNow",
                "Atlassian", "JP Morgan", "Visa", "Mastercard", "Accenture", "Capgemini",
                "Paytm", "CRED", "Snowflake", "Ernst & Young"
            ],
        },
        "Remove Nth Node From End of List": {
            topic: "Linked List",
            companies: [
                "Google", "Amazon", "Microsoft", "Meta", "Apple", "Adobe", "Uber", "Airbnb",
                "Stripe", "Oracle", "NVIDIA", "LinkedIn", "Snap", "Samsung", "Goldman Sachs",
                "Morgan Stanley", "JP Morgan", "DE Shaw", "Jane Street", "Citadel",
                "Tower Research", "Visa", "Infosys", "TCS", "Wipro", "HCL Technologies",
                "Tech Mahindra", "LTIMindtree", "Mphasis", "Persistent Systems", "Flipkart",
                "Razorpay", "Swiggy", "Zomato", "Paytm", "PhonePe", "Shopify", "Databricks",
                "Twilio", "Deloitte", "KPMG"
            ],
        },
        "Palindrome Linked List": {
            topic: "Linked List",
            companies: [
                "Google", "Amazon", "Microsoft", "Meta", "Apple", "Netflix", "Adobe", "IBM",
                "LinkedIn", "Snap", "Spotify", "Qualcomm", "VMware", "ServiceNow",
                "Goldman Sachs", "Morgan Stanley", "Visa", "Mastercard", "Infosys", "Cognizant",
                "Capgemini", "PhonePe", "CRED", "Meesho", "Palantir", "PwC", "Ernst & Young"
            ],
        },
        "Reverse Linked List II": {
            topic: "Linked List",
            companies: [
                "Google", "Amazon", "Microsoft", "Meta", "Apple", "Adobe", "Uber", "Airbnb",
                "Stripe", "Salesforce", "Oracle", "NVIDIA", "Intel", "X (Twitter)", "Spotify",
                "Samsung", "Atlassian", "Goldman Sachs", "JP Morgan", "DE Shaw", "Jane Street",
                "Citadel", "Tower Research", "Mastercard", "Infosys", "TCS", "Wipro",
                "HCL Technologies", "Tech Mahindra", "LTIMindtree", "Mphasis", "Persistent Systems",
                "Flipkart", "Razorpay", "Swiggy", "Zomato", "Paytm", "Zerodha", "Shopify",
                "Databricks", "Snowflake", "Twilio", "Deloitte", "Accenture", "KPMG"
            ],
        },
        "Add Two Numbers": {
            topic: "Linked List",
            companies: [
                "Google", "Amazon", "Microsoft", "Meta", "Apple", "Adobe", "Uber", "Airbnb",
                "Stripe", "Salesforce", "Oracle", "NVIDIA", "Intel", "IBM", "LinkedIn",
                "Snap", "Qualcomm", "Samsung", "Goldman Sachs", "Morgan Stanley", "JP Morgan",
                "Visa", "Mastercard", "Infosys", "TCS", "Wipro", "Cognizant", "HCL Technologies",
                "Tech Mahindra", "Flipkart", "Razorpay", "PhonePe", "Meesho", "Shopify",
                "Databricks", "Twilio", "Deloitte"
            ],
        },
        "Swap Nodes in Pairs": {
            topic: "Linked List",
            companies: [
                "Google", "Amazon", "Microsoft", "Meta", "Apple", "Adobe", "Uber", "Airbnb",
                "Oracle", "NVIDIA", "Intel", "ServiceNow", "Atlassian", "Goldman Sachs",
                "Morgan Stanley", "JP Morgan", "DE Shaw", "Visa", "Infosys", "TCS",
                "Wipro", "Tech Mahindra", "Flipkart", "Swiggy", "Zomato", "Shopify",
                "Databricks", "Snowflake", "PwC", "KPMG"
            ],
        },
        "Odd Even Linked List": {
            topic: "Linked List",
            companies: [
                "Google", "Amazon", "Microsoft", "Meta", "Apple", "Netflix", "Adobe", "Stripe",
                "LinkedIn", "Snap", "Spotify", "X (Twitter)", "Oracle", "IBM", "Visa",
                "Mastercard", "Infosys", "Cognizant", "Accenture", "Capgemini", "Razorpay",
                "Paytm", "PhonePe", "CRED", "Twilio", "Deloitte"
            ],
        },
        "Partition List": {
            topic: "Linked List",
            companies: [
                "Google", "Amazon", "Microsoft", "Meta", "Apple", "Adobe", "Uber", "Airbnb",
                "Stripe", "Salesforce", "Oracle", "NVIDIA", "Intel", "LinkedIn", "Snap",
                "Goldman Sachs", "Morgan Stanley", "JP Morgan", "Visa", "Mastercard",
                "Infosys", "TCS", "Wipro", "HCL Technologies", "Flipkart", "Swiggy",
                "Razorpay", "PhonePe", "Meesho", "Shopify", "Databricks", "Twilio"
            ],
        },
        "Rotate List": {
            topic: "Linked List",
            companies: [
                "Google", "Amazon", "Microsoft", "Meta", "Apple", "Adobe", "Uber", "Oracle",
                "NVIDIA", "Intel", "Qualcomm", "Samsung", "VMware", "ServiceNow",
                "Goldman Sachs", "JP Morgan", "Jane Street", "Visa", "Infosys", "TCS",
                "Wipro", "Cognizant", "Tech Mahindra", "Flipkart", "Zomato", "Paytm",
                "Zerodha", "Palantir", "PwC"
            ],
        },
        "Delete the Middle Node of a Linked List": {
            topic: "Linked List",
            companies: [
                "Google", "Amazon", "Microsoft", "Meta", "Apple", "Adobe", "Uber", "Stripe",
                "Oracle", "NVIDIA", "IBM", "LinkedIn", "Snap", "Spotify", "Goldman Sachs",
                "Morgan Stanley", "JP Morgan", "Visa", "Infosys", "TCS", "Wipro",
                "HCL Technologies", "PhonePe", "CRED", "Shopify", "Snowflake", "Deloitte"
            ],
        },
        "Maximum Twin Sum of a Linked List": {
            topic: "Linked List",
            companies: [
                "Google", "Amazon", "Microsoft", "Meta", "Apple", "Adobe", "Uber", "Airbnb",
                "Stripe", "NVIDIA", "Intel", "Oracle", "LinkedIn", "Snap", "Goldman Sachs",
                "DE Shaw", "Citadel", "Tower Research", "Visa", "Mastercard", "Infosys",
                "TCS", "Wipro", "Razorpay", "Paytm", "PhonePe", "Databricks", "Twilio"
            ],
        },
        "Reverse Nodes in k-Group": {
            topic: "Linked List",
            companies: [
                "Google", "Amazon", "Microsoft", "Meta", "Apple", "Adobe", "Uber", "Airbnb",
                "Stripe", "Salesforce", "Oracle", "NVIDIA", "Intel", "LinkedIn", "Snap",
                "Spotify", "Goldman Sachs", "Morgan Stanley", "JP Morgan", "DE Shaw",
                "Jane Street", "Citadel", "Tower Research", "Visa", "Infosys", "TCS",
                "Wipro", "HCL Technologies", "Tech Mahindra", "Flipkart", "Swiggy",
                "PhonePe", "Shopify", "Databricks", "Snowflake", "Twilio", "Deloitte"
            ],
        },
        "Deletion of the head of LL": {
            topic: "Linked List",
            companies: [
                "Oracle", "IBM", "Morgan Stanley", "PwC", "Shopify", "Stripe",
                "Flipkart", "TCS", "Cognizant", "Accenture", "Infosys", "Capgemini", "Wipro"
            ],
        },
        "Deletion of the tail of LL": {
            topic: "Linked List",
            companies: [
                "McKinsey & Company", "Goldman Sachs", "IBM", "Stripe", "Oracle", "Texas Instruments",
                "ARM", "TCS", "Cognizant", "Accenture", "Infosys", "Capgemini", "Wipro"
            ],
        },
        "Deletion of the Kth element of LL": {
            topic: "Linked List",
            companies: [
                "McKinsey & Company", "JPMorgan Chase", "Uber", "Reddit", "Morgan Stanley", "Salesforce",
                "KPMG", "Red Hat", "Cloudflare", "eBay", "TCS", "Cognizant", "Accenture", "Infosys", "Capgemini", "Wipro"
            ],
        },
        "Delete the element with value X": {
            topic: "Linked List",
            companies: [
                "Goldman Sachs", "Salesforce", "Qualcomm", "Swiggy", "Zomato", "PwC",
                "TCS", "Cognizant", "Accenture", "Infosys", "Capgemini", "Wipro"
            ],
        },
        "Insertion at the head of Linked List": {
            topic: "Linked List",
            companies: [
                "Oracle", "Twilio", "Shopify", "Qualcomm", "Databricks", "Goldman Sachs",
                "Flipkart", "ARM", "TCS", "Cognizant", "Accenture", "Infosys", "Capgemini", "Wipro"
            ],
        },
        "Two Sum": {
            topic: "Array",
            companies: ARRAY_BROAD_COMPANIES,
        },
        "Best Time to Buy and Sell Stock": {
            topic: "Array",
            companies: ARRAY_FOUNDATION_COMPANIES,
        },
        "Maximum Subarray": {
            topic: "Array",
            companies: ARRAY_BROAD_COMPANIES,
        },
        "Merge Sorted Array": {
            topic: "Array",
            companies: ARRAY_FOUNDATION_COMPANIES,
        },
        "Majority Element": {
            topic: "Array",
            companies: ARRAY_FOUNDATION_COMPANIES,
        },
        "Pascal's Triangle": {
            topic: "Array",
            companies: companyNamesFor('FAANG+', 'Big Tech', 'Indian IT', 'Consulting'),
        },
        "Product of Array Except Self": {
            topic: "Array",
            companies: ARRAY_CORE_COMPANIES,
        },
        "Rotate Array": {
            topic: "Array",
            companies: ARRAY_PRODUCT_COMPANIES,
        },
        "Set Matrix Zeroes": {
            topic: "Array",
            companies: ARRAY_CORE_COMPANIES,
        },
        "Merge Intervals": {
            topic: "Array",
            companies: ARRAY_BROAD_COMPANIES,
        },
        "Next Permutation": {
            topic: "Array",
            companies: ARRAY_CORE_COMPANIES,
        },
        "Game of Life": {
            topic: "Array",
            companies: companyNamesFor('FAANG+', 'Big Tech', 'Finance & Trading', 'Product (Global)'),
        },
        "First Missing Positive": {
            topic: "Array",
            companies: ARRAY_CORE_COMPANIES,
        },
        "Longest Common Prefix": {
            topic: "String",
            companies: STRING_FOUNDATION_COMPANIES,
        },
        "Valid Anagram": {
            topic: "String",
            companies: STRING_FOUNDATION_COMPANIES,
        },
        "Isomorphic Strings": {
            topic: "String",
            companies: STRING_BROAD_COMPANIES,
        },
        "Roman to Integer": {
            topic: "String",
            companies: STRING_FOUNDATION_COMPANIES,
        },
        "Integer to Roman": {
            topic: "String",
            companies: STRING_CORE_COMPANIES,
        },
        "Find the Index of the First Occurrence in a String": {
            topic: "String",
            companies: STRING_FOUNDATION_COMPANIES,
        },
        "Zigzag Conversion": {
            topic: "String",
            companies: STRING_CORE_COMPANIES,
        },
        "String to Integer (atoi)": {
            topic: "String",
            companies: STRING_CORE_COMPANIES,
        },
        "Group Anagrams": {
            topic: "String",
            companies: STRING_CORE_COMPANIES,
        },
        "Decode String": {
            topic: "String",
            companies: STRING_CORE_COMPANIES,
        },
        "Longest Palindromic Substring": {
            topic: "String",
            companies: STRING_ADVANCED_COMPANIES,
        },
        "Palindromic Substrings": {
            topic: "String",
            companies: STRING_CORE_COMPANIES,
        },
        "Multiply Strings": {
            topic: "String",
            companies: STRING_CORE_COMPANIES,
        },
        "Minimum Remove to Make Valid Parentheses": {
            topic: "String",
            companies: STRING_BROAD_COMPANIES,
        },
        "Custom Sort String": {
            topic: "String",
            companies: STRING_BROAD_COMPANIES,
        },
        "Simplify Path": {
            topic: "String",
            companies: STRING_CORE_COMPANIES,
        },
        "Count and Say": {
            topic: "String",
            companies: STRING_FOUNDATION_COMPANIES,
        },
        "Word Break": {
            topic: "String",
            companies: STRING_CORE_COMPANIES,
        },
        "Valid Number": {
            topic: "String",
            companies: STRING_ADVANCED_COMPANIES,
        },
        "Regular Expression Matching": {
            topic: "String",
            companies: STRING_ADVANCED_COMPANIES,
        },
    };

    const companyProblems = problems
        .filter((p) => p.problem_type !== 'cp')
        .map((p) => {
            let title = p.title;
            if (title.includes("Spiral")) title = "Print the matrix in spiral manner";

            const metadata = PROBLEM_METADATA[title];
            if (!metadata) return null;

            const isMappedToCompany = metadata.companies.some((mappedCompany) =>
                companyNameMatches(company?.name, mappedCompany)
            );

            if (!isMappedToCompany) return null;

            return {
                ...p,
                topic: metadata.topic,
            };
        })
        .filter(Boolean);

    const difficultyCounts = useMemo(() => {
        const counts = { all: companyProblems.length, easy: 0, medium: 0, hard: 0 };
        companyProblems.forEach((problem) => {
            const key = (problem.difficulty || '').toLowerCase();
            if (counts[key] !== undefined) counts[key] += 1;
        });
        return counts;
    }, [companyProblems]);

    const filteredProblems = useMemo(() => {
        return companyProblems.filter((problem) => {
            const matchesDifficulty =
                difficultyFilter === 'all' ||
                (problem.difficulty || '').toLowerCase() === difficultyFilter;
            const matchesTopic =
                topicFilter === 'all' ||
                (problem.topic || '').toLowerCase() === topicFilter;
            const matchesSearch =
                !searchQuery ||
                problem.title.toLowerCase().includes(searchQuery.toLowerCase());
            return matchesDifficulty && matchesTopic && matchesSearch;
        });
    }, [companyProblems, difficultyFilter, topicFilter, searchQuery]);

    const topicOptions = useMemo(() => {
        const uniqueTopics = [...new Set(companyProblems.map((problem) => problem.topic).filter(Boolean))];
        return ['all', ...uniqueTopics.map((topic) => topic.toLowerCase())];
    }, [companyProblems]);

    const topicCounts = useMemo(() => {
        const counts = { all: companyProblems.length };
        companyProblems.forEach((problem) => {
            const key = (problem.topic || '').toLowerCase();
            if (!key) return;
            counts[key] = (counts[key] || 0) + 1;
        });
        return counts;
    }, [companyProblems]);

    const difficultyColor = (d) => {
        const dl = (d || '').toLowerCase();
        if (dl === 'easy') return '#6fbf73';
        if (dl === 'medium') return '#c39a4f';
        return '#c65a49';
    };

    if (!company) {
        return (
            <div className="cprob">
                <div className="cprob__inner" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
                    <div style={{ textAlign: 'center' }}>
                        <Building2 size={40} style={{ margin: '0 auto 12px', opacity: 0.3, color: 'var(--color-text-muted)' }} />
                        <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem', fontWeight: 600 }}>System not found</p>
                        <button
                            onClick={() => navigate('/practice/dsa')}
                            className="cprob__back-btn"
                            style={{ marginTop: '1rem' }}
                        >
                            <ArrowLeft size={14} />
                            Return to Company Hub
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="cprob">
            <div className="cprob__inner">
                {/* ── Header ──────────────────────────────── */}
                <motion.div
                    initial={{ opacity: 0, y: -12 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="cprob__header"
                >
                    <button
                        onClick={() => navigate('/practice/dsa')}
                        className="cprob__back-btn"
                    >
                        <ArrowLeft size={14} />
                        Company Hub
                    </button>

                    <div className="cprob__header-main">
                        <div className="cprob__header-left">
                            <CompanyLogo
                                company={company}
                                size="lg"
                                roundedClassName="rounded-xl"
                                className="cprob__company-logo"
                            />
                            <div>
                                <span className="cprob__kicker">System Profile</span>
                                <h1 className="cprob__title">{company.name}</h1>
                                <p className="cprob__subtitle">
                                    {companyProblems.length} challenge{companyProblems.length === 1 ? '' : 's'} mapped
                                    <span className="cprob__subtitle-sep">·</span>
                                    {topicOptions.length - 1} topic{topicOptions.length - 1 === 1 ? '' : 's'}
                                </p>
                            </div>
                        </div>

                        <div className="cprob__search-wrap">
                            <Search size={15} className="cprob__search-icon" />
                            <input
                                type="text"
                                placeholder="Search challenges..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="cprob__search-input"
                            />
                        </div>
                    </div>
                </motion.div>

                {/* ── Body ────────────────────────────────── */}
                {isLoading ? (
                    <div className="cprob__loading">
                        <div className="cprob__spinner" />
                    </div>
                ) : companyProblems.length > 0 ? (
                    <div className="cprob__body">
                        {/* Sidebar */}
                        <motion.aside
                            initial={{ opacity: 0, x: -16 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.08 }}
                            className="cprob__sidebar"
                        >
                            {/* Difficulty */}
                            <p className="cprob__sidebar-title">Threat Level</p>
                            {[
                                { key: 'all', label: 'All Levels' },
                                { key: 'easy', label: 'Easy' },
                                { key: 'medium', label: 'Medium' },
                                { key: 'hard', label: 'Hard' },
                            ].map((chip) => (
                                <button
                                    key={chip.key}
                                    onClick={() => setDifficultyFilter(chip.key)}
                                    className={`cprob__filter-btn ${difficultyFilter === chip.key ? 'cprob__filter-btn--active' : ''}`}
                                >
                                    {chip.key !== 'all' && (
                                        <span
                                            className="cprob__diff-dot"
                                            style={{ background: difficultyColor(chip.key) }}
                                        />
                                    )}
                                    <span>{chip.label}</span>
                                    <span className="cprob__filter-count">{difficultyCounts[chip.key]}</span>
                                </button>
                            ))}

                            {/* Topics */}
                            <p className="cprob__sidebar-title" style={{ marginTop: '1.5rem' }}>
                                Algorithm Class
                            </p>
                            {topicOptions.map((topicKey) => (
                                <button
                                    key={topicKey}
                                    onClick={() => setTopicFilter(topicKey)}
                                    className={`cprob__filter-btn ${topicFilter === topicKey ? 'cprob__filter-btn--active' : ''}`}
                                >
                                    <span>
                                        {topicKey === 'all'
                                            ? 'All Topics'
                                            : topicKey.split(' ').map((w) => w[0].toUpperCase() + w.slice(1)).join(' ')}
                                    </span>
                                    <span className="cprob__filter-count">{topicCounts[topicKey] || 0}</span>
                                </button>
                            ))}

                            {/* Stats */}
                            <div className="cprob__stats-panel">
                                <div className="cprob__stats-header">
                                    <Terminal size={12} />
                                    <span>Intel Summary</span>
                                </div>
                                <div className="cprob__stats-row">
                                    <span className="cprob__stats-label">Total</span>
                                    <span className="cprob__stats-value cprob__stats-value--accent">{companyProblems.length}</span>
                                </div>
                                <div className="cprob__stats-row">
                                    <span className="cprob__stats-label">Showing</span>
                                    <span className="cprob__stats-value">{filteredProblems.length}</span>
                                </div>
                                <div className="cprob__stats-row">
                                    <span className="cprob__stats-label">Topics</span>
                                    <span className="cprob__stats-value">{topicOptions.length - 1}</span>
                                </div>
                            </div>
                        </motion.aside>

                        {/* Problem List */}
                        <motion.main
                            initial={{ opacity: 0, y: 16 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.12 }}
                            className="cprob__main"
                        >
                            {/* Column headers */}
                            <div className="cprob__list-header">
                                <span className="cprob__list-header-status">Status</span>
                                <span className="cprob__list-header-title">Challenge</span>
                                <span className="cprob__list-header-diff">Level</span>
                                <span className="cprob__list-header-topic">Topic</span>
                            </div>

                            {filteredProblems.length === 0 ? (
                                <div className="cprob__empty">
                                    <p>No challenges match current filters</p>
                                </div>
                            ) : (
                                <div className="cprob__list">
                                    <AnimatePresence mode="popLayout">
                                        {filteredProblems.map((prob, idx) => (
                                            <motion.div
                                                key={prob.id}
                                                layout
                                                initial={{ opacity: 0, y: 8 }}
                                                animate={{ opacity: 1, y: 0 }}
                                                exit={{ opacity: 0, y: -8 }}
                                                transition={{ delay: Math.min(idx * 0.03, 0.5), duration: 0.3 }}
                                                onClick={() => navigate(`/practice/${prob.id}`)}
                                                className="cprob__row"
                                            >
                                                {/* Status */}
                                                <div className="cprob__row-status">
                                                    <div className={`cprob__check ${prob.solved ? 'cprob__check--solved' : ''}`}>
                                                        <Check className="cprob__check-icon" />
                                                    </div>
                                                </div>

                                                {/* Title */}
                                                <div className="cprob__row-title">
                                                    <h3 className="cprob__row-name">{prob.title}</h3>
                                                </div>

                                                {/* Difficulty */}
                                                <div className="cprob__row-diff">
                                                    <span
                                                        className="cprob__diff-badge"
                                                        style={{
                                                            color: difficultyColor(prob.difficulty),
                                                            background: `${difficultyColor(prob.difficulty)}15`,
                                                            borderColor: `${difficultyColor(prob.difficulty)}30`,
                                                        }}
                                                    >
                                                        {prob.difficulty}
                                                    </span>
                                                </div>

                                                {/* Topic */}
                                                <div className="cprob__row-topic">
                                                    {prob.topic && (
                                                        <span className="cprob__topic-badge">
                                                            {prob.topic}
                                                        </span>
                                                    )}
                                                </div>

                                                {/* Hover arrow */}
                                                <div className="cprob__row-arrow">
                                                    <ChevronRight size={16} />
                                                </div>
                                            </motion.div>
                                        ))}
                                    </AnimatePresence>
                                </div>
                            )}
                        </motion.main>
                    </div>
                ) : (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.15 }}
                        className="cprob__coming-soon"
                    >
                        <div className="cprob__coming-soon-icon">
                            <Clock size={28} />
                        </div>
                        <h2 className="cprob__coming-soon-title">Challenges Incoming</h2>
                        <p className="cprob__coming-soon-desc">
                            We're curating the most frequently asked coding questions from{' '}
                            <strong>{company.name}</strong> interviews and online assessments.
                            Check back soon!
                        </p>
                        <div className="cprob__coming-soon-meta">
                            <span><Code2 size={14} /> OA Questions</span>
                            <span className="cprob__coming-soon-sep" />
                            <span><Building2 size={14} /> Interview Rounds</span>
                        </div>
                    </motion.div>
                )}
            </div>
        </div>
    );
}
