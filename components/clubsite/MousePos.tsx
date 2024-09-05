"use client";
import { useEffect, useState } from "react";

const MousePos = () => {
    useEffect(() => {
        const handleMouseMoveMem = (e: MouseEvent) => {
            for (const card of document.querySelectorAll(".memberCard")) {
                if (!card) return;

                const rect = (card as HTMLElement).getBoundingClientRect();
                const newMousePos = {
                    x: e.clientX - rect.left,
                    y: e.clientY - rect.top,
                };
                (card as HTMLElement).style.setProperty(
                    "--mouse-x",
                    `${newMousePos.x}px`
                );
                (card as HTMLElement).style.setProperty(
                    "--mouse-y",
                    `${newMousePos.y}px`
                );
            }
        };

        const handleMouseMoveProj = (e: MouseEvent) => {
            for (const card of document.querySelectorAll(".projCard")) {
                if (!card) return;

                const rect = (card as HTMLElement).getBoundingClientRect();
                const newMousePos = {
                    x: e.clientX - rect.left,
                    y: e.clientY - rect.top,
                };
                (card as HTMLElement).style.setProperty(
                    "--mouse-x",
                    `${newMousePos.x}px`
                );
                (card as HTMLElement).style.setProperty(
                    "--mouse-y",
                    `${newMousePos.y}px`
                );
            }
        };

        const memberCards = document.querySelector(".memberCards");
        if (memberCards) {
            memberCards.addEventListener(
                "mousemove",
                handleMouseMoveMem as EventListenerOrEventListenerObject
            );
        }

        const projCards = document.querySelector(".projCards");
        if (projCards) {
            projCards.addEventListener(
                "mousemove",
                handleMouseMoveProj as EventListenerOrEventListenerObject
            );
        }
        return () => {
            if (memberCards) {
                memberCards.removeEventListener(
                    "mousemove",
                    handleMouseMoveMem as EventListenerOrEventListenerObject
                );
            }
            if (projCards) {
                projCards.removeEventListener(
                    "mousemove",
                    handleMouseMoveProj as EventListenerOrEventListenerObject
                );
            }
        };
    });

    return null;
};

export default MousePos;
