"use client";
import {
    Carousel,
    CarouselContent,
    CarouselItem,
    CarouselNext,
    CarouselPrevious,
} from "@/components/clubsite/Carousel";
import Image from "next/image";

import { projects } from "@/lib/data";

const Projects = () => {
    return (
        <div className="my-auto projCards">
            <div className="sm:hidden text-4xl font-bold mb-4 text-neutral-50">
                Projects
            </div>
            {/* Mobile View */}
            <div className="sm:hidden flex flex-col gap-4">
                {projects.map((project) => (
                    <div className="projCard w-full h-96 rounded-lg bg-[#333333] overflow-hidden">
                        <div className="projCardBorder"></div>
                        <div className="projCardContent w-[calc(100%-2px)] h-[calc(100%-2px)] m-[1px] bg-black rounded-lg relative overflow-hidden">
                            <Image
                                src={project.image}
                                alt={project.name}
                                className="px-2 mt-4 sm:mt-10 w-max h-max"
                            />
                            <div className="mx-8 mb-6 flex flex-col gap-1 absolute bottom-0">
                                <div className="text-2xl font-semibold text-neutral-50">
                                    {project.name}
                                </div>
                                <div className="text-neutral-200">
                                    {project.description}
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Desktop View */}
            <div className="hidden sm:block">
                <Carousel
                    opts={{
                        align: "start",
                    }}
                    className="w-full max-w-none"
                >
                    <CarouselContent>
                        {projects.map((project) => (
                            <CarouselItem className="sm:basis-1/3">
                                <div className="projCard w-full h-96 rounded-lg bg-[#333333] overflow-hidden">
                                    <div className="projCardBorder"></div>
                                    <div className="projCardContent w-[calc(100%-2px)] h-[calc(100%-2px)] m-[1px] bg-black rounded-lg relative overflow-hidden">
                                        <Image
                                            src={project.image}
                                            alt={project.name}
                                            className="px-2 mt-10 w-max h-max"
                                        />
                                        <div className="mx-8 mb-6 flex flex-col gap-1 absolute bottom-0">
                                            <div className="text-2xl font-semibold text-neutral-50">
                                                {project.name}
                                            </div>
                                            <div className="text-neutral-200">
                                                {project.description}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </CarouselItem>
                        ))}
                    </CarouselContent>
                    <CarouselPrevious />
                    <CarouselNext />
                </Carousel>
            </div>
            <div>
                <a
                    href="/research"
                    className="inline-flex items-center font-semibold bold leading-tight text-neutral-200 group mt-6"
                    rel="noreferrer noopener"
                >
                    <span className="text-xl border-b-[1px] border-transparent transition group-hover:border-[#c28b00]/60">
                        Click here to see our research
                    </span>
                    <span className="ml-4 group-hover:translate-x-2 group-hover:text-[#c28b00]/60 ease-in-out duration-200">
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            fill="currentColor"
                            className="h-5 w-5"
                            viewBox="0 0 16 16"
                        >
                            <path
                                fillRule="evenodd"
                                d="M1 8a.5.5 0 0 1 .5-.5h11.793l-3.147-3.146a.5.5 0 0 1 .708-.708l4 4a.5.5 0 0 1 0 .708l-4 4a.5.5 0 0 1-.708-.708L13.293 8.5H1.5A.5.5 0 0 1 1 8"
                            />
                        </svg>
                    </span>
                </a>
            </div>
        </div>
    );
};

export default Projects;
