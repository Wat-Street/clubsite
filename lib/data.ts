//pfps
import jaimil from "@/assets/images/jaimil.jpg";
import jai from "@/assets/images/jai.jpg";
import joseph from "@/assets/images/joseph.jpg";
import ishaan from "@/assets/images/ishaan.jpg";
import akshar from "@/assets/images/akshar.jpg";
import krish from "@/assets/images/krish.jpg";
//projgraphics
import mean from "@/assets/graphics/Mean Reversion.svg";
import sentiment from "@/assets/graphics/Sentiment Analysis.svg";
import crypto from "@/assets/graphics/Crypto Arbitrage.svg";
import llm from "@/assets/graphics/LLM.svg";
import backtesting from "@/assets/graphics/backtesting.png";
import ml from "@/assets/graphics/ml.svg";

export const execs = [
    {
        name: "Jaimil Dalwadi",
        role: "President + Co-Founder, Lead Dev",
        image: jaimil,
        alt: "Placeholder",
    },
    {
        name: "Joseph Ma",
        role: "VP of Tech + Finance",
        image: joseph,
        alt: "Placeholder",
    },
] as const;

export const leads = [
    {
        name: "Krish Modi",
        role: "VP Logistics, Machine Learning Lead",
        image: krish,
        alt: "Placeholder",
    },

    {
        name: "Ishaan Dey",
        role: "VP Operations, Frontend Lead",
        image: ishaan,
        alt: "Placeholder",
    },
    {
        name: "Akshar Barot",
        role: "VP Marketing, Frontend Lead",
        image: akshar,
        alt: "Placeholder",
    },
] as const;

export const team = [
    { name: "Jay Patel", team: "Backend" },
    { name: "Ryan Hu", team: "Backend" },
    { name: "Anthony Pirvuti", team: "Backend" },
    { name: "Arshvir Chaudhary", team: "Backend" },
    { name: "Jeffery Zhao", team: "Backend" },
    { name: "Shaheer Hassan", team: "Backend" },
    { name: "BK", team: "Backend" },
    { name: "Emma Shi", team: "Backend" },
    { name: "Krish Patel", team: "Backend" },
    { name: "Naman Biyani", team: "Backend" },
    { name: "Tanmay Shah", team: "Backend" },
    { name: "Krish Chopra", team: "Backend" },

    { name: "Sunnie Kapar", team: "Frontend" },
    { name: "Tian Yao", team: "Frontend" },
    { name: "Aurora Shi", team: "Frontend" },
    { name: "Jordan Kok", team: "Frontend" },
    { name: "Brian Zhang", team: "Frontend" },
    { name: "Rafael", team: "Frontend" },

    { name: "Alekszandr Martin Olah", team: "Quant" },
    { name: "Richard Fan", team: "Quant" },
    { name: "Jacob Yan", team: "Quant" },
    { name: "Suraj Sivaraja", team: "Quant" },
    { name: "Denys Inhul", team: "Quant" },
    { name: "Owen Zhang", team: "Quant" },
    { name: "Rebecca Xu", team: "Quant" },
    { name: "Gurik Mangat", team: "Quant" },
    { name: "Kamakshi Sarva", team: "Quant" },
    { name: "Rehan Anjum", team: "Quant" },
    { name: "Reshi Adavan", team: "Quant" },
    { name: "Sheldon Lewis", team: "Quant" },
    { name: "Sourish Das", team: "Quant" },
    { name: "Wilson", team: "Quant" },
    { name: "Mustafa", team: "Quant" },
    { name: "Hanz Po", team: "Quant" },
    { name: "Bryan Deng", team: "Quant" },
    { name: "Manas", team: "Quant" },
    { name: "Madhav", team: "Quant" },
    { name: "Darsh Shah", team: "Quant" },
    { name: "Aly Shariff", team: "Quant" },
    { name: "Vaishvi", team: "Quant" },

    { name: "Ronnie Huang", team: "Marketing" },
    { name: "Shawn Xiao", team: "Marketing" },
] as const;

export const projects = [
    {
        name: "Mean Reversion",
        description:
            "Using fluctuations in the price of a stock to generate profits over time.",
        image: mean,
    },
    {
        name: "Sentiment Analysis",
        description:
            "Using fluctuations in the price of a stock to generate profits over time.",
        image: sentiment,
    },
    {
        name: "Crypto Arbitrage",
        description:
            "Analyzing opportunities for arbitrage across various exchanges.",
        image: crypto,
    },
    {
        name: "LLM Research",
        description:
            "In-house LLM to assist quant devs with training models, research, etc.",
        image: llm,
    },
    {
        name: "Backtesting Platform",
        description:
            "A way to test our models on the market and assess performance.",
        image: backtesting,
    },
    {
        name: "ML Platform",
        description:
            "A place for devs to securely utilize hardware to train models for free!",
        image: ml,
    },
] as const;
