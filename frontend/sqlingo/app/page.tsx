'use client';

import { Button } from '@/components/ui/button';
import DotGrid from '../components/DotGrid';
import TextType from '../components/TextType';
import { Press_Start_2P } from 'next/font/google';
import { ArrowRight } from 'lucide-react';
import Link from 'next/link';
import { useState, useEffect } from 'react';

const pressStart2P = Press_Start_2P({
  weight: '400',
  subsets: ['latin']
});

export default function Home() {
  const [showButton, setShowButton] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowButton(true);
    }, 2100);

    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="fixed inset-0 overflow-hidden bg-black">
      <div className="absolute -inset-[10%] w-[120%] h-[130%]">
        <DotGrid
          dotSize={6}
          gap={12}
          baseColor="#271e37"
          activeColor="#5227ff"
          proximity={120}
          shockRadius={150}
          shockStrength={20}
          resistance={750}
          returnDuration={1.5}
          className="w-full h-full"
        />
      </div>
      <div>
        <a
          href=""
          target="_blank"
          rel="noopener noreferrer"
          className="absolute top-8 right-8 z-20 p-3 rounded-full text-white hover:text-gray-300 transition-colors duration-300"
        >
          <svg className="w-10 h-10" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
          </svg>
        </a>
        <div className="pointer-events-none fixed inset-0 z-10 flex flex-col items-center justify-center gap-4 p-4 -translate-y-[3%]">
          <h1 className={`${pressStart2P.className} text-4xl font-normal text-white/80 drop-shadow-[0_0_40px_rgba(0,0,0,0.9)] md:text-8xl`}
              style={{
                textShadow: '0 0 40px rgba(0,0,0,0.9), 0 0 80px rgba(0,0,0,0.8), 0 0 120px rgba(0,0,0,0.7)'
              }}>
            <TextType 
              as="span"
              text={["SQLingo"]}
              typingSpeed={100}
              pauseDuration={0}
              showCursor={false}
              loop={false}
            />
          </h1>
          <p className={`${pressStart2P.className} text-xs md:text-lg text-white/60 text-center`}
             style={{
               textShadow: '0 0 20px rgba(0,0,0,0.8)'
             }}>
            <TextType 
              as="span"
              text={["A Text-to-SQL Query Engine"]}
              typingSpeed={75}
              pauseDuration={0}
              showCursor={true}
              cursorCharacter={'_'}
              loop={false}
            />
          </p>
          <div className="pointer-events-auto mt-8">
            <Link href="/playground">
              <Button
                size="lg"
                variant="outline"
                className={`${pressStart2P.className} rounded-full px-8 transition-all duration-1000 ${
                  showButton ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
                }`}
              >
                Try Now <ArrowRight className="ml-2 w-4 h-4" />
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}