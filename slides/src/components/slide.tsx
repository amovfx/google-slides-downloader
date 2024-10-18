"use client";
import Image from "next/image";
import React from "react";

import { getImagePath } from "@/actions/slide";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface SlideProps {
  item: {
    title?: string;
    subtitle?: string;
    content?: string | string[];
    imagePosition?: "left" | "right";
  };
  index: number;
}

// Moved and modified getImagePath function

const Slide: React.FC<SlideProps> = ({ item, index }) => {
  const {
    title = "Saga",
    subtitle = "Default Subtitle",
    content = "Default Content",
    imagePosition = "left",
  } = item;

  const image = await getImagePath(index);

  const [spacebarPressCount, setSpacebarPressCount] = useState(0);

  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (event.code === "Space") {
        setSpacebarPressCount((prevCount) => {
          const newCount = prevCount + 1;
          if (newCount === 1) {
            console.log("start");
          } else if (newCount === 2) {
            console.log("end");
            return 0; // Reset the count after the second press
          }
          return newCount;
        });
      }
    };

    window.addEventListener("keydown", handleKeyPress);

    return () => {
      window.removeEventListener("keydown", handleKeyPress);
    };
  }, []);

  return (
    <div className="flex h-screen w-full items-center p-0 font-futura">
      <div
        className={`w-3/5 h-full v-full relative ${
          imagePosition === "left" ? "order-first" : "order-last"
        }`}
      >
        <Image
          src={image}
          alt={title}
          layout="fill"
          objectFit="cover"
          objectPosition="center"
        />
      </div>
      <Card
        className={`w-2/5 flex flex-col justify-center shadow-none mx-40 border-none ${
          imagePosition === "left" ? "order-last" : "order-first"
        }`}
      >
        <CardHeader>
          <CardTitle className="text-4xl font-bold mb-4 font-futura">
            {title}
          </CardTitle>
          <h3 className="text-2xl text-gray-600 mb-6 font-futura">
            {subtitle}
          </h3>
        </CardHeader>
        <CardContent className="text-lg font-futura">
          {Array.isArray(content) ? (
            <ul className="list-disc list-inside">
              {content.map((bullet, index) => (
                <li key={index}>{bullet}</li>
              ))}
            </ul>
          ) : (
            <p>{content}</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Slide;
