import React from 'react';

const DenialExplanation = ({ explanation }) => {
    if (!explanation) return null;

    return (
        <div className="denial-explanation">
            <h3 style={{ marginBottom: '1.5rem', color: 'var(--text-secondary)' }}>
                📋 Denial Explanation
            </h3>

            {explanation.simple_explanation && (
                <div className="requirement-item" style={{ borderLeftColor: 'var(--primary-blue)' }}>
                    <strong>Simple Explanation</strong>
                    <p style={{ marginTop: '0.5rem' }}>{explanation.simple_explanation}</p>
                </div>
            )}

            {explanation.denial_code_meaning && (
                <div className="requirement-item" style={{ borderLeftColor: 'var(--warning-yellow)' }}>
                    <strong>Denial Code Meaning</strong>
                    <p style={{ marginTop: '0.5rem' }}>{explanation.denial_code_meaning}</p>
                </div>
            )}

            {explanation.insurer_reasoning && (
                <div className="requirement-item" style={{ borderLeftColor: 'var(--accent-purple)' }}>
                    <strong>Insurer's Reasoning</strong>
                    <p style={{ marginTop: '0.5rem' }}>{explanation.insurer_reasoning}</p>
                </div>
            )}

            {explanation.missing_documentation_identified &&
                explanation.missing_documentation_identified.length > 0 && (
                    <div className="missing-requirements">
                        <h4 style={{ marginTop: '1rem', marginBottom: '0.75rem', color: 'var(--danger-red)' }}>
                            Missing Documentation
                        </h4>
                        {explanation.missing_documentation_identified.map((item, index) => (
                            <div key={index} className="requirement-item">
                                {item}
                            </div>
                        ))}
                    </div>
                )}

            {explanation.next_steps && (
                <div className="requirement-item" style={{ borderLeftColor: 'var(--success-green)' }}>
                    <strong>Next Steps</strong>
                    <p style={{ marginTop: '0.5rem' }}>{explanation.next_steps}</p>
                </div>
            )}
        </div>
    );
};

export default DenialExplanation;
