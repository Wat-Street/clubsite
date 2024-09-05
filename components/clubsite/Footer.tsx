import Image from "next/image";
import mef from "@/assets/logos/mef-grayscale.png";
import logo from "@/assets/logos/watstreet.png";
import Socials from "@/components/clubsite/Socials";

import { Linkedin, Mail } from "lucide-react";

const Footer = () => {
  return (
    <div>
      <div className="flex flex-wrap sm:flex-nowrap mt-16 sm:mt-20 min-h-20 sm:px-20 border-t border-neutral-800 pt-6 sm:py-6 justify-around sm:justify-between">
        <div className="w-1/2 sm:w-auto flex flex-col sm:mt-3">
          <div className="text-left text-neutral-300 text-sm">
            Sponsored by:
          </div>
          <Image
            src={mef}
            alt="logo"
            className="aspect-[500/258] w-36 sm:w-56 -ml-3 -mt-2 brightness-150"
          />
          <div>Funding for team PC and data subscriptions.</div>
        </div>
        <div className=" order-3 my-auto ">
          <Socials />
        </div>
        <div className="flex flex-col order-last mt-4 sm:order-2 sm:mt-0 mx-auto sm:absolute inset-x-0 -translate-y-3 -z-10">
          <Image
            src={logo}
            alt="logo"
            className="w-24 h-24 sm:w-32 sm:h-32 mx-auto drop-shadow-[0_0px_40px_rgba(251,228,159,0.7)]"
          />
          <div className="text-neutral-300 text-center text-sm">
            © 2024 Wat Street
          </div>
        </div>
      </div>
    </div>
  );
};

export default Footer;
