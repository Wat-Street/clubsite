"use client";
import * as React from "react";

const Sidebar = () => {
    const tags = [
        { name: "All" },
        { name: "Finance" },
        { name: "Machine Learning" },
        { name: "Other Stuff" },
        // { name: "Contact", href: "#contact" },
    ];

    const checkActive = (key: number) => {
        return active.includes(key);
    };

    const [active, setActive] = React.useState([0]);
    const onClick = (item: any, key: any) => {
        setActive([...active, key]);
    };

    return (
        <div>
            <div className="h-16 flex items-center justify-center gap-1 text-sm">
                {tags.map((tag, key) => (
                    <div className="px-5 py-3 border border-1 border-[#2c2d2d] rounded-md hover:bg-[#2c2d2d] transition ease-in-out duration-200">
                        {tag.name}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Sidebar;
