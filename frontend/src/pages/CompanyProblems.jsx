import { useMemo, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { ArrowLeft, Building2, Check, Clock, Code2, Play } from 'lucide-react';
import { COMPANIES } from '../utils/companies';
import { problemApi } from '../api/auth';
import Badge from '../components/ui/Badge';
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

export default function CompanyProblems() {
    const { companyId } = useParams();
    const navigate = useNavigate();
    const [difficultyFilter, setDifficultyFilter] = useState('all');
    const [topicFilter, setTopicFilter] = useState('all');

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
    };

    const companyProblems = problems
        .map((p) => {
            let title = p.title;
            // Normalization for the db title
            if (title.includes("Spiral")) title = "Print the matrix in spiral manner";

            const metadata = PROBLEM_METADATA[title];
            if (!metadata) return null;

            const isMappedToCompany = metadata.companies.some((mappedCompany) =>
                companyNameMatches(company.name, mappedCompany)
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
            return matchesDifficulty && matchesTopic;
        });
    }, [companyProblems, difficultyFilter, topicFilter]);

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

    const difficultyChips = [
        { key: 'all', label: 'All' },
        { key: 'easy', label: 'Easy' },
        { key: 'medium', label: 'Medium' },
        { key: 'hard', label: 'Hard' },
    ];

    if (!company) {
        return (
            <div className="min-h-screen bg-bg-root flex items-center justify-center">
                <div className="text-center">
                    <Building2 size={40} className="mx-auto text-text-muted/40 mb-3" />
                    <p className="text-text-secondary text-sm font-medium">Company not found</p>
                    <button
                        onClick={() => navigate('/problems')}
                        className="mt-4 px-4 py-2 rounded-[14px_11px_13px_9px] bg-accent/10 text-accent text-sm font-medium hover:bg-accent/20 transition-colors"
                    >
                        ← Back to Companies
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-bg-root pb-20">
            <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
                {/* Back button */}
                <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}>
                    <button
                        onClick={() => navigate('/problems')}
                        className="flex items-center gap-2 text-text-secondary hover:text-text-primary text-sm font-medium mb-6 transition-colors group"
                    >
                        <ArrowLeft size={16} className="group-hover:-translate-x-0.5 transition-transform" />
                        Back to Companies
                    </button>
                </motion.div>

                {/* Company Header */}
                <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.05 }}
                    className="paper-card p-6 sm:p-7 border-l-4"
                    style={{ borderLeftColor: company.color }}
                >
                    <div className="flex items-center gap-4 sm:gap-5">
                        <CompanyLogo
                            company={company}
                            size="lg"
                            roundedClassName="rounded-xl"
                            className="shadow-[0_6px_16px_rgba(0,0,0,0.2)]"
                        />
                        <div className="min-w-0">
                            <p className="text-[11px] uppercase tracking-[0.18em] text-text-muted font-semibold">Company</p>
                            <h1 className="text-2xl sm:text-3xl font-bold text-text-primary truncate">
                                {company.name}
                            </h1>
                            <p className="text-sm text-text-secondary mt-1">
                                {companyProblems.length} question{companyProblems.length === 1 ? '' : 's'} mapped for this company
                            </p>
                        </div>
                    </div>
                </motion.div>

                {isLoading ? (
                    <div className="mt-8 flex justify-center"><div className="w-8 h-8 border-4 border-accent border-t-transparent rounded-full animate-spin"></div></div>
                ) : companyProblems.length > 0 ? (
                    <div className="mt-8 grid gap-4">
                        <div className="paper-card-soft p-4 sm:p-5">
                            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                                <h2 className="text-lg font-bold text-text-primary">
                                    Company Questions
                                </h2>
                                <div className="flex flex-wrap gap-2">
                                    {difficultyChips.map((chip) => (
                                        <button
                                            key={chip.key}
                                            onClick={() => setDifficultyFilter(chip.key)}
                                            className={`px-3 py-1.5 rounded-full text-xs font-semibold border transition-colors ${
                                                difficultyFilter === chip.key
                                                    ? 'bg-bg-hover text-text-primary border-border-hover'
                                                    : 'bg-bg-secondary text-text-secondary border-border hover:text-text-primary'
                                            }`}
                                        >
                                            {chip.label}
                                            <span className="ml-1.5 opacity-70">{difficultyCounts[chip.key]}</span>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="mt-3 flex flex-wrap gap-2">
                                {topicOptions.map((topicKey) => (
                                    <button
                                        key={topicKey}
                                        onClick={() => setTopicFilter(topicKey)}
                                        className={`px-3 py-1.5 rounded-full text-xs font-semibold border transition-colors ${
                                            topicFilter === topicKey
                                                ? 'bg-accent/15 text-accent border-accent/40'
                                                : 'bg-bg-secondary text-text-secondary border-border hover:text-text-primary'
                                        }`}
                                    >
                                        {topicKey === 'all' ? 'All Topics' : topicKey.split(' ').map((w) => w[0].toUpperCase() + w.slice(1)).join(' ')}
                                        <span className="ml-1.5 opacity-70">{topicCounts[topicKey] || 0}</span>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {filteredProblems.length === 0 ? (
                            <div className="paper-card-soft p-8 text-center">
                                <p className="text-text-secondary text-sm">
                                    No problems found for the selected filters in {company.name}.
                                </p>
                            </div>
                        ) : filteredProblems.map((prob, idx) => (
                            <motion.div
                                key={prob.id}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.1 + idx * 0.05 }}
                                onClick={() => navigate(`/practice/${prob.id}`)}
                                className="group relative paper-card-soft hover:border-accent/50 p-5 cursor-pointer transition-colors"
                            >
                                <div className="flex items-center justify-between z-10 relative">
                                    <div className="flex items-start gap-3 min-w-0">
                                        <div
                                            className={`mt-0.5 h-5 w-5 shrink-0 rounded-md border flex items-center justify-center transition-colors ${
                                                prob.solved
                                                    ? 'border-[#6fbf73] bg-[#6fbf73]/15 text-[#6fbf73]'
                                                    : 'border-border text-transparent bg-bg-secondary'
                                            }`}
                                            title={prob.solved ? 'Solved' : 'Not solved yet'}
                                        >
                                            <Check className="w-3.5 h-3.5" />
                                        </div>
                                        <div className="min-w-0">
                                        <h3 className="text-base font-bold text-text-primary group-hover:text-accent transition-colors pr-5">
                                            {prob.title}
                                        </h3>
                                        <div className="flex items-center gap-3 mt-2 text-xs text-text-muted">
                                            <Badge color={prob.difficulty === 'easy' ? 'green' : prob.difficulty === 'medium' ? 'yellow' : 'red'}>
                                                {prob.difficulty}
                                            </Badge>
                                            {prob.topic && (
                                                <span className="px-2 py-1 rounded-full border border-border text-text-secondary">
                                                    {prob.topic}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                    </div>
                                    <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center translate-x-3 opacity-0 group-hover:translate-x-0 group-hover:opacity-100 transition-all">
                                        <Play className="w-4 h-4 text-accent translate-x-0.5" />
                                    </div>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                ) : (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.15 }}
                        className="mt-8 paper-card p-12 text-center"
                    >
                        <div className="w-16 h-16 mx-auto rounded-xl bg-accent/10 flex items-center justify-center mb-5">
                            <Clock size={28} className="text-accent" />
                        </div>
                        <h2 className="text-xl font-bold text-text-primary mb-2">
                            Questions Coming Soon
                        </h2>
                        <p className="text-text-secondary text-sm max-w-md mx-auto leading-relaxed">
                            We're curating the most frequently asked coding questions from{' '}
                            <span className="font-semibold text-text-primary">{company.name}</span> interviews and online assessments.
                            Check back soon!
                        </p>

                        <div className="mt-8 flex items-center justify-center gap-6">
                            <div className="flex items-center gap-2 text-text-muted text-xs">
                                <Code2 size={14} />
                                <span>OA Questions</span>
                            </div>
                            <div className="w-px h-4 bg-border" />
                            <div className="flex items-center gap-2 text-text-muted text-xs">
                                <Building2 size={14} />
                                <span>Interview Rounds</span>
                            </div>
                        </div>
                    </motion.div>
                )}
            </div>
        </div>
    );
}
