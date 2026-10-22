import React from 'react';

export default function LoadingSpinner({ size = 40 }: { size?: number }) {
  const style: React.CSSProperties = {
    width: size,
    height: size,
    border: `${size / 8}px solid #f3f3f3`,
    borderTop: `${size / 8}px solid #3498db`,
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
    margin: 'auto',
  };
  return <div style={style} />;
}

/* Add this CSS to src/styles/global.css or equivalent */
/* @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } } */
