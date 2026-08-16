import { useEffect, useRef, useState } from 'react';
export function FadeIn({ children, className = '', delay = 0 }) {
    const ref = useRef(null);
    const [visible, setVisible] = useState(false);
    useEffect(() => {
        const el = ref.current;
        if (!el)
            return;
        const observer = new IntersectionObserver(([entry]) => { if (entry.isIntersecting)
            setVisible(true); }, { threshold: 0.1, rootMargin: '0px 0px -60px 0px' });
        observer.observe(el);
        return () => observer.disconnect();
    }, []);
    return (<div ref={ref} className={`fade-in ${visible ? 'visible' : ''} ${className}`} style={{ transitionDelay: `${delay}ms` }}>
      {children}
    </div>);
}
