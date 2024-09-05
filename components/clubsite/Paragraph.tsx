"use client";
import { motion, useScroll, useTransform } from "framer-motion";
import React, { useRef } from "react";

const Paragraph = ({ paragraph }: { paragraph: string }) => {
    const container = useRef(null);
    const { scrollYProgress } = useScroll({
        target: container,
        offset: ["start 0.9", "start 0.2"],
    });

    const opacity = useTransform(scrollYProgress, [0, 1], [0, 1]);

    return (
        <motion.p ref={container} style={{ opacity }} className="text-4xl">
            {paragraph}
        </motion.p>
    );
};

export default Paragraph;
