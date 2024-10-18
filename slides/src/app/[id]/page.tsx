import Slide from "@/components/slide";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
} from "@/components/ui/carousel";

import { getSlideData } from "./actions";

// Async function to read and parse the YAML file

export default async function SlidePage({
  params,
}: {
  params: { id: string };
}) {
  const slides = await getSlideData(params.id);

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
