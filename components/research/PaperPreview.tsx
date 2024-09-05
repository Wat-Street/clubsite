import React from "react";

const PaperPreview = (props: {
    title: string;
    abstract: string;
    slug: string;
    author: string;
    pdfLink: string;
    githubLink: string;
    tags: string[];
}) => {
    return (
        <div>
            {/* this is for desktop view */}
            <div className="hidden md:block">
                <div className="md:h-72 w-full rounded-md p-4 border border-1 border-[#2c2d2d] relative group/card hover:bg-[#ffbb0f]/5 hover:border-[#ffbb0f]/25 transition ease-in-out duration-300">
                    <div className="text-pretty">
                        <div className="text-xl font-bold text-neutral-50">
                            {props.title}
                        </div>
                    </div>
                    <div className="mt-2 text-sm line-clamp-3 text-neutral-200">
                        {props.abstract}
                    </div>
                    <div className="absolute bottom-0 pb-4 -ml-4 px-4 w-full">
                        <div className="text-sm text-neutral-200 font-semibold mb-2">
                            {props.author}
                        </div>
                        <div className="flex flex-wrap gap-x-2 gap-y-1">
                            {props.tags.map((tag, key) => {
                                return (
                                    <div
                                        key={key}
                                        className="px-2 py-1 bg-[#2c2d2d]/0 border border-[#2c2d2d] text-neutral-200 rounded-md text-xs font-semibold group-hover/card:border-[#ffbb0f]/20 transition ease-in-out duration-300"
                                    >
                                        {tag}
                                    </div>
                                );
                            })}
                        </div>
                        <div className="flex w-full mt-2">
                            <a
                                href={`/research/${props.slug}`}
                                className={
                                    props.githubLink
                                        ? `w-1/2 pr-1`
                                        : `w-full pr-1`
                                }
                            >
                                <div className="px-2 py-3 bg-[#2c2d2d] text-neutral-200 rounded-md text-sm group border border-[#2c2d2d]/0 group-hover/card:bg-[#ffbb0f]/15   transition ease-in-out duration-300 hover:border hover:border-[#ffbb0f]/25 text-center">
                                    Paper
                                    <span>
                                        <svg
                                            xmlns="http://www.w3.org/2000/svg"
                                            fill="currentColor"
                                            className="inline h-[14px] w-[14px] ml-2 -mt-1 group-hover:translate-x-1 group-hover:-translate-y-0.5 transition ease-in-out duration-300 group-hover:text-[#ffd978]"
                                            viewBox="0 0 16 16"
                                        >
                                            <path
                                                fillRule="evenodd"
                                                d="M8.636 3.5a.5.5 0 0 0-.5-.5H1.5A1.5 1.5 0 0 0 0 4.5v10A1.5 1.5 0 0 0 1.5 16h10a1.5 1.5 0 0 0 1.5-1.5V7.864a.5.5 0 0 0-1 0V14.5a.5.5 0 0 1-.5.5h-10a.5.5 0 0 1-.5-.5v-10a.5.5 0 0 1 .5-.5h6.636a.5.5 0 0 0 .5-.5"
                                            />
                                            <path
                                                fillRule="evenodd"
                                                d="M16 .5a.5.5 0 0 0-.5-.5h-5a.5.5 0 0 0 0 1h3.793L6.146 9.146a.5.5 0 1 0 .708.708L15 1.707V5.5a.5.5 0 0 0 1 0z"
                                            />
                                        </svg>
                                    </span>
                                </div>
                            </a>
                            {props.githubLink != "" && (
                                <a
                                    href={props.githubLink}
                                    target="_blank"
                                    rel="noreferrer noopener"
                                    className="w-1/2 pl-1"
                                >
                                    <div className="px-2 py-3 bg-[#2c2d2d] text-neutral-200 rounded-md text-sm group border border-[#2c2d2d]/0 group-hover/card:bg-[#ffbb0f]/15   transition ease-in-out duration-300 hover:border hover:border-[#ffbb0f]/25 text-center">
                                        Github
                                        <span>
                                            <svg
                                                xmlns="http://www.w3.org/2000/svg"
                                                fill="currentColor"
                                                className="inline h-[14px] w-[14px] ml-2 -mt-1 group-hover:translate-x-1 group-hover:-translate-y-0.5 transition ease-in-out duration-300 group-hover:text-[#ffd978]"
                                                viewBox="0 0 16 16"
                                            >
                                                <path
                                                    fillRule="evenodd"
                                                    d="M8.636 3.5a.5.5 0 0 0-.5-.5H1.5A1.5 1.5 0 0 0 0 4.5v10A1.5 1.5 0 0 0 1.5 16h10a1.5 1.5 0 0 0 1.5-1.5V7.864a.5.5 0 0 0-1 0V14.5a.5.5 0 0 1-.5.5h-10a.5.5 0 0 1-.5-.5v-10a.5.5 0 0 1 .5-.5h6.636a.5.5 0 0 0 .5-.5"
                                                />
                                                <path
                                                    fillRule="evenodd"
                                                    d="M16 .5a.5.5 0 0 0-.5-.5h-5a.5.5 0 0 0 0 1h3.793L6.146 9.146a.5.5 0 1 0 .708.708L15 1.707V5.5a.5.5 0 0 0 1 0z"
                                                />
                                            </svg>
                                        </span>
                                    </div>
                                </a>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* This is for mobile view */}
            <div className="md:hidden">
                <div className="h-72 md:h-[245px] w-full rounded-md p-4 border border-1 border-[#2c2d2d] relative group/card hover:bg-[#ffbb0f]/10 hover:border-[#ffbb0f]/25 transition ease-in-out duration-300">
                    <div className="text-pretty">
                        <div className="text-xl font-bold text-neutral-50">
                            {props.title}
                        </div>
                    </div>
                    <div className="mt-2 text-sm line-clamp-3 text-neutral-200">
                        {props.abstract}
                    </div>
                    <div className="absolute bottom-0 pb-4 -ml-4 px-4 w-full">
                        <div className="text-sm text-neutral-200 font-semibold mb-2">
                            {props.author}
                        </div>
                        <div className="flex flex-wrap gap-x-2 gap-y-1">
                            {props.tags.map((tag, key) => {
                                return (
                                    <div
                                        key={key}
                                        className="px-2 py-1 bg-[#2c2d2d]/0 border border-[#2c2d2d] text-neutral-200 rounded-md text-xs font-semibold group-hover/card:border-[#ffbb0f]/20 transition ease-in-out duration-300"
                                    >
                                        {tag}
                                    </div>
                                );
                            })}
                        </div>
                        <div className="flex w-full mt-2">
                            <a
                                href={`/researchPapers/${props.slug}.pdf`}
                                className={
                                    props.githubLink
                                        ? `w-1/2 pr-1`
                                        : `w-full pr-1`
                                }
                            >
                                <div className="px-2 py-3 bg-[#2c2d2d] text-neutral-200 rounded-md text-sm group border border-[#2c2d2d]/0 group-hover/card:bg-[#ffbb0f]/15   transition ease-in-out duration-300 hover:border hover:border-[#ffbb0f]/25 text-center">
                                    Paper
                                    <span>
                                        <svg
                                            xmlns="http://www.w3.org/2000/svg"
                                            fill="currentColor"
                                            className="inline h-[14px] w-[14px] ml-2 -mt-1 group-hover:translate-x-1 group-hover:-translate-y-0.5 transition ease-in-out duration-300 group-hover:text-[#ffd978]"
                                            viewBox="0 0 16 16"
                                        >
                                            <path
                                                fillRule="evenodd"
                                                d="M8.636 3.5a.5.5 0 0 0-.5-.5H1.5A1.5 1.5 0 0 0 0 4.5v10A1.5 1.5 0 0 0 1.5 16h10a1.5 1.5 0 0 0 1.5-1.5V7.864a.5.5 0 0 0-1 0V14.5a.5.5 0 0 1-.5.5h-10a.5.5 0 0 1-.5-.5v-10a.5.5 0 0 1 .5-.5h6.636a.5.5 0 0 0 .5-.5"
                                            />
                                            <path
                                                fillRule="evenodd"
                                                d="M16 .5a.5.5 0 0 0-.5-.5h-5a.5.5 0 0 0 0 1h3.793L6.146 9.146a.5.5 0 1 0 .708.708L15 1.707V5.5a.5.5 0 0 0 1 0z"
                                            />
                                        </svg>
                                    </span>
                                </div>
                            </a>
                            {props.githubLink != "" && (
                                <a
                                    href={props.githubLink}
                                    target="_blank"
                                    rel="noreferrer noopener"
                                    className="w-1/2 pl-1"
                                >
                                    <div className="px-2 py-3 bg-[#2c2d2d] text-neutral-200 rounded-md text-sm group group-hover/card:bg-[#ffbb0f]/15 transition ease-in-out duration-300 hover:ring-[1.5px] hover:ring-[#ffbb0f]/25 text-center">
                                        Github
                                        <span>
                                            <svg
                                                xmlns="http://www.w3.org/2000/svg"
                                                fill="currentColor"
                                                className="inline h-[14px] w-[14px] ml-2 -mt-1 group-hover:translate-x-1 group-hover:-translate-y-0.5 transition ease-in-out duration-300 group-hover:text-[#ffd978]"
                                                viewBox="0 0 16 16"
                                            >
                                                <path
                                                    fillRule="evenodd"
                                                    d="M8.636 3.5a.5.5 0 0 0-.5-.5H1.5A1.5 1.5 0 0 0 0 4.5v10A1.5 1.5 0 0 0 1.5 16h10a1.5 1.5 0 0 0 1.5-1.5V7.864a.5.5 0 0 0-1 0V14.5a.5.5 0 0 1-.5.5h-10a.5.5 0 0 1-.5-.5v-10a.5.5 0 0 1 .5-.5h6.636a.5.5 0 0 0 .5-.5"
                                                />
                                                <path
                                                    fillRule="evenodd"
                                                    d="M16 .5a.5.5 0 0 0-.5-.5h-5a.5.5 0 0 0 0 1h3.793L6.146 9.146a.5.5 0 1 0 .708.708L15 1.707V5.5a.5.5 0 0 0 1 0z"
                                                />
                                            </svg>
                                        </span>
                                    </div>
                                </a>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PaperPreview;
