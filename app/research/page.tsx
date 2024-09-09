"use client";

import { useState, useEffect } from "react";

import Header from "@/components/clubsite/Header";
import Footer from "@/components/clubsite/Footer";
import MousePos from "@/components/clubsite/MousePos";
import PaperPreview from "@/components/research/PaperPreview";

import { ScrollArea } from "@/components/ui/scroll-area";

import { researchData, tags } from "@/lib/researchData";

export default function HomePage() {
    const [allActive, setAllActive] = useState(true);
    const [activeTags, setActiveTags] = useState<string[]>([]);
    const [activeTag, setActiveTag] = useState("");

    // const handleTagClick = (tagName: string) => {
    //     if (activeTags.includes(tagName)) {
    //         setActiveTags(activeTags.filter((item) => item !== tagName));
    //     } else {
    //         setActiveTags([...activeTags, tagName]);
    //     }
    // };
    const handleTagClick = (tagName: string) => {
        if (activeTag === tagName) {
            setActiveTag("");
        } else {
            setActiveTag(tagName);
        }
    };

    // useEffect(() => {
    //     if (activeTags.length > 0) {
    //         setAllActive(false);
    //     } else {
    //         setAllActive(true);
    //     }
    // }, [activeTags]);
    useEffect(() => {
        if (activeTag === "") {
            setAllActive(true);
        } else {
            setAllActive(false);
        }
    }, [activeTag]);

    return (
        <main className="mx-6 sm:mx-0 h-screen">
            <Header defaultPage={3} />
            <div className="pt-4 md:pt-8 pb-6 mx-6 min-h-[calc(100vh-80px)]">
                <div className="min-h-8 py-4 flex flex-wrap justify-center gap-1 text-sm text-neutral-50">
                    <button
                        onClick={() => {
                            setAllActive(true);
                            // setActiveTags([]);
                            setActiveTag("");
                        }}
                        className={`${allActive ? "bg-[#333333]" : ""}
                        px-4 py-2 border border-1 border-[#333333] rounded-2xl hover:bg-[#333333] transition ease-in-out duration-200`}
                    >
                        All
                    </button>
                    {tags.map((tag, key) => (
                        <button
                            onClick={() => handleTagClick(tag.name)}
                            className={`${
                                // activeTags.includes(tag.name)
                                activeTag === tag.name ? "bg-[#333333]/80" : ""
                            }
                                px-4 py-2 border border-1 border-[#333333] rounded-2xl hover:bg-[#333333] transition ease-in-out duration-200`}
                        >
                            {tag.name}
                        </button>
                    ))}
                </div>
                <ScrollArea className="h-[72vh]">
                    {/* <div className="grid grid-cols-1 md:grid-cols-4 gap-2"> */}
                    <div className="flex flex-row flex-wrap justify-center gap-2">
                        {researchData.map((paper, key) => {
                            if (
                                allActive ||
                                // paper.tags.some((tag) =>
                                //     activeTags.includes(tag)
                                // )
                                paper.tags.includes(activeTag)
                            ) {
                                return (
                                    <div className="w-full md:w-[calc(25%-(24px/4))]">
                                        <PaperPreview key={key} {...paper} />
                                    </div>
                                );
                            }
                        })}
                    </div>
                </ScrollArea>
            </div>
            <Footer />
        </main>
    );
}
