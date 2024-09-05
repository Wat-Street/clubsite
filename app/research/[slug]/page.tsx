import React from "react";

import { researchData } from "@/lib/researchData";

const getContent = (slug: string) => {
    for (let i in researchData) {
        if (researchData[i].slug === slug) {
            return researchData[i];
        }
    }
};

export const dynamicParams = false;

export const generateStaticParams = async () => {
    return researchData.map((paper) => ({
        slug: paper.slug,
    }));
};

const page = ({ params }: { params: { slug: string } }) => {
    const slug = params.slug;
    const paper = getContent(slug);
    return (
        <div className="max-w-5xl mx-auto px-6">
            <div className="relative">
                <div className="absolute -left-24 pt-10">
                    <a href="/research" className="hidden lg:block fixed group">
                        <div className="ml-2 group-hover:-translate-x-2 ease-in-out duration-300 group">
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                fill="currentColor"
                                className="h-6 w-6"
                                viewBox="0 0 16 16"
                            >
                                <path
                                    fillRule="evenodd"
                                    d="M15 8a.5.5 0 0 0-.5-.5H2.707l3.147-3.146a.5.5 0 1 0-.708-.708l-4 4a.5.5 0 0 0 0 .708l4 4a.5.5 0 0 0 .708-.708L2.707 8.5H14.5A.5.5 0 0 0 15 8"
                                />
                            </svg>
                        </div>
                        <p className="opacity-0 group-hover:opacity-100 group-hover:block text-[12px] text-neutral-200 group duration-300">
                            Go back
                        </p>
                    </a>
                </div>
            </div>
            <div className="w-full h-[100vh] pb-2">
                <object
                    data={paper?.pdfLink}
                    type="application/pdf"
                    width="100%"
                    height="100%"
                >
                    <div className="pt-10">
                        PDF could not be loaded.{" "}
                        <a
                            href={paper?.pdfLink}
                            className="inline-flex items-center font-bold leading-tight text-slate-200 group"
                            target="_blank"
                            rel="noreferrer noopener"
                        >
                            Click here to view the paper.
                        </a>
                    </div>
                </object>
            </div>
        </div>
    );
};

// export async function generateMetadata({
//     params,
// }: {
//     params: any;
// }): Promise<Metadata> {
//     const slug = params.slug;
//     const post = getPostContent(slug);
//     return {
//         title: `${post.data.title} | Akshar Barot`,
//         description: post.data.subtitle,
//         keywords: post.data.keywords,
//     };
// }

export default page;
