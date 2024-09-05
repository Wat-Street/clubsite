"use client";
import { motion, useScroll, useTransform } from "framer-motion";
import React, { useRef } from "react";

const Paragraph = ({ paragraph, end }: { paragraph: string; end: any }) => {
    const container = useRef(null);
    const { scrollYProgress } = useScroll({
        target: container,
        offset: ["start 0.9", end],
    });

    const words = paragraph.split(" ");

    return (
        <div
            ref={container}
            className="flex flex-wrap w-[100%] gap-x-[0.255em]"
        >
            {words.map((word, i) => {
                const start = i / words.length;
                const end = start + 1 / words.length;
                return (
                    <div className="">
                        <Word
                            key={i}
                            progress={scrollYProgress}
                            range={[start, end]}
                        >
                            {word}
                        </Word>
                    </div>
                );
            })}
        </div>
    );
};

const Word = ({
    children,
    progress,
    range,
}: {
    children: any;
    progress: any;
    range: any;
}) => {
    const opacity = useTransform(progress, range, [0, 1]);
    return (
        <span>
            <motion.span style={{ opacity: opacity }}>{children}</motion.span>
        </span>
    );
};

export default Paragraph;
