"use client";
import React, { useEffect, useState } from "react";

const navLinks = [
    { name: "About", href: "/#about" },
    { name: "Projects", href: "/#projects" },
    { name: "Team", href: "/#team" },
    { name: "Research", href: "/research" },
    // { name: "Contact", href: "#contact" },
];

const Navbar = (props: { defaultPage: number }) => {
    const [visibleKey, setVisibleKey] = useState(props.defaultPage);

    const onClick = (item: any, key: any) => {
        setVisibleKey(key);
    };

    useEffect(() => {
        const handleScroll = () => {
            let scrollPosition = window.scrollY;
            const sections = document.querySelectorAll("section");

            if (sections[0].offsetTop > scrollPosition) setVisibleKey(-1);

            sections.forEach((section, index) => {
                if (
                    section.offsetTop <= scrollPosition + 100 &&
                    section.offsetTop + section.offsetHeight >
                        scrollPosition + 100
                ) {
                    setVisibleKey(index);
                }
            });
        };

        const sections = document.querySelectorAll("section");
        if (sections.length > 0) {
            window.addEventListener("scroll", handleScroll);
        }
    }, [visibleKey]);

    return (
        <div>
            <div className="rounded-xl bg-black/10 backdrop-blur-md backdrop-brightness-75 border border-1 border-[#333333] hover:border-[#56461a] hover:bg-black/50 transition ease-in-out duration-200">
                <ul className="flex gap-1 px-1 py-1">
                    {navLinks.map((item, key) => (
                        <a href={item.href} onClick={() => onClick(item, key)}>
                            <li
                                key={item.name}
                                className={`${
                                    key === visibleKey ? "bg-[#333333]" : ""
                                } px-6 py-2 rounded-lg text-neutral-50 hover:bg-[#56461a]/60 transition ease-in-out duration-200`}
                            >
                                {item.name}
                            </li>
                        </a>
                    ))}
                </ul>
            </div>
        </div>
    );
};

export default Navbar;
