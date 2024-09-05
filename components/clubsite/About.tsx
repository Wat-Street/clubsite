// import Paragraph from "@/components/clubsite/Paragraph";
import Word from "@/components/clubsite/Word";

const paragraph =
    "Wat Street is a design team at the University of Waterloo striving to provide a comprehensive education in financial investment strategies and algorithm development. Our goal is to create a space where students can learn the fundamentals of quantitative analysis and how to apply them in the real world.";
const About = () => {
    return (
        <div className="sm:my-auto">
            {/* <div className="text-5xl font-bold mb-5 relative text-white/30">
                Who we are
                <div className="absolute top-0 left-0 text-white">
                    <Word paragraph={"Who we are"} end={"start 0.8"} />
                </div>
            </div> */}
            <div className="relative">
                {/* <Paragraph paragraph={paragraph} /> */}
                <div className="text-3xl sm:text-4xl text-white/30 font-semibold text-wrap">
                    {paragraph}
                </div>
                <div className=" font-semibold text-neutral-50">
                    <div className="absolute top-0 text-4xl left-0 invisible sm:visible">
                        <Word paragraph={paragraph} end={"start 0.36"} />
                    </div>
                    <div className="absolute top-0 left-0 visible sm:invisible text-3xl">
                        <Word paragraph={paragraph} end={"start 0.21"} />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default About;
