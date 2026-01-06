import React from 'react';

const AppealLetter = ({ onGenerate, isGenerating }) => {
    const handleDownload = (blob, filename) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    };

    return (
        <div className="appeal-letter-section">
            <h3 style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>
                📄 Appeal Letter Generation
            </h3>

            <p style={{ marginBottom: '1.5rem', color: 'var(--text-secondary)' }}>
                Generate a professional appeal letter based on your documents and the denial reason.
            </p>

            <button
                className="btn btn-primary download-btn"
                onClick={onGenerate}
                disabled={isGenerating}
            >
                {isGenerating ? (
                    <>
                        <div className="spinner" style={{ width: '20px', height: '20px' }}></div>
                        Generating...
                    </>
                ) : (
                    <>
                        📥 Generate Appeal Letter
                    </>
                )}
            </button>

            <div style={{ marginTop: '1rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                The appeal letter will include medical evidence, procedure justification, and policy references.
            </div>
        </div>
    );
};

export default AppealLetter;
