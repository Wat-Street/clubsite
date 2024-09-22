import Header from "@/components/clubsite/Header";
import Landing from "@/components/clubsite/Landing";
import About from "@/components/clubsite/About";
import Projects from "@/components/clubsite/Projects";
import Team from "@/components/clubsite/Team";
import Footer from "@/components/clubsite/Footer";
import MousePos from "@/components/clubsite/MousePos";

export default function HomePage() {
  return (
    <main className="mx-6 sm:mx-0">
      <Header defaultPage={0} />
      <div className="max-w-4xl mx-auto">
        <div className="h-[calc(100vh-80px)]">
          <Landing />
        </div>
        <section
          id="about"
          className="section sm:-mt-16 flex flex-col sm:h-screen"
        >
          <About />
        </section>
      </div>
      <div className="max-w-5xl mx-auto">
        <section
          id="projects"
          className="section mt-20 sm:-mt-[150px] flex flex-col sm:h-screen"
        >
          <Projects />
        </section>
      </div>
      <div className="max-w-5xl mx-auto">
        <section
          id="team"
          className="section mt-20 sm:-mt-20 sm:scroll-m-[40px]"
        >
          <Team />
        </section>
      </div>
      <MousePos />

      <Footer />
    </main>
  );
}
