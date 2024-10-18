import { promises as fs } from "fs";
import yaml from "js-yaml";
import path from "path";

import Slide from "@/components/slide";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
} from "@/components/ui/carousel";

// Async function to read and parse the YAML file
async function getSlideData() {
  const filePath = path.join(process.cwd(), "src/data/01_Intro/manifest.yml");
  const fileContents = await fs.readFile(filePath, "utf8");
  return yaml.load(fileContents) as Array<{
    title: string;
    subtitle: string;
    content: string | string[];
    image: string;
    imagePosition: "left" | "right";
  }>;
}

export default async function Home() {
  const slides = await getSlideData();

  return (
    <div className="w-full h-full">
      <Carousel className="w-full h-full ml-0">
        <CarouselContent className="w-full h-full p-0 ml-0">
          {slides.map((slide, index) => (
            <CarouselItem key={index} className="w-full h-full p-0">
              <Slide item={slide} index={index} />
            </CarouselItem>
          ))}
        </CarouselContent>
      </Carousel>
    </div>
  );
}
