//pfps
import jacob from "@/assets/images/jacob.png";
import krish from "@/assets/images/krish.jpg";
import rebecca from "@/assets/images/rebecca.jpg";
import vaishvi from "@/assets/images/vaishvi.jpeg";
//projgraphics
import mean from "@/assets/graphics/Mean Reversion.svg";
import sentiment from "@/assets/graphics/Sentiment Analysis.svg";
import crypto from "@/assets/graphics/Crypto Arbitrage.svg";
import llm from "@/assets/graphics/LLM.svg";
import backtesting from "@/assets/graphics/backtesting.png";
import ml from "@/assets/graphics/ml.svg";
import correlation from "@/assets/graphics/correlation.svg";

export const execs = [
    {
        name: "Jacob Yan",
        role: "Co-Pres",
        image: jacob,
        alt: "Jacob Yan",
    },
    {
        name: "Krish Modi",
        role: "Co-Pres",
        image: krish,
        alt: "Krish Modi",
    },
    {
        name: "Rebecca Xu",
        role: "Internal Ops",
        image: rebecca,
        alt: "Rebecca Xu",
    },
    {
        name: "Vaishvi Shah",
        role: "ML Lead",
        image: vaishvi,
        alt: "Vaishvi Shah",
    },
] as const;

export const team = [
    { name: "Utkarsh Gupta", team: "Quant Lead" },
    { name: "Abdullah Al Amaan", team: "Project Lead" },
    { name: "Sachit Singh Juneja", team: "Project Lead" },
    { name: "Ramzy Girgis", team: "Project Lead" },
    { name: "Sean Song", team: "Project Lead" },
    { name: "Sanjay Ramesh", team: "Project Lead" },
    { name: "Aadya Garg", team: "Project Lead" },
    { name: "Alex Wang", team: "Project Lead" },
    { name: "Akash Lakshmanan", team: "Project Lead" },
    { name: "Kamakshi Sarvananthan", team: "Project Lead" },
    { name: "Ishaan Bansal", team: "Project Lead" },
    { name: "Emma Shi", team: "Project Lead" },
    { name: "Ario Barin Ostovary", team: "ML Engineer" },
    { name: "Bhumi Shah", team: "ML Engineer" },
    { name: "Liron Katsif", team: "ML Engineer" },
    { name: "Sahil Alamgir", team: "ML Engineer" },
    { name: "Anish Nagariya", team: "Quant" },
    { name: "Johan Naresh", team: "Quant" },
    { name: "Adam Kamel", team: "ML Engineer" },
    { name: "Gaurang Jindal", team: "Quant" },
    { name: "Ryan Li", team: "Quant" },
    { name: "Jishnu Jetwani", team: "ML Engineer" },
    { name: "Cindy Li", team: "Quant" },
    { name: "James Hong", team: "ML Engineer" },
    { name: "Pravin Lohani", team: "Quant" },
    { name: "Arav Sharma", team: "Quant" },
    { name: "Justin Wei", team: "Quant" },
    { name: "Kapil Iyer", team: "ML Engineer" },
    { name: "Philip William Ventura", team: "Quant" },
    { name: "Varnit Sahu", team: "ML Engineer" },
    { name: "Ruifeng Li", team: "Quant" },
    { name: "Tom Almog", team: "ML Engineer" },
    { name: "Jinghua Zhao", team: "Quant" },
    { name: "Parth Patel", team: "ML Engineer" },
    { name: "Shruti Dua", team: "Quant" },
    { name: "Caden Sun", team: "ML Engineer" },
    { name: "Mohammed Elshrief", team: "ML Engineer" },
    { name: "Nancy Zhou", team: "Quant" },
    { name: "Harman Singh", team: "ML Engineer" },
    { name: "Krish Chopra", team: "Quant" },
    { name: "Rickey Zheng", team: "ML Engineer" },
    { name: "Rishab Anand", team: "ML Engineer" },
    { name: "Tahseen Rayhan", team: "Quant" },
    { name: "David He", team: "ML Engineer" },
    { name: "Aarav Patel", team: "ML Engineer" },
    { name: "Alex Wang", team: "ML Engineer" },
] as const;

export const projects = [
    {
        name: "Mean Reversion",
        description:
            "Using fluctuations in the price of a stock to generate profits over time.",
        image: mean,
        href: "",
    },
    {
        name: "Sentiment Analysis",
        description:
            "Using fluctuations in the price of a stock to generate profits over time.",
        image: sentiment,
        href: "",
    },
    {
        name: "Crypto Arbitrage",
        description:
            "Analyzing opportunities for arbitrage across various exchanges.",
        image: crypto,
        href: "",
    },
    {
        name: "Correlation Trading",
        description:
            "Analyzing lagged correlations and statistical trading signals between stock pairs.",
        image: correlation,
        href: "/correlation-trading",
    },
    {
        name: "LLM Research",
        description:
            "In-house LLM to assist quant devs with training models, research, etc.",
        image: llm,
        href: "",
    },
    {
        name: "Backtesting Platform",
        description:
            "A way to test our models on the market and assess performance.",
        image: backtesting,
        href: "",
    },
    {
        name: "ML Platform",
        description:
            "A place for devs to securely utilize hardware to train models for free!",
        image: ml,
        href: "",
    },
] as const;
