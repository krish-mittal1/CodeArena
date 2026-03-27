import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { ArrowLeft, Building2, Clock, Code2, Play } from 'lucide-react';
import { COMPANIES } from '../utils/companies';
import { problemApi } from '../api/auth';
import Badge from '../components/ui/Badge';

export default function CompanyProblems() {
    const { companyId } = useParams();
    const navigate = useNavigate();

    const company = COMPANIES.find((c) => c.id === companyId);

    const { data: problems = [], isLoading } = useQuery({
        queryKey: ['problems'],
        queryFn: problemApi.getAll,
    });

    const PROBLEM_COMPANY_MAPPING = {
        "Print the matrix in spiral manner": [
            "Visa", "Reddit", "Twilio", "Square", "Nutanix",
            "Flipkart", "Target", "AMD", "American Express",
            "Alibaba", "Unity Technologies", "Activision Blizzard",
            "Bain & Company", "Medtronic", "Goldman Sachs",
            "Splunk", "Bloomberg", "Dropbox", "PwC",
            "Philips Healthcare", "Oracle", "Ubisoft", "Uber",
            "JPMorgan Chase", "IBM", "TCS", "Cognizant",
            "Accenture", "Infosys", "Capgemini", "Wipro"
        ],
        "3 Sum": [
            "Teladoc Health", "Oracle", "DoorDash", "Nutanix", 
            "Epic Games", "ARM", "Wayfair", "Robinhood", 
            "Cloudflare", "Mastercard", "Optum", "Stripe", 
            "Goldman Sachs", "Bain & Company", "Visa", "Deloitte", 
            "MongoDB", "Airbnb", "Rakuten", "KPMG", "AMD", 
            "Johnson & Johnson", "Byju's", "Flipkart", "NVIDIA", 
            "Google", "Microsoft", "Amazon", "Meta", "Apple", 
            "Netflix", "Adobe"
        ]
    };

    const companyProblems = problems.filter(p => {
        let title = p.title;
        // Normalization for the db title
        if (title.includes("Spiral")) title = "Print the matrix in spiral manner";
        
        const mappedCompanies = PROBLEM_COMPANY_MAPPING[title];
        if (!mappedCompanies) return false;
        
        return mappedCompanies.some(tc => 
            tc.toLowerCase() === company.name.toLowerCase() || 
            company.name.toLowerCase().includes(tc.toLowerCase())
        );
    });

    if (!company) {
        return (
            <div className="min-h-screen bg-bg-root flex items-center justify-center">
                <div className="text-center">
                    <Building2 size={40} className="mx-auto text-text-muted/40 mb-3" />
                    <p className="text-text-secondary text-sm font-medium">Company not found</p>
                    <button
                        onClick={() => navigate('/problems')}
                        className="mt-4 px-4 py-2 rounded-lg bg-accent/10 text-accent text-sm font-medium hover:bg-accent/20 transition-colors"
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
                    className="bg-bg-secondary border border-border rounded-2xl p-8 relative overflow-hidden"
                >
                    {/* Accent gradient */}
                    <div
                        className="absolute top-0 left-0 right-0 h-1 opacity-60"
                        style={{
                            background: `linear-gradient(90deg, ${company.color}, ${company.color}00)`,
                        }}
                    />

                    <div className="flex items-center gap-5">
                        <div
                            className="w-16 h-16 rounded-2xl flex items-center justify-center text-3xl shrink-0"
                            style={{ backgroundColor: `${company.color}15` }}
                        >
                            {company.logo}
                        </div>
                        <div>
                            <h1 className="text-2xl sm:text-3xl font-extrabold text-text-primary tracking-tight">
                                {company.name}
                            </h1>
                            <span
                                className="inline-block mt-1 px-3 py-1 rounded-md text-xs font-semibold uppercase tracking-wider"
                                style={{
                                    color: company.color,
                                    backgroundColor: `${company.color}12`,
                                }}
                            >
                                {company.category}
                            </span>
                        </div>
                    </div>
                </motion.div>

                {isLoading ? (
                    <div className="mt-8 flex justify-center"><div className="w-8 h-8 border-4 border-accent border-t-transparent rounded-full animate-spin"></div></div>
                ) : companyProblems.length > 0 ? (
                    <div className="mt-8 grid gap-4">
                        <h2 className="text-lg font-bold text-text-primary mb-2">Company Questions</h2>
                        {companyProblems.map((prob, idx) => (
                            <motion.div
                                key={prob.id}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.1 + idx * 0.05 }}
                                onClick={() => navigate(`/practice/${prob.id}`)}
                                className="group relative bg-bg-secondary border border-border hover:border-accent/50 rounded-xl p-5 cursor-pointer transition-all overflow-hidden"
                            >
                                <div className="flex items-center justify-between z-10 relative">
                                    <div>
                                        <h3 className="text-base font-bold text-text-primary group-hover:text-accent transition-colors">
                                            {prob.title}
                                        </h3>
                                        <div className="flex items-center gap-3 mt-2 text-xs text-text-muted">
                                            <Badge color={prob.difficulty === 'easy' ? 'green' : prob.difficulty === 'medium' ? 'yellow' : 'red'}>
                                                {prob.difficulty}
                                            </Badge>
                                        </div>
                                    </div>
                                    <div className="w-10 h-10 rounded-full bg-accent/10 flex items-center justify-center translate-x-4 opacity-0 group-hover:translate-x-0 group-hover:opacity-100 transition-all">
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
                        className="mt-8 bg-bg-secondary border border-border rounded-2xl p-12 text-center"
                    >
                        <div className="w-16 h-16 mx-auto rounded-2xl bg-accent/10 flex items-center justify-center mb-5">
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
