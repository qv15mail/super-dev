'use client';

import { useEffect, useState } from 'react';
import { DEFAULT_STAR_COUNT, loadGithubStars } from '@/lib/github';

export function useGithubStars() {
  const [stars, setStars] = useState(DEFAULT_STAR_COUNT);

  useEffect(() => {
    let active = true;

    loadGithubStars()
      .then((value) => {
        if (active) {
          setStars(value);
        }
      })
      .catch(() => {
        if (active) {
          setStars(DEFAULT_STAR_COUNT);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  return stars;
}
